"""
risk_metrics.py — Calcul de la VaR et de l'Expected Shortfall
=============================================================
Ce module centralise le calcul des mesures de risque pour le portefeuille.

Trois méthodes sont implémentées pour chaque mesure :

1. Méthode historique (non-paramétrique)
   - Utilise directement la distribution empirique des rendements passés.
   - Avantage : aucune hypothèse distributionnelle.
   - Limite : dépend fortement de la fenêtre historique disponible.

2. Méthode paramétrique gaussienne
   - Suppose des rendements normalement distribués.
   - Formule analytique fermée.
   - Avantage : simple, rapide, interprétable.
   - Limite : sous-estime les queues de distribution (kurtosis empirique > 3).

3. Méthode Monte Carlo
   - Utilise la distribution empirique des simulations.
   - Avantage : flexible, peut intégrer des distributions non-gaussiennes.
   - Limite : variance d'estimation (converge avec le nombre de simulations).

Conventions
-----------
  - La VaR est exprimée en PERTE (valeur positive = perte monétaire).
  - La VaR(alpha) au niveau alpha correspond au quantile (1-alpha)
    de la distribution des P&L, pris avec signe négatif.
  - Exemple : VaR(99%) = -quantile(1%) des P&L = perte dépassée avec probabilité 1%.

  Formellement : VaR_alpha = -inf{x : P(PnL <= x) >= 1 - alpha}
               = -Q_{1-alpha}(PnL)
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from src.simulation import ResultatsSimulation

logger = logging.getLogger("var_mc.risk_metrics")


# =============================================================================
# Structures de résultats
# =============================================================================

@dataclass
class ResultatsRisque:
    """
    Contient les résultats VaR/ES pour une méthode et un niveau de confiance.

    Attributs
    ---------
    methode : str
        Nom de la méthode ("historique", "parametrique", "monte_carlo").
    niveau_confiance : float
        Niveau de confiance (ex : 0.95, 0.99).
    horizon_jours : int
        Horizon en jours ouvrés.
    var : float
        Value-at-Risk en EUR (perte positive).
    es : float
        Expected Shortfall en EUR (perte positive, >= VaR).
    var_pct : float
        VaR en % de la valeur initiale du portefeuille.
    es_pct : float
        ES en % de la valeur initiale.
    valeur_initiale : float
        Valeur du portefeuille utilisée.
    """
    methode:           str
    niveau_confiance:  float
    horizon_jours:     int
    var:               float
    es:                float
    valeur_initiale:   float

    @property
    def var_pct(self) -> float:
        return self.var / self.valeur_initiale * 100

    @property
    def es_pct(self) -> float:
        return self.es / self.valeur_initiale * 100

    @property
    def ratio_es_var(self) -> float:
        """Ratio ES/VaR. Toujours >= 1 par construction. Mesure l'excès de risque au-delà de la VaR."""
        return self.es / self.var if self.var > 0 else float("nan")

    def to_dict(self) -> dict:
        return {
            "Méthode":            self.methode,
            "Niveau confiance":   f"{self.niveau_confiance*100:.1f}%",
            "Horizon (jours)":    self.horizon_jours,
            "VaR (EUR)":          round(self.var, 2),
            "ES (EUR)":           round(self.es, 2),
            "VaR (%)":            round(self.var_pct, 4),
            "ES (%)":             round(self.es_pct, 4),
            "Ratio ES/VaR":       round(self.ratio_es_var, 4),
        }


# =============================================================================
# Méthode historique
# =============================================================================

def var_es_historique(
    pnl_historique: np.ndarray,
    niveau_confiance: float,
    valeur_initiale: float,
    horizon_jours: int = 1,
) -> ResultatsRisque:
    """
    Calcule la VaR et l'ES par la méthode historique.

    Principe
    --------
    On utilise directement la distribution empirique des P&L historiques.
    La VaR est le quantile (1 - alpha) de cette distribution.
    L'ES est la moyenne des P&L en-dessous de ce quantile.

    Formule
    -------
    VaR_alpha = -quantile_{1-alpha}(P&L)
    ES_alpha  = -E[P&L | P&L <= -VaR_alpha]
              = -mean{PnL_t : PnL_t <= Q_{1-alpha}(PnL)}

    Extrapolation multi-jours (règle racine carrée)
    -----------------------------------------------
    Si horizon_jours > 1 et les données sont journalières, on applique :
        VaR_h = VaR_1j * sqrt(h)
    Cette règle est une approximation valide sous hypothèse i.i.d.

    Paramètres
    ----------
    pnl_historique : np.ndarray
        Série de P&L historiques (N observations).
    niveau_confiance : float
        Niveau de confiance alpha (ex : 0.99).
    valeur_initiale : float
        Valeur du portefeuille (pour normalisation en %).
    horizon_jours : int
        Horizon d'extrapolation (règle racine carrée si > 1).

    Retourne
    --------
    ResultatsRisque
    """
    alpha = niveau_confiance
    seuil = np.percentile(pnl_historique, (1 - alpha) * 100)

    # VaR : perte positive
    var_1j = -seuil

    # ES : espérance conditionnelle des pertes dépassant la VaR
    pertes_extremes = pnl_historique[pnl_historique <= seuil]
    if len(pertes_extremes) == 0:
        logger.warning(
            f"Aucune observation en-dessous du seuil VaR ({seuil:.2f}) "
            f"pour alpha={alpha}. ES non défini."
        )
        es_1j = var_1j  # Fallback conservateur
    else:
        es_1j = -pertes_extremes.mean()

    # Extrapolation multi-jours
    facteur_horizon = np.sqrt(horizon_jours)
    var = var_1j * facteur_horizon
    es  = es_1j  * facteur_horizon

    logger.debug(
        f"[Historique] VaR({alpha*100:.0f}%, {horizon_jours}j) = {var:,.0f} EUR | "
        f"ES = {es:,.0f} EUR"
    )
    return ResultatsRisque(
        methode="historique",
        niveau_confiance=alpha,
        horizon_jours=horizon_jours,
        var=var,
        es=es,
        valeur_initiale=valeur_initiale,
    )


# =============================================================================
# Méthode paramétrique gaussienne
# =============================================================================

def var_es_parametrique(
    mu_portfolio: float,
    sigma_portfolio: float,
    valeur_initiale: float,
    niveau_confiance: float,
    horizon_jours: int = 1,
) -> ResultatsRisque:
    """
    Calcule la VaR et l'ES par la méthode paramétrique gaussienne.

    Principe
    --------
    On suppose PnL ~ N(mu * V_0, sigma^2 * V_0^2).
    La VaR s'exprime alors analytiquement via le quantile de la normale.

    Formules
    --------
    Pour PnL ~ N(mu_p, sigma_p^2) avec mu_p = mu*V_0 et sigma_p = sigma*V_0 :

        VaR_alpha = -(mu_p + sigma_p * z_{1-alpha})
        ES_alpha  = -(mu_p - sigma_p * phi(z_{1-alpha}) / (1-alpha))

    où z_{1-alpha} est le quantile (1-alpha) de N(0,1)
    et phi est la densité de N(0,1).

    Extrapolation multi-jours
    -------------------------
        mu_h = mu_j * h
        sigma_h = sigma_j * sqrt(h)

    Paramètres
    ----------
    mu_portfolio : float
        Rendement moyen journalier du portefeuille.
    sigma_portfolio : float
        Volatilité journalière du portefeuille.
    valeur_initiale : float
        Valeur nominale.
    niveau_confiance : float
        Niveau alpha.
    horizon_jours : int
        Horizon en jours.

    Retourne
    --------
    ResultatsRisque
    """
    alpha = niveau_confiance

    # Paramètres à l'horizon h
    mu_h    = mu_portfolio    * horizon_jours
    sigma_h = sigma_portfolio * np.sqrt(horizon_jours)

    # Quantile de la normale standard
    z_alpha = stats.norm.ppf(1 - alpha)   # négatif pour alpha > 0.5

    # VaR
    # PnL ~ N(mu_h * V0, (sigma_h * V0)^2)
    # Q_{1-alpha}(PnL) = V0*(mu_h + sigma_h * z_{1-alpha})
    # VaR = -Q_{1-alpha}(PnL)
    var_rendement = -(mu_h + sigma_h * z_alpha)   # en rendement
    var = var_rendement * valeur_initiale

    # ES analytique pour la normale
    # ES = V0 * (-mu_h + sigma_h * phi(z_{1-alpha}) / (1-alpha))
    phi_z = stats.norm.pdf(z_alpha)
    es_rendement = -mu_h + sigma_h * phi_z / (1 - alpha)
    es = es_rendement * valeur_initiale

    # Cohérence : ES >= VaR (toujours vrai analytiquement, vérification numérique)
    if es < var - 1e-6:
        logger.warning(
            f"ES ({es:.2f}) < VaR ({var:.2f}) pour méthode paramétrique. "
            "Vérifiez les paramètres."
        )

    logger.debug(
        f"[Paramétrique] VaR({alpha*100:.0f}%, {horizon_jours}j) = {var:,.0f} EUR | "
        f"ES = {es:,.0f} EUR"
    )
    return ResultatsRisque(
        methode="parametrique",
        niveau_confiance=alpha,
        horizon_jours=horizon_jours,
        var=var,
        es=es,
        valeur_initiale=valeur_initiale,
    )


# =============================================================================
# Méthode Monte Carlo
# =============================================================================

def var_es_monte_carlo(
    resultats_simulation: ResultatsSimulation,
    valeur_initiale: float,
    niveau_confiance: float,
) -> ResultatsRisque:
    """
    Calcule la VaR et l'ES à partir des simulations Monte Carlo.

    Principe
    --------
    On utilise la distribution empirique des P&L simulés, exactement
    comme la méthode historique mais sur les données simulées.

    VaR = -percentile(P&L_simulés, (1-alpha)*100)
    ES  = -mean(P&L_simulés qui sont <= -VaR)

    Avantage sur la méthode paramétrique
    -------------------------------------
    La MC ne suppose PAS de forme fonctionnelle pour la distribution :
    si on utilise la Student-t multivariée, les queues simulées sont plus
    épaisses et la VaR/ES capte mieux les événements extrêmes.

    Paramètres
    ----------
    resultats_simulation : ResultatsSimulation
        Résultats de la simulation Monte Carlo.
    valeur_initiale : float
        Valeur nominale du portefeuille.
    niveau_confiance : float
        Niveau de confiance alpha.

    Retourne
    --------
    ResultatsRisque
    """
    alpha = niveau_confiance
    pnl   = resultats_simulation.pnl

    seuil = np.percentile(pnl, (1 - alpha) * 100)
    var   = -seuil

    pertes_extremes = pnl[pnl <= seuil]
    if len(pertes_extremes) == 0:
        es = var
    else:
        es = -pertes_extremes.mean()

    logger.debug(
        f"[Monte Carlo] VaR({alpha*100:.0f}%, "
        f"{resultats_simulation.horizon_jours}j) = {var:,.0f} EUR | "
        f"ES = {es:,.0f} EUR"
    )
    return ResultatsRisque(
        methode="monte_carlo",
        niveau_confiance=alpha,
        horizon_jours=resultats_simulation.horizon_jours,
        var=var,
        es=es,
        valeur_initiale=valeur_initiale,
    )


# =============================================================================
# Calcul groupé et tableaux récapitulatifs
# =============================================================================

def calculer_toutes_mesures(
    pnl_historique: np.ndarray,
    mu_portfolio: float,
    sigma_portfolio: float,
    resultats_mc: ResultatsSimulation,
    valeur_initiale: float,
    niveaux_confiance: list[float],
    horizon_jours: int,
) -> pd.DataFrame:
    """
    Calcule toutes les mesures de risque pour tous les niveaux de confiance
    et toutes les méthodes, et retourne un tableau récapitulatif.

    Paramètres
    ----------
    (voir les fonctions individuelles)

    Retourne
    --------
    pd.DataFrame
        Tableau croisé : méthodes en lignes, niveaux de confiance en colonnes.
    """
    lignes = []
    for alpha in niveaux_confiance:
        for res in [
            var_es_historique(
                pnl_historique, alpha, valeur_initiale, horizon_jours
            ),
            var_es_parametrique(
                mu_portfolio, sigma_portfolio, valeur_initiale, alpha, horizon_jours
            ),
            var_es_monte_carlo(
                resultats_mc, valeur_initiale, alpha
            ),
        ]:
            lignes.append(res.to_dict())

    df = pd.DataFrame(lignes)
    return df


# =============================================================================
# Backtesting simplifié
# =============================================================================

def backtester_var(
    pnl_historique: np.ndarray,
    var_series: np.ndarray,
    niveau_confiance: float,
) -> dict:
    """
    Backtesting simplifié de la VaR par comptage des exceptions (Basel).

    Une "exception" se produit lorsque la perte réalisée dépasse la VaR prévue.
    Sous l'hypothèse nulle (modèle correct), la fréquence des exceptions
    devrait être (1 - alpha).

    Test de Kupiec (1995)
    ---------------------
    H0 : p = 1 - alpha  (fréquence des exceptions conforme)
    La statistique est LR = -2 * ln(p0^x * (1-p0)^(T-x) / p^x * (1-p)^(T-x))
    où p = x/T est la fréquence observée, p0 = 1-alpha, T = nb d'observations.
    Elle suit une chi2(1) sous H0.

    Paramètres
    ----------
    pnl_historique : np.ndarray
        P&L réalisés (in-sample ou out-of-sample).
    var_series : np.ndarray
        Série de VaR prévues pour chaque période (même longueur).
    niveau_confiance : float
        Niveau de confiance utilisé.

    Retourne
    --------
    dict
        Résultats du backtesting.
    """
    from scipy.stats import chi2

    T = len(pnl_historique)
    if len(var_series) != T:
        raise ValueError(
            f"pnl_historique ({T}) et var_series ({len(var_series)}) "
            "doivent avoir la même longueur."
        )

    # Nombre d'exceptions : jours où la perte > VaR
    exceptions = np.sum(pnl_historique < -var_series)
    p_obs      = exceptions / T
    p_theo     = 1 - niveau_confiance

    # Statistique de Kupiec
    if p_obs == 0 or p_obs == 1:
        lr_stat  = np.nan
        lr_pval  = np.nan
        verdict  = "Indéterminé (0 ou 100% d'exceptions)"
    else:
        lr_stat = -2 * (
            exceptions * np.log(p_theo / p_obs)
            + (T - exceptions) * np.log((1 - p_theo) / (1 - p_obs))
        )
        lr_pval = 1 - chi2.cdf(lr_stat, df=1)
        verdict = (
            "Modèle VALIDE (Kupiec, 5%)"
            if lr_pval > 0.05
            else "Modèle REJETÉ (Kupiec, 5%)"
        )

    resultats = {
        "n_observations":     T,
        "niveau_confiance":   niveau_confiance,
        "freq_theo_exception": p_theo,
        "n_exceptions":       int(exceptions),
        "freq_obs_exception": round(p_obs, 4),
        "LR_stat":            round(lr_stat, 4) if not np.isnan(lr_stat) else "N/A",
        "LR_pval":            round(lr_pval, 4) if not np.isnan(lr_pval) else "N/A",
        "verdict":            verdict,
    }
    logger.info(
        f"Backtesting VaR({niveau_confiance*100:.0f}%) : "
        f"{exceptions}/{T} exceptions ({p_obs*100:.2f}% vs {p_theo*100:.1f}% théorique). "
        f"{verdict}"
    )
    return resultats


# =============================================================================
# Attribution marginale du risque
# =============================================================================

def attribution_marginale_risque(
    rendements_actifs: np.ndarray,
    poids: np.ndarray,
    valeur_initiale: float,
    niveau_confiance: float,
) -> dict:
    """
    Calcule la contribution marginale de chaque actif à la VaR du portefeuille.

    Méthode : dérivée numérique de la VaR par rapport aux poids.
    La contribution marginale de l'actif i est la dérivée ∂VaR/∂w_i.
    La contribution totale de l'actif i est w_i * ∂VaR/∂w_i.
    La somme des contributions totales = VaR du portefeuille (Euler).

    Paramètres
    ----------
    rendements_actifs : np.ndarray
        Matrice (T x n) de rendements simulés ou historiques.
    poids : np.ndarray
        Vecteur de poids.
    valeur_initiale : float
        Valeur nominale.
    niveau_confiance : float
        Niveau de confiance.

    Retourne
    --------
    dict
        Contributions marginales et totales par actif.
    """
    alpha = niveau_confiance
    eps   = 1e-4   # Perturbation pour la dérivée numérique
    n     = len(poids)

    def var_pour_poids(w: np.ndarray) -> float:
        """VaR du portefeuille avec les poids w."""
        pnl = rendements_actifs @ w * valeur_initiale
        return float(-np.percentile(pnl, (1 - alpha) * 100))

    var_base = var_pour_poids(poids)
    contrib_marginale = np.zeros(n)

    for i in range(n):
        w_plus         = poids.copy()
        w_minus        = poids.copy()
        w_plus[i]     += eps
        w_minus[i]    -= eps
        # Renormaliser pour maintenir la contrainte somme = 1
        w_plus        /= w_plus.sum()
        w_minus       /= w_minus.sum()
        contrib_marginale[i] = (var_pour_poids(w_plus) - var_pour_poids(w_minus)) / (2 * eps)

    contrib_totale  = poids * contrib_marginale
    contrib_pct     = contrib_totale / var_base * 100 if var_base > 0 else np.zeros(n)

    return {
        "var_totale":          var_base,
        "contrib_marginale":   contrib_marginale,
        "contrib_totale":      contrib_totale,
        "contrib_pct":         contrib_pct,
    }
