"""
utils.py — Fonctions utilitaires transverses
============================================
Ce module regroupe les fonctions auxiliaires utilisées par l'ensemble du projet :
  - chargement de la configuration YAML,
  - initialisation du logger,
  - fixation de la graine aléatoire,
  - manipulation de chemins.

Conception : les fonctions ici ne contiennent aucune logique financière.
Elles sont purement techniques et réutilisables dans n'importe quel projet.
"""

import logging
import sys
import yaml
import numpy as np
from pathlib import Path
from typing import Any


# =============================================================================
# Configuration
# =============================================================================

def charger_config(chemin: str = "config.yaml") -> dict[str, Any]:
    """
    Charge le fichier de configuration YAML.

    Paramètres
    ----------
    chemin : str
        Chemin relatif ou absolu vers config.yaml.

    Retourne
    --------
    dict
        Dictionnaire Python issu du fichier YAML.

    Lève
    ----
    FileNotFoundError si le fichier n'existe pas.
    ValueError si le fichier est vide ou invalide.
    """
    p = Path(chemin)
    if not p.exists():
        raise FileNotFoundError(
            f"Fichier de configuration introuvable : {p.resolve()}\n"
            "Vérifiez que config.yaml est bien à la racine du projet."
        )
    with open(p, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if config is None:
        raise ValueError(f"Le fichier de configuration {chemin} est vide.")
    return config


# =============================================================================
# Logging
# =============================================================================

def initialiser_logger(
    nom: str = "var_mc",
    niveau: str = "INFO",
    fichier_log: str | None = None,
    afficher_console: bool = True,
) -> logging.Logger:
    """
    Initialise et retourne un logger configuré.

    Un même logger peut écrire simultanément en console et dans un fichier.
    L'appel multiple avec le même nom retourne le même logger (idempotent).

    Paramètres
    ----------
    nom : str
        Nom du logger (utilisé pour identifier la source dans les logs).
    niveau : str
        Niveau de log : "DEBUG", "INFO", "WARNING", "ERROR".
    fichier_log : str | None
        Chemin vers le fichier de log. Si None, pas de fichier.
    afficher_console : bool
        Afficher les logs en console si True.
    """
    logger = logging.getLogger(nom)
    if logger.handlers:
        # Évite de doubler les handlers si appelé plusieurs fois
        return logger

    logger.setLevel(getattr(logging, niveau.upper(), logging.INFO))
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if afficher_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    if fichier_log:
        Path(fichier_log).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(fichier_log, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


# =============================================================================
# Reproductibilité
# =============================================================================

def fixer_seed(seed: int = 42) -> None:
    """
    Fixe la graine aléatoire de numpy pour garantir la reproductibilité.

    Pourquoi c'est important :
    Les simulations Monte Carlo reposent sur des nombres pseudo-aléatoires.
    Sans graine fixe, deux exécutions successives donnent des résultats
    légèrement différents, ce qui complique la validation et le débogage.

    Paramètres
    ----------
    seed : int
        Valeur de la graine. 42 est conventionnel mais arbitraire.
    """
    np.random.seed(seed)


# =============================================================================
# Chemins
# =============================================================================

def creer_dossiers_sortie(config: dict) -> None:
    """
    Crée les dossiers de sortie s'ils n'existent pas.

    Paramètres
    ----------
    config : dict
        Configuration complète (depuis config.yaml).
    """
    dossiers = [
        config["outputs"]["dossier_figures"],
        config["outputs"]["dossier_tables"],
        config["outputs"]["dossier_reports"],
        config["outputs"]["dossier_logs"],
    ]
    for d in dossiers:
        Path(d).mkdir(parents=True, exist_ok=True)


def chemin_figure(nom: str, config: dict) -> Path:
    """Retourne le chemin complet pour sauvegarder une figure."""
    ext = config["outputs"].get("format_figures", "png")
    return Path(config["outputs"]["dossier_figures"]) / f"{nom}.{ext}"


def chemin_table(nom: str, config: dict) -> Path:
    """Retourne le chemin complet pour sauvegarder un tableau CSV."""
    return Path(config["outputs"]["dossier_tables"]) / f"{nom}.csv"


# =============================================================================
# Validation
# =============================================================================

def verifier_poids(poids: dict[str, float], tolerance: float = 1e-6) -> None:
    """
    Vérifie que les poids du portefeuille somment à 1.

    Paramètres
    ----------
    poids : dict
        Dictionnaire {ticker: poids}.
    tolerance : float
        Tolérance numérique pour la vérification.

    Lève
    ----
    ValueError si la somme s'éloigne de 1 de plus que la tolérance.
    """
    total = sum(poids.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(
            f"Les poids du portefeuille somment à {total:.6f} au lieu de 1.0.\n"
            f"Poids actuels : {poids}\n"
            "Corrigez les poids dans config.yaml."
        )


def verifier_matrice_correlation(corr: np.ndarray) -> None:
    """
    Vérifie qu'une matrice de corrélation est bien formée :
    - symétrique,
    - diagonale = 1,
    - valeurs propres toutes positives (définie positive).

    Paramètres
    ----------
    corr : np.ndarray
        Matrice de corrélation (n x n).

    Lève
    ----
    ValueError si l'une des conditions n'est pas satisfaite.
    """
    n = corr.shape[0]

    if not np.allclose(corr, corr.T, atol=1e-8):
        raise ValueError("La matrice de corrélation n'est pas symétrique.")

    if not np.allclose(np.diag(corr), np.ones(n), atol=1e-8):
        raise ValueError("La diagonale de la matrice de corrélation doit être 1.")

    valeurs_propres = np.linalg.eigvalsh(corr)
    if np.any(valeurs_propres < -1e-8):
        raise ValueError(
            f"La matrice de corrélation n'est pas définie semi-positive.\n"
            f"Valeurs propres minimales : {valeurs_propres.min():.6f}"
        )
