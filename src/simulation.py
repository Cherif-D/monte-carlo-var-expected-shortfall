"""
simulation.py — Moteur de simulation Monte Carlo
=================================================
Ce module implémente le cœur du projet : la simulation de scénarios
de rendements multi-actifs et le calcul de la distribution des P&L.

Algorithme (cas gaussien)
--------------------------
1. Décomposition de Cholesky de la matrice de covariance :
       Sigma = L L^T  (L triangulaire inférieure)
2. Génération de vecteurs gaussiens indépendants :
       Z ~ N(0, I_n),  Z de dimension (N_simul x n_actifs)
3. Corrélation des innovations :
       X = Z @ L^T  =>  X ~ N(0, Sigma)
4. Ajout de la dérive :
       r_sim = mu_h + X
5. Calcul du rendement du portefeuille :
       r_p = r_sim @ w  =>  scalaire par simulation
6. Calcul du P&L :
       PnL = r_p * V_0

Cette procédure produit N_simul scénarios de P&L à l'horizon h,
qui forment la distribution empirique Monte Carlo.

Extension Student-t
-------------------
Pour mieux capturer les queues épaisses observées sur les marchés,
on peut remplacer l'étape 2 par une distribution de Student-t multivariée :
    X = Z / sqrt(chi2_nu / nu)
où chi2_nu ~ chi2(nu) est indépendant de Z.
"""

import logging

import numpy as np
import pandas as pd

from src.returns_model import ParametresRendements, echelonner_parametres

logger = logging.getLogger("var_mc.simulation")


# =============================================================================
# Résultats de simulation
# =============================================================================

class ResultatsSimulation:
    """
    Contient les résultats d'une simulation Monte Carlo.

    Attributs
    ---------
    pnl : np.ndarray
        Vecteur des P&L simulés (N_simul,), en devise.
    rendements_portfolio : np.ndarray
        Vecteur des rendements portfolio simulés (N_simul,).
    rendements_actifs : np.ndarray
        Matrice des rendements actifs simulés (N_simul x n_actifs).
    n_simulations : int
        Nombre de scénarios.
    horizon_jours : int
        Horizon de la simulation.
    distribution : str
        Nom de la distribution utilisée.
    seed : int
        Graine utilisée.
    """

    def __init__(
        self,
        pnl: np.ndarray,
        rendements_portfolio: np.ndarray,
        rendements_actifs: np.ndarray,
        horizon_jours: int,
        distribution: str,
        seed: int,
    ):
        self.pnl                  = pnl
        self.rendements_portfolio = rendements_portfolio
        self.rendements_actifs    = rendements_actifs
        self.n_simulations        = len(pnl)
        self.horizon_jours        = horizon_jours
        self.distribution         = distribution
        self.seed                 = seed

    @property
    def pertes(self) -> np.ndarray:
        """
        Vecteur des pertes (conventions : perte = valeur positive).
        Les pertes sont définies comme l'opposé des P&L négatifs.
        On travaille ici sur toute la distribution (pertes ET gains).
        """
        return -self.pnl

    def percentile(self, q: float) -> float:
        """
        Retourne le quantile q de la distribution des P&L.
        q=0.05 correspond au 5ème percentile.
        """
        return float(np.percentile(self.pnl, q * 100))

    def statistiques(self) -> dict:
        """Statistiques descriptives de la distribution simulée."""
        return {
            "n_simulations": self.n_simulations,
            "horizon_jours": self.horizon_jours,
            "distribution":  self.distribution,
            "mean_pnl":      float(self.pnl.mean()),
            "std_pnl":       float(self.pnl.std()),
            "min_pnl":       float(self.pnl.min()),
            "max_pnl":       float(self.pnl.max()),
            "skewness":      float(pd.Series(self.pnl).skew()),
            "kurtosis":      float(pd.Series(self.pnl).kurtosis()),
        }


# =============================================================================
# Moteur de simulation
# =============================================================================

def simuler_monte_carlo(
    params: ParametresRendements,
    poids: np.ndarray,
    valeur_initiale: float,
    n_simulations: int,
    horizon_jours: int,
    distribution: str = "normal",
    student_df: int = 5,
    seed: int = 42,
) -> ResultatsSimulation:
    """
    Lance la simulation Monte Carlo et retourne la distribution des P&L.

    Paramètres
    ----------
    params : ParametresRendements
        Paramètres calibrés sur données historiques.
    poids : np.ndarray
        Vecteur de poids du portefeuille (n_actifs,).
    valeur_initiale : float
        Valeur nominale du portefeuille.
    n_simulations : int
        Nombre de scénarios à simuler.
    horizon_jours : int
        Horizon en jours ouvrés.
    distribution : str
        "normal" ou "student".
    student_df : int
        Degrés de liberté pour la Student-t (si distribution="student").
    seed : int
        Graine aléatoire.

    Retourne
    --------
    ResultatsSimulation
        Objet contenant toute la distribution simulée.
    """
    rng = np.random.default_rng(seed)
    n_actifs = len(params.tickers)

    # 1. Échelonnage des paramètres à l'horizon h
    mu_h, cov_h = echelonner_parametres(params, horizon_jours)

    # 2. Décomposition de Cholesky de la matrice de covariance
    L = _cholesky_robuste(cov_h, params.tickers)

    # 3. Génération des innovations
    if distribution == "normal":
        innovations = _innovations_normales(rng, n_simulations, n_actifs)
    elif distribution == "student":
        innovations = _innovations_student(rng, n_simulations, n_actifs, student_df)
    else:
        raise ValueError(
            f"Distribution inconnue : '{distribution}'. "
            "Valeurs acceptées : 'normal', 'student'."
        )

    # 4. Transformation : Z -> X = mu + L @ Z  (corrélation + dérive)
    # Chaque ligne : r_sim[i] = mu_h + L @ innovations[i]
    rendements_actifs = mu_h + (innovations @ L.T)
    # rendements_actifs : shape (N_simul, n_actifs)

    # 5. Rendement du portefeuille
    rendements_portfolio = rendements_actifs @ poids
    # rendements_portfolio : shape (N_simul,)

    # 6. P&L
    pnl = rendements_portfolio * valeur_initiale

    logger.info(
        f"Simulation terminée : {n_simulations:,} scénarios, "
        f"horizon={horizon_jours}j, distribution={distribution}, seed={seed}. "
        f"PnL moyen={pnl.mean():,.0f} EUR, "
        f"PnL 1% percentile={np.percentile(pnl, 1):,.0f} EUR."
    )

    return ResultatsSimulation(
        pnl=pnl,
        rendements_portfolio=rendements_portfolio,
        rendements_actifs=rendements_actifs,
        horizon_jours=horizon_jours,
        distribution=distribution,
        seed=seed,
    )


# =============================================================================
# Fonctions auxiliaires
# =============================================================================

def _cholesky_robuste(cov: np.ndarray, tickers: list[str]) -> np.ndarray:
    """
    Décomposition de Cholesky avec régularisation si nécessaire.

    Pourquoi Cholesky ?
    -------------------
    Pour simuler X ~ N(0, Sigma), on décompose Sigma = L L^T et on pose
    X = L Z avec Z ~ N(0, I). Cela garantit Cov(X) = L Cov(Z) L^T = Sigma.

    La décomposition de Cholesky est préférable à la décomposition spectrale
    (eigendecomposition) pour sa stabilité numérique sur des matrices de
    petite dimension.

    Si la matrice est numériquement non définie positive (en raison d'erreurs
    d'arrondi), on ajoute une perturbation diagonale epsilon (régularisation
    de Tikhonov).

    Paramètres
    ----------
    cov : np.ndarray
        Matrice de covariance (n x n).
    tickers : list[str]
        Noms des actifs (pour les messages d'erreur).

    Retourne
    --------
    np.ndarray
        Matrice L triangulaire inférieure telle que L @ L.T = cov.
    """
    try:
        return np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        logger.warning(
            "Matrice de covariance non définie positive. "
            "Application de la régularisation de Tikhonov (epsilon=1e-8)."
        )
        eps = 1e-8
        n = cov.shape[0]
        cov_reg = cov + eps * np.eye(n)
        return np.linalg.cholesky(cov_reg)


def _innovations_normales(
    rng: np.random.Generator,
    n_simulations: int,
    n_actifs: int,
) -> np.ndarray:
    """
    Génère une matrice d'innovations gaussiennes standard i.i.d.

    Retourne
    --------
    np.ndarray
        Matrice (n_simulations x n_actifs) de N(0,1) i.i.d.
    """
    return rng.standard_normal((n_simulations, n_actifs))


def _innovations_student(
    rng: np.random.Generator,
    n_simulations: int,
    n_actifs: int,
    df: int,
) -> np.ndarray:
    """
    Génère des innovations suivant une Student-t multivariée.

    Méthode de génération
    ---------------------
    Une Student-t multivariée avec nu degrés de liberté s'obtient par :
        X = Z / sqrt(chi2_nu / nu)
    où Z ~ N(0, I) et chi2_nu ~ chi2(nu), indépendants.

    Cette construction est appelée "mélange gaussien" ou "variance-mean mixture".

    Avantage : les queues de la Student-t sont plus épaisses que la gaussienne,
    ce qui capte mieux les mouvements extrêmes observés sur les marchés.

    Paramètres
    ----------
    df : int
        Degrés de liberté. df=5 est courant en finance (queues épaisses).
        df -> infini tend vers la gaussienne.

    Retourne
    --------
    np.ndarray
        Matrice (n_simulations x n_actifs) d'innovations Student-t.
    """
    if df <= 2:
        raise ValueError(
            f"Les degrés de liberté doivent être > 2 pour que la variance "
            f"soit définie. Valeur reçue : df={df}."
        )

    Z = rng.standard_normal((n_simulations, n_actifs))
    # chi2_nu : scalaire partagé entre actifs => même "niveau de marché"
    chi2_nu = rng.chisquare(df=df, size=n_simulations)  # (N,)
    # Division : chaque ligne de Z divisée par sqrt(chi2/nu)
    scale = np.sqrt(chi2_nu / df)                       # (N,)
    return Z / scale[:, np.newaxis]


# =============================================================================
# Simulation multi-horizons (utilitaire pour la sensibilité)
# =============================================================================

def simuler_multi_horizons(
    params: ParametresRendements,
    poids: np.ndarray,
    valeur_initiale: float,
    horizons: list[int],
    n_simulations: int,
    distribution: str = "normal",
    seed: int = 42,
) -> dict[int, ResultatsSimulation]:
    """
    Lance des simulations pour plusieurs horizons simultanément.

    Paramètres
    ----------
    horizons : list[int]
        Liste d'horizons en jours (ex: [1, 5, 10, 21]).

    Retourne
    --------
    dict[int, ResultatsSimulation]
        Dictionnaire {horizon: ResultatsSimulation}.
    """
    resultats = {}
    for h in horizons:
        resultats[h] = simuler_monte_carlo(
            params=params,
            poids=poids,
            valeur_initiale=valeur_initiale,
            n_simulations=n_simulations,
            horizon_jours=h,
            distribution=distribution,
            seed=seed + h,  # graine différente par horizon pour indépendance
        )
    return resultats
