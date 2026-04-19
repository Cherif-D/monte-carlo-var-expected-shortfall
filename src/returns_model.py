"""
returns_model.py — Calibration du modèle de rendements
=======================================================
Ce module estime les paramètres statistiques des rendements historiques
qui seront utilisés pour les simulations Monte Carlo et la VaR paramétrique.

Paramètres estimés
------------------
  mu     : vecteur de rendements moyens journaliers (n_actifs,)
  sigma  : vecteur de volatilités journalières (n_actifs,)
  Sigma  : matrice de covariance journalière (n_actifs x n_actifs)
  Corr   : matrice de corrélation (n_actifs x n_actifs)

Hypothèse principale
--------------------
  Par défaut, on suppose que les rendements sont i.i.d. de loi normale
  multivariée N(mu, Sigma). Cette hypothèse est une simplification connue
  (elle sous-estime les queues épaisses observées empiriquement), mais elle
  constitue le point de départ standard en risk management académique.

  Une extension avec distribution de Student est documentée en module simulation.
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger("var_mc.returns_model")


# =============================================================================
# Dataclass de paramètres
# =============================================================================

@dataclass
class ParametresRendements:
    """
    Contient tous les paramètres estimés sur les données historiques.

    Attributs
    ---------
    tickers : list[str]
        Noms des actifs dans l'ordre du vecteur/matrice.
    mu : np.ndarray
        Rendements moyens journaliers (vecteur n,).
    sigma : np.ndarray
        Volatilités journalières individuelles (vecteur n,).
    cov : np.ndarray
        Matrice de covariance journalière (n x n).
    corr : np.ndarray
        Matrice de corrélation (n x n).
    n_obs : int
        Nombre d'observations utilisées pour la calibration.
    """

    tickers: list[str]
    mu:      np.ndarray
    sigma:   np.ndarray
    cov:     np.ndarray
    corr:    np.ndarray
    n_obs:   int

    def annualiser(self, jours: int = 252) -> dict:
        """
        Retourne les paramètres annualisés.

        Conventions
        -----------
        - mu annuel  = mu_j * 252
        - sigma ann. = sigma_j * sqrt(252)
        - La matrice de corrélation ne dépend pas de l'horizon.
        """
        return {
            "mu_annuel":    self.mu    * jours,
            "sigma_annuel": self.sigma * np.sqrt(jours),
            "corr":         self.corr.copy(),
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Représentation tabulaire des paramètres par actif."""
        ann = self.annualiser()
        df = pd.DataFrame(index=self.tickers)
        df["mu_journalier"]       = self.mu
        df["sigma_journalier"]    = self.sigma
        df["mu_annuel"]           = ann["mu_annuel"]
        df["sigma_annuel"]        = ann["sigma_annuel"]
        return df.round(6)

    def __repr__(self) -> str:
        df = self.to_dataframe()
        return (
            f"ParametresRendements ({self.n_obs} obs, {len(self.tickers)} actifs)\n"
            + df.to_string()
        )


# =============================================================================
# Calibration
# =============================================================================

def calibrer_parametres(
    rendements: pd.DataFrame,
    tickers: list[str] | None = None,
    ddof: int = 1,
) -> ParametresRendements:
    """
    Estime les paramètres statistiques à partir des rendements historiques.

    Cette fonction est le cœur de la calibration. Elle calcule les estimateurs
    empiriques standards :
      - mu_i  = (1/T) * sum_t r_{i,t}       (moyenne empirique)
      - sigma_i = std(r_i)                   (écart-type empirique)
      - Sigma   = (1/(T-1)) * R^T R - mu mu^T (matrice de covariance empirique)
      - Corr    = D^{-1} Sigma D^{-1}        (D = diag des sigma)

    Paramètres
    ----------
    rendements : pd.DataFrame
        Log-rendements journaliers (T x n).
    tickers : list[str] | None
        Sous-ensemble d'actifs à calibrer. Si None, tous les actifs sont pris.
    ddof : int
        Degrés de liberté pour l'estimateur de variance. 1 = estimateur
        non-biaisé (de Bessel), 0 = estimateur MLE.

    Retourne
    --------
    ParametresRendements
        Objet contenant tous les paramètres calibrés.
    """
    if tickers is None:
        tickers = list(rendements.columns)

    r = rendements[tickers].values  # shape (T, n)
    T, n = r.shape

    if T < 30:
        logger.warning(
            f"Seulement {T} observations disponibles pour la calibration. "
            "Les estimations seront peu robustes. Recommandé : > 250 obs."
        )

    mu    = r.mean(axis=0)                           # (n,)
    sigma = r.std(axis=0, ddof=ddof)                 # (n,)
    cov   = np.cov(r.T, ddof=ddof)                   # (n, n)

    # Calcul explicite de la matrice de corrélation pour éviter les imprécisions
    # numériques dues aux divisions dans np.corrcoef
    D_inv = np.diag(1.0 / sigma)
    corr  = D_inv @ cov @ D_inv

    # Forcer la symétrie exacte (erreurs d'arrondi numériques)
    corr = 0.5 * (corr + corr.T)
    np.fill_diagonal(corr, 1.0)

    params = ParametresRendements(
        tickers=tickers,
        mu=mu,
        sigma=sigma,
        cov=cov,
        corr=corr,
        n_obs=T,
    )

    logger.info(
        f"Calibration effectuée sur {T} observations, {n} actifs. "
        f"Vol. journalières : {dict(zip(tickers, sigma.round(4)))}"
    )

    _verifier_parametres(params)
    return params


def _verifier_parametres(params: ParametresRendements) -> None:
    """
    Contrôles de cohérence sur les paramètres calibrés.
    Émet des avertissements si des valeurs semblent anormales.
    """
    # Volatilités anormalement élevées
    SEUIL_VOL_J = 0.05  # 5% de vol journalière = ~80% annuelle = extrême
    idx_vol_eleve = np.where(params.sigma > SEUIL_VOL_J)[0]
    if len(idx_vol_eleve) > 0:
        noms = [params.tickers[i] for i in idx_vol_eleve]
        logger.warning(
            f"Volatilités journalières élevées (> {SEUIL_VOL_J*100:.0f}%) : {noms}. "
            "Vérifiez les données."
        )

    # Matrice de covariance définie positive
    valeurs_propres = np.linalg.eigvalsh(params.cov)
    if np.any(valeurs_propres < -1e-8):
        raise ValueError(
            "La matrice de covariance n'est pas définie semi-positive.\n"
            f"Plus petite valeur propre : {valeurs_propres.min():.2e}\n"
            "Vérifiez les données (actifs très corrélés ou données insuffisantes)."
        )

    # Corrélations dans [-1, 1]
    corr_hd = params.corr[np.triu_indices_from(params.corr, k=1)]
    if np.any(np.abs(corr_hd) > 1.0 + 1e-6):
        logger.warning("Certaines corrélations sont hors de [-1, 1]. Vérifier la calibration.")


# =============================================================================
# Tests de normalité (optionnel, à titre informatif)
# =============================================================================

def tester_normalite(rendements: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le test de Jarque-Bera sur chaque actif pour évaluer
    si l'hypothèse de normalité est plausible.

    Interprétation
    --------------
    - p-value > 0.05 : on ne rejette pas la normalité (au seuil 5%).
    - p-value < 0.05 : on rejette la normalité — les queues épaisses
      ou la skewness sont significatives.

    En pratique, les rendements financiers rejettent presque toujours la
    normalité (kurtosis > 3 = "leptokurtique"), ce qui est une limite
    importante de notre modèle gaussien.

    Paramètres
    ----------
    rendements : pd.DataFrame
        Log-rendements journaliers.

    Retourne
    --------
    pd.DataFrame
        Tableau avec statistiques JB et p-values par actif.
    """
    resultats = {}
    for col in rendements.columns:
        r = rendements[col].dropna().values
        jb_stat, jb_pval = stats.jarque_bera(r)
        _, sw_pval = stats.shapiro(r[:5000])  # Shapiro limité à 5000 obs
        resultats[col] = {
            "JB_stat":   round(jb_stat, 2),
            "JB_pval":   round(jb_pval, 4),
            "Skewness":  round(float(pd.Series(r).skew()), 4),
            "Kurtosis":  round(float(pd.Series(r).kurtosis()), 4),  # kurtosis excès
            "SW_pval":   round(sw_pval, 4),
            "Normal_5%": "OUI" if jb_pval > 0.05 else "NON",
        }
    return pd.DataFrame(resultats).T


def echelonner_parametres(
    params: ParametresRendements,
    horizon_jours: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Échelonne les paramètres à un horizon multi-jours.

    Règle de la racine carrée du temps (hypothèse i.i.d.) :
      mu_h    = mu_j * h
      sigma_h = sigma_j * sqrt(h)
      Sigma_h = Sigma_j * h

    Cette règle est valide sous l'hypothèse que les rendements sont
    indépendants et identiquement distribués (i.i.d.). Elle est une
    approximation acceptable pour des horizons courts (< 30 jours).

    Paramètres
    ----------
    params : ParametresRendements
        Paramètres journaliers calibrés.
    horizon_jours : int
        Horizon cible en jours ouvrés.

    Retourne
    --------
    tuple[np.ndarray, np.ndarray]
        (mu_h, cov_h) : vecteur de rendements et matrice de covariance
        à l'horizon h.
    """
    mu_h   = params.mu  * horizon_jours
    cov_h  = params.cov * horizon_jours
    return mu_h, cov_h
