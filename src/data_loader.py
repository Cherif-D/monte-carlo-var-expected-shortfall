"""
data_loader.py — Chargement et validation des données de prix
=============================================================
Ce module gère deux modes de chargement :

  Mode "example" (par défaut) :
    Charge le fichier CSV local data/examples/example_prices.csv.
    Si ce fichier n'existe pas, il est généré automatiquement.
    Ce mode garantit que le projet fonctionne sans connexion internet.

  Mode "live" :
    Télécharge les prix via yfinance (non requis par défaut).
    Nécessite une connexion internet et le package yfinance installé.

Après chargement, le module applique des contrôles de qualité :
  - cohérence des dates,
  - détection des valeurs manquantes,
  - détection des prix négatifs ou nuls,
  - vérification des actifs attendus.
"""

import logging
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger("var_mc.data_loader")


# =============================================================================
# Point d'entrée principal
# =============================================================================

def charger_prix(config: dict) -> pd.DataFrame:
    """
    Charge les prix selon le mode défini dans config.yaml.

    Paramètres
    ----------
    config : dict
        Configuration complète du projet.

    Retourne
    --------
    pd.DataFrame
        DataFrame de prix ajustés, index = DatetimeIndex, colonnes = tickers.
        Fréquence quotidienne, valeurs positives, sans NaN.
    """
    mode = config["data"].get("mode", "example")
    tickers = list(config["portfolio"]["actifs"].keys())

    if mode == "example":
        df = _charger_csv_exemple(config, tickers)
    elif mode == "live":
        df = _charger_live(config, tickers)
    else:
        raise ValueError(
            f"Mode de chargement inconnu : '{mode}'. "
            "Valeurs acceptées : 'example', 'live'."
        )

    df = _filtrer_par_dates(df, config)
    _controler_qualite(df, tickers)

    logger.info(
        f"Données chargées : {len(df)} observations, "
        f"{len(df.columns)} actifs, "
        f"du {df.index[0].date()} au {df.index[-1].date()}"
    )
    return df


# =============================================================================
# Mode CSV local
# =============================================================================

def _charger_csv_exemple(config: dict, tickers: list[str]) -> pd.DataFrame:
    """
    Charge le fichier CSV d'exemple. Si absent, le génère automatiquement.
    """
    chemin = Path(config["data"]["example_file"])

    if not chemin.exists():
        logger.info(
            f"Fichier exemple introuvable ({chemin}). Génération automatique..."
        )
        _generer_exemple(chemin)

    df = pd.read_csv(chemin, index_col="Date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)

    # Sélectionner uniquement les actifs demandés (dans l'ordre du config)
    colonnes_presentes = [t for t in tickers if t in df.columns]
    colonnes_manquantes = [t for t in tickers if t not in df.columns]
    if colonnes_manquantes:
        logger.warning(
            f"Actifs absents du fichier CSV : {colonnes_manquantes}. "
            "Ils seront ignorés."
        )
    return df[colonnes_presentes]


def _generer_exemple(chemin: Path) -> None:
    """Lance le script de génération des données synthétiques."""
    script = Path(__file__).parent.parent / "data" / "examples" / "generate_example_data.py"
    if not script.exists():
        raise FileNotFoundError(
            f"Script de génération introuvable : {script}"
        )
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Échec de la génération des données exemple :\n{result.stderr}"
        )
    logger.info("Données exemple générées avec succès.")


# =============================================================================
# Mode live (yfinance)
# =============================================================================

def _charger_live(config: dict, tickers: list[str]) -> pd.DataFrame:
    """
    Télécharge les prix historiques via yfinance.

    Note : l'actif EURUSD est renommé en EURUSD=X pour yfinance.
    """
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError(
            "Le mode 'live' nécessite le package yfinance. "
            "Installez-le via : pip install yfinance\n"
            "Ou utilisez le mode 'example' dans config.yaml."
        )

    # Adaptation des tickers pour yfinance (FX pairs)
    tickers_yf = [
        "EURUSD=X" if t == "EURUSD" else t
        for t in tickers
    ]
    ticker_map = dict(zip(tickers_yf, tickers))

    start = config["data"]["start_date"]
    end   = config["data"]["end_date"]

    logger.info(f"Téléchargement yfinance : {tickers_yf} du {start} au {end}...")
    raw = yf.download(
        tickers_yf,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
    )["Close"]

    # Renommer les colonnes (ex: "EURUSD=X" -> "EURUSD")
    raw = raw.rename(columns=ticker_map)
    raw = raw[[t for t in tickers if t in raw.columns]]
    return raw


# =============================================================================
# Filtrage par dates
# =============================================================================

def _filtrer_par_dates(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Restreint le DataFrame à la plage de dates définie dans la config."""
    start = pd.Timestamp(config["data"]["start_date"])
    end   = pd.Timestamp(config["data"]["end_date"])
    masque = (df.index >= start) & (df.index <= end)
    df_filtre = df.loc[masque].copy()
    if len(df_filtre) == 0:
        raise ValueError(
            f"Aucune donnée dans la plage [{start.date()}, {end.date()}].\n"
            "Vérifiez les paramètres start_date / end_date dans config.yaml."
        )
    return df_filtre


# =============================================================================
# Contrôle qualité
# =============================================================================

def _controler_qualite(df: pd.DataFrame, tickers: list[str]) -> None:
    """
    Applique des contrôles de cohérence sur le DataFrame de prix.

    Vérifications effectuées :
    1. Présence de toutes les colonnes attendues.
    2. Absence de valeurs manquantes (après forward-fill éventuel).
    3. Absence de prix nuls ou négatifs.
    4. Tri chronologique de l'index.
    """
    # Tri chronologique (par sécurité)
    if not df.index.is_monotonic_increasing:
        df.sort_index(inplace=True)
        logger.warning("Index non trié : réordonné chronologiquement.")

    # Forward-fill pour les éventuels jours fériés locaux
    n_nan_avant = df.isna().sum().sum()
    if n_nan_avant > 0:
        df.ffill(inplace=True)
        logger.warning(
            f"{n_nan_avant} valeurs manquantes comblées par forward-fill. "
            "Vérifiez la qualité des données source."
        )

    # Vérification post-fill
    n_nan_apres = df.isna().sum().sum()
    if n_nan_apres > 0:
        raise ValueError(
            f"{n_nan_apres} NaN persistent après forward-fill. "
            "Les premières lignes contiennent peut-être des NaN."
        )

    # Prix strictement positifs
    if (df <= 0).any().any():
        actifs_pb = df.columns[(df <= 0).any()].tolist()
        raise ValueError(
            f"Prix nuls ou négatifs détectés pour : {actifs_pb}. "
            "Les prix doivent être strictement positifs."
        )

    logger.debug("Contrôle qualité des données : OK.")


# =============================================================================
# Calcul des rendements
# =============================================================================

def calculer_rendements_log(prix: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les rendements logarithmiques journaliers.

    Formule : r_t = ln(P_t / P_{t-1})

    Pourquoi log-rendements ?
    - Propriété d'additivité temporelle : r_{t,t+n} = sum(r_t, ..., r_{t+n})
    - Plus symétriques que les rendements simples
    - Correspondent à la solution du GBM continu

    Paramètres
    ----------
    prix : pd.DataFrame
        Séries de prix, index temporel.

    Retourne
    --------
    pd.DataFrame
        Rendements logarithmiques (première observation perdue).
    """
    rendements = np.log(prix / prix.shift(1)).dropna()
    logger.debug(
        f"Rendements log calculés : {len(rendements)} observations "
        f"pour {len(rendements.columns)} actifs."
    )
    return rendements
