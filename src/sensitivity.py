"""
sensitivity.py — Analyses de sensibilité
=========================================
Ce module implémente les expériences de sensibilité paramétriques :
stress-testing de la VaR et de l'ES en faisant varier les hypothèses du modèle.

Analyses disponibles
--------------------
1. Sensibilité à la volatilité
   → On multiplie les volatilités par un facteur (0.5x à 2x).
   → Permet de visualiser l'impact d'une hausse/baisse de la volatilité de marché.

2. Sensibilité à la corrélation
   → On fait varier les corrélations hors-diagonale (de 0 à 1.5x).
   → Illustre l'effet de diversification et son érosion en période de stress.
   → Note : en crise, les corrélations tendent vers 1 (perte de diversification).

3. Sensibilité à l'horizon
   → On calcule VaR/ES pour 1j, 5j, 10j, 21j.
   → Illustre la règle racine carrée du temps.

4. Sensibilité au niveau de confiance
   → On fait varier alpha de 90% à 99.9%.
   → Illustre la sensibilité des mesures aux scénarios extrêmes rares.

5. Comparaison équipondéré vs. portefeuille cible
   → Mesure le bénéfice ou coût de l'allocation active.

Philosophie
-----------
L'analyse de sensibilité est essentielle en risk management car les modèles
reposent sur des hypothèses (distribution, corrélations, horizons) qui sont
incertaines. Connaître la sensibilité des résultats à ces hypothèses permet
d'évaluer la robustesse des conclusions et de définir des scénarios de stress.
"""

import logging
from copy import deepcopy

import numpy as np
import pandas as pd

from src.returns_model import ParametresRendements, echelonner_parametres
from src.simulation import simuler_monte_carlo
from src.risk_metrics import (
    var_es_historique,
    var_es_monte_carlo,
    var_es_parametrique,
    ResultatsRisque,
)

logger = logging.getLogger("var_mc.sensitivity")


# =============================================================================
# Utilitaire : reconstruction d'une matrice de covariance stressée
# =============================================================================

def stresser_covariance(
    cov_base: np.ndarray,
    sigma_base: np.ndarray,
    facteur_vol: float = 1.0,
    facteur_corr: float = 1.0,
) -> np.ndarray:
    """
    Applique des chocs de volatilité et de corrélation à une matrice de covariance.

    Méthode
    -------
    1. Extraire la corrélation : Corr = D^{-1} Sigma D^{-1}  (D = diag(sigma))
    2. Appliquer le choc de corrélation : Corr_stress = clip(facteur_corr * Corr_off_diag + I)
    3. Appliquer le choc de volatilité : sigma_stress = facteur_vol * sigma
    4. Reconstruire : Sigma_stress = D_stress Corr_stress D_stress

    Le clipping garantit que les corrélations restent dans [-1, 1].

    Paramètres
    ----------
    cov_base : np.ndarray
        Matrice de covariance de base (n x n).
    sigma_base : np.ndarray
        Volatilités individuelles de base (n,).
    facteur_vol : float
        Multiplicateur de volatilité (ex: 1.5 = +50%).
    facteur_corr : float
        Multiplicateur des corrélations hors-diagonale.

    Retourne
    --------
    np.ndarray
        Matrice de covariance stressée (définie positive).
    """
    n = len(sigma_base)

    # Volatilités stressées
    sigma_stress = sigma_base * facteur_vol

    # Matrice de corrélation de base
    D_inv = np.diag(1.0 / sigma_base)
    corr  = D_inv @ cov_base @ D_inv

    # Choc sur les corrélations hors-diagonale uniquement
    corr_stress = corr.copy()
    masque_hd = ~np.eye(n, dtype=bool)
    corr_stress[masque_hd] = np.clip(corr[masque_hd] * facteur_corr, -0.9999, 0.9999)

    # Symétrie
    corr_stress = 0.5 * (corr_stress + corr_stress.T)
    np.fill_diagonal(corr_stress, 1.0)

    # Vérification de la définition positive
    valeurs_propres = np.linalg.eigvalsh(corr_stress)
    if np.any(valeurs_propres < 0):
        # Correction par regularisation
        eps = np.abs(valeurs_propres.min()) + 1e-8
        corr_stress += eps * np.eye(n)
        # Re-normalisation des diagonales
        d = np.sqrt(np.diag(corr_stress))
        corr_stress = corr_stress / np.outer(d, d)
        np.fill_diagonal(corr_stress, 1.0)

    # Reconstruction de la covariance
    D_stress = np.diag(sigma_stress)
    cov_stress = D_stress @ corr_stress @ D_stress
    return cov_stress


def _params_stresses(
    params_base: ParametresRendements,
    facteur_vol: float = 1.0,
    facteur_corr: float = 1.0,
) -> ParametresRendements:
    """
    Retourne une copie des paramètres avec volatilités/corrélations stressées.
    """
    cov_stress = stresser_covariance(
        params_base.cov, params_base.sigma,
        facteur_vol=facteur_vol, facteur_corr=facteur_corr,
    )
    sigma_stress = params_base.sigma * facteur_vol
    D_inv = np.diag(1.0 / sigma_stress)
    corr_stress = D_inv @ cov_stress @ D_inv
    corr_stress = 0.5 * (corr_stress + corr_stress.T)
    np.fill_diagonal(corr_stress, 1.0)

    return ParametresRendements(
        tickers=params_base.tickers,
        mu=params_base.mu.copy(),
        sigma=sigma_stress,
        cov=cov_stress,
        corr=corr_stress,
        n_obs=params_base.n_obs,
    )


# =============================================================================
# Analyse 1 : Sensibilité à la volatilité
# =============================================================================

def sensibilite_volatilite(
    params_base: ParametresRendements,
    poids: np.ndarray,
    valeur_initiale: float,
    facteurs_vol: list[float],
    niveaux_confiance: list[float],
    n_simulations: int,
    horizon_jours: int = 1,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Calcule la VaR MC pour différents niveaux de volatilité.

    Paramètres
    ----------
    facteurs_vol : list[float]
        Multiplicateurs de volatilité à tester.

    Retourne
    --------
    pd.DataFrame
        Tableau (facteur_vol x niveau_confiance).
    """
    resultats = []
    for fv in facteurs_vol:
        params_s = _params_stresses(params_base, facteur_vol=fv)
        sim = simuler_monte_carlo(
            params=params_s,
            poids=poids,
            valeur_initiale=valeur_initiale,
            n_simulations=n_simulations,
            horizon_jours=horizon_jours,
            seed=seed,
        )
        for alpha in niveaux_confiance:
            res = var_es_monte_carlo(sim, valeur_initiale, alpha)
            resultats.append({
                "Facteur volatilité": fv,
                "Niveau confiance":   f"{alpha*100:.0f}%",
                "VaR MC (EUR)":       round(res.var, 0),
                "ES MC (EUR)":        round(res.es, 0),
                "VaR MC (%)":         round(res.var_pct, 3),
            })

    logger.info(
        f"Sensibilité volatilité calculée : "
        f"{len(facteurs_vol)} facteurs x {len(niveaux_confiance)} niveaux."
    )
    return pd.DataFrame(resultats)


# =============================================================================
# Analyse 2 : Sensibilité à la corrélation
# =============================================================================

def sensibilite_correlation(
    params_base: ParametresRendements,
    poids: np.ndarray,
    valeur_initiale: float,
    facteurs_corr: list[float],
    niveaux_confiance: list[float],
    n_simulations: int,
    horizon_jours: int = 1,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Calcule la VaR MC pour différents niveaux de corrélation.

    Paramètres
    ----------
    facteurs_corr : list[float]
        Multiplicateurs des corrélations hors-diagonale.
        - 0.0 : actifs décorrélés (diversification maximale)
        - 1.0 : corrélations historiques (baseline)
        - 1.5 : stress (corrélations augmentées)
    """
    resultats = []
    for fc in facteurs_corr:
        label_corr = (
            "Indépendants (0)"
            if fc == 0
            else f"{fc}x historique"
        )
        params_s = _params_stresses(params_base, facteur_corr=fc)
        sim = simuler_monte_carlo(
            params=params_s,
            poids=poids,
            valeur_initiale=valeur_initiale,
            n_simulations=n_simulations,
            horizon_jours=horizon_jours,
            seed=seed,
        )
        for alpha in niveaux_confiance:
            res = var_es_monte_carlo(sim, valeur_initiale, alpha)
            resultats.append({
                "Facteur corrélation": fc,
                "Label corrélation":   label_corr,
                "Niveau confiance":    f"{alpha*100:.0f}%",
                "VaR MC (EUR)":        round(res.var, 0),
                "ES MC (EUR)":         round(res.es, 0),
                "VaR MC (%)":          round(res.var_pct, 3),
            })

    logger.info(
        f"Sensibilité corrélation calculée : "
        f"{len(facteurs_corr)} facteurs x {len(niveaux_confiance)} niveaux."
    )
    return pd.DataFrame(resultats)


# =============================================================================
# Analyse 3 : Sensibilité à l'horizon
# =============================================================================

def sensibilite_horizon(
    params_base: ParametresRendements,
    poids: np.ndarray,
    valeur_initiale: float,
    horizons: list[int],
    niveaux_confiance: list[float],
    n_simulations: int,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Calcule la VaR MC pour différents horizons temporels.

    Illustre la règle racine carrée du temps.
    """
    resultats = []
    for h in horizons:
        sim = simuler_monte_carlo(
            params=params_base,
            poids=poids,
            valeur_initiale=valeur_initiale,
            n_simulations=n_simulations,
            horizon_jours=h,
            seed=seed + h,
        )
        for alpha in niveaux_confiance:
            res = var_es_monte_carlo(sim, valeur_initiale, alpha)
            resultats.append({
                "Horizon (jours)": h,
                "Niveau confiance": f"{alpha*100:.0f}%",
                "VaR MC (EUR)":     round(res.var, 0),
                "ES MC (EUR)":      round(res.es, 0),
                "VaR MC (%)":       round(res.var_pct, 3),
                "ES / VaR":         round(res.ratio_es_var, 3),
            })
    return pd.DataFrame(resultats)


# =============================================================================
# Analyse 4 : Sensibilité au niveau de confiance
# =============================================================================

def sensibilite_niveau_confiance(
    resultats_mc: object,  # ResultatsSimulation
    pnl_historique: np.ndarray,
    mu_portfolio: float,
    sigma_portfolio: float,
    valeur_initiale: float,
    niveaux: list[float],
    horizon_jours: int = 1,
) -> pd.DataFrame:
    """
    Calcule VaR et ES pour une large gamme de niveaux de confiance,
    pour les trois méthodes.
    """
    resultats = []
    for alpha in niveaux:
        for methode, res in [
            ("Historique", var_es_historique(
                pnl_historique, alpha, valeur_initiale, horizon_jours
            )),
            ("Paramétrique", var_es_parametrique(
                mu_portfolio, sigma_portfolio, valeur_initiale, alpha, horizon_jours
            )),
            ("Monte Carlo", var_es_monte_carlo(
                resultats_mc, valeur_initiale, alpha
            )),
        ]:
            resultats.append({
                "Niveau confiance": alpha,
                "Méthode":          methode,
                "VaR (EUR)":        round(res.var, 0),
                "ES (EUR)":         round(res.es, 0),
                "VaR (%)":          round(res.var_pct, 4),
            })
    return pd.DataFrame(resultats)


# =============================================================================
# Analyse 5 : Comparaison portefeuille utilisateur vs équipondéré
# =============================================================================

def comparer_portefeuilles(
    params_base: ParametresRendements,
    poids_user: np.ndarray,
    poids_eq: np.ndarray,
    valeur_initiale: float,
    niveaux_confiance: list[float],
    n_simulations: int,
    horizon_jours: int = 1,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Compare la VaR/ES entre le portefeuille défini par l'utilisateur
    et un portefeuille de référence équipondéré.
    """
    resultats = []
    for nom_ptf, poids in [("Utilisateur", poids_user), ("Équipondéré", poids_eq)]:
        sim = simuler_monte_carlo(
            params=params_base,
            poids=poids,
            valeur_initiale=valeur_initiale,
            n_simulations=n_simulations,
            horizon_jours=horizon_jours,
            seed=seed,
        )
        for alpha in niveaux_confiance:
            res = var_es_monte_carlo(sim, valeur_initiale, alpha)
            resultats.append({
                "Portefeuille":     nom_ptf,
                "Niveau confiance": f"{alpha*100:.0f}%",
                "VaR MC (EUR)":     round(res.var, 0),
                "ES MC (EUR)":      round(res.es, 0),
                "VaR MC (%)":       round(res.var_pct, 3),
            })
    return pd.DataFrame(resultats)
