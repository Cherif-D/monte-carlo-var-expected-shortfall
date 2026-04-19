"""
generate_example_data.py
========================
Script utilitaire pour générer des données de prix synthétiques réalistes.

Les données sont générées via un mouvement brownien géométrique (GBM) avec
corrélations calibrées sur des ordres de grandeur observés sur les marchés
financiers entre 2020 et 2023.

Ce script est exécuté automatiquement par data_loader.py si le fichier
example_prices.csv n'existe pas encore.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_correlated_gbm(
    n_days: int,
    tickers: list[str],
    mu_annuel: dict[str, float],
    sigma_annuel: dict[str, float],
    correlation_matrix: np.ndarray,
    prix_initiaux: dict[str, float],
    seed: int = 42,
    start_date: str = "2020-01-02",
) -> pd.DataFrame:
    """
    Génère des séries de prix via un mouvement brownien géométrique multivarié.

    Paramètres
    ----------
    n_days : int
        Nombre de jours de cotation à simuler.
    tickers : list[str]
        Noms des actifs.
    mu_annuel : dict
        Rendements annuels espérés par actif (ex: 0.07 pour 7%).
    sigma_annuel : dict
        Volatilités annuelles par actif (ex: 0.15 pour 15%).
    correlation_matrix : np.ndarray
        Matrice de corrélation (n_actifs x n_actifs), doit être définie positive.
    prix_initiaux : dict
        Prix de départ pour chaque actif.
    seed : int
        Graine aléatoire.
    start_date : str
        Date de début de la série.

    Retourne
    --------
    pd.DataFrame
        DataFrame avec dates en index et tickers en colonnes.
    """
    rng = np.random.default_rng(seed)
    n_actifs = len(tickers)
    dt = 1 / 252  # 1 jour ouvré / 252 jours ouvrés par an

    # Conversion des paramètres annuels en paramètres journaliers
    mu_j = np.array([mu_annuel[t] for t in tickers]) * dt
    sigma_j = np.array([sigma_annuel[t] for t in tickers]) * np.sqrt(dt)

    # Décomposition de Cholesky pour simuler des innovations corrélées
    # Si la matrice n'est pas définie positive, on la régularise légèrement
    try:
        L = np.linalg.cholesky(correlation_matrix)
    except np.linalg.LinAlgError:
        # Régularisation de Tikhonov pour garantir la définition positive
        eps = 1e-6
        corr_reg = correlation_matrix + eps * np.eye(n_actifs)
        L = np.linalg.cholesky(corr_reg)

    # Génération des innovations indépendantes (bruit blanc gaussien)
    Z = rng.standard_normal((n_days, n_actifs))
    # Corrélation des innovations : Z_corr = Z @ L^T
    Z_corr = Z @ L.T

    # Calcul des rendements journaliers via la formule exacte du GBM discret
    # log(S_{t+1}/S_t) = (mu - sigma^2/2)*dt + sigma*sqrt(dt)*Z
    rendements = (mu_j - 0.5 * sigma_j**2) + sigma_j * Z_corr

    # Reconstruction des prix par cumul des log-rendements
    log_prix = np.cumsum(rendements, axis=0)
    prix_initiaux_arr = np.array([prix_initiaux[t] for t in tickers])
    prix = prix_initiaux_arr * np.exp(log_prix)
    prix = np.vstack([prix_initiaux_arr, prix])  # Ajouter la ligne initiale

    # Création de l'index de dates ouvrées
    dates = pd.bdate_range(start=start_date, periods=n_days + 1, freq="B")

    df = pd.DataFrame(prix, index=dates, columns=tickers)
    df.index.name = "Date"
    return df


def main():
    """Point d'entrée : génère et sauvegarde example_prices.csv."""

    tickers = ["SPY", "EFA", "AGG", "GLD", "EURUSD"]

    # Paramètres calibrés sur ordre de grandeur marché 2020-2023
    mu_annuel = {
        "SPY":    0.10,    # ~10% rendement annuel espéré (actions US)
        "EFA":    0.07,    # ~7%  (actions internationales, légèrement moins)
        "AGG":   -0.02,    # ~-2% en période de hausse des taux
        "GLD":    0.05,    # ~5%  (or, valeur refuge)
        "EURUSD": 0.00,    # ~0%  (change, rendement espéré neutre)
    }

    sigma_annuel = {
        "SPY":    0.18,    # 18% volatilité annuelle (actions US)
        "EFA":    0.16,    # 16% (actions internationales)
        "AGG":    0.06,    # 6%  (obligations, plus faible)
        "GLD":    0.14,    # 14% (or)
        "EURUSD": 0.07,    # 7%  (FX majeur)
    }

    prix_initiaux = {
        "SPY":    370.0,
        "EFA":    70.0,
        "AGG":    115.0,
        "GLD":    175.0,
        "EURUSD": 1.22,
    }

    # Matrice de corrélation (calibrée sur observations historiques)
    # Ordre : SPY, EFA, AGG, GLD, EURUSD
    corr = np.array([
        [1.00,  0.80, -0.15,  0.05,  0.10],   # SPY
        [0.80,  1.00, -0.10,  0.05,  0.15],   # EFA
        [-0.15, -0.10, 1.00,  0.20, -0.05],   # AGG
        [0.05,  0.05,  0.20,  1.00,  0.10],   # GLD
        [0.10,  0.15, -0.05,  0.10,  1.00],   # EURUSD
    ])

    # Génération sur ~4 ans de données ouvrées (≈ 1008 jours)
    df = generate_correlated_gbm(
        n_days=1008,
        tickers=tickers,
        mu_annuel=mu_annuel,
        sigma_annuel=sigma_annuel,
        correlation_matrix=corr,
        prix_initiaux=prix_initiaux,
        seed=42,
        start_date="2020-01-02",
    )

    # Arrondi pour plus de réalisme
    df = df.round(4)

    output_path = Path(__file__).parent / "example_prices.csv"
    df.to_csv(output_path)
    print(f"Données générées : {len(df)} observations pour {len(tickers)} actifs.")
    print(f"Fichier sauvegardé : {output_path}")
    print(df.tail())


if __name__ == "__main__":
    main()
