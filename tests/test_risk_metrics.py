"""
test_risk_metrics.py — Tests unitaires du module risk_metrics.py
================================================================
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk_metrics import (
    var_es_historique,
    var_es_parametrique,
    var_es_monte_carlo,
    backtester_var,
)
from src.returns_model import ParametresRendements
from src.simulation import simuler_monte_carlo


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def pnl_gaussien():
    """P&L gaussiens simulés : N(0, 5000^2)."""
    rng = np.random.default_rng(42)
    return rng.normal(loc=0, scale=5_000, size=10_000)


@pytest.fixture
def sim_mc():
    """Simulation MC simple pour les tests."""
    params = ParametresRendements(
        tickers=["A", "B"],
        mu=np.array([0.0, 0.0]),
        sigma=np.array([0.01, 0.008]),
        cov=np.array([[1e-4, 4.8e-5], [4.8e-5, 6.4e-5]]),
        corr=np.array([[1.0, 0.6], [0.6, 1.0]]),
        n_obs=500,
    )
    return simuler_monte_carlo(params, np.array([0.5, 0.5]), 1_000_000, 100_000, 1, seed=42)


# =============================================================================
# Tests VaR historique
# =============================================================================

class TestVaRHistorique:

    def test_var_positive(self, pnl_gaussien):
        """La VaR doit toujours être positive."""
        res = var_es_historique(pnl_gaussien, 0.95, 1_000_000, 1)
        assert res.var > 0

    def test_es_superieur_var(self, pnl_gaussien):
        """ES >= VaR toujours."""
        res = var_es_historique(pnl_gaussien, 0.99, 1_000_000, 1)
        assert res.es >= res.var - 1.0  # tolérance 1 EUR

    def test_var99_superieur_var95(self, pnl_gaussien):
        """VaR 99% >= VaR 95%."""
        r95 = var_es_historique(pnl_gaussien, 0.95, 1_000_000, 1)
        r99 = var_es_historique(pnl_gaussien, 0.99, 1_000_000, 1)
        assert r99.var >= r95.var

    def test_horizon_augmente_var(self, pnl_gaussien):
        """VaR multi-jours (règle sqrt) > VaR 1 jour."""
        r1 = var_es_historique(pnl_gaussien, 0.99, 1_000_000, 1)
        r10 = var_es_historique(pnl_gaussien, 0.99, 1_000_000, 10)
        assert r10.var > r1.var

    def test_methode_label(self, pnl_gaussien):
        res = var_es_historique(pnl_gaussien, 0.95, 1_000_000, 1)
        assert res.methode == "historique"

    def test_var_pct_coherent(self, pnl_gaussien):
        """var_pct = var / valeur_initiale * 100."""
        vi = 500_000
        res = var_es_historique(pnl_gaussien, 0.95, vi, 1)
        assert abs(res.var_pct - res.var / vi * 100) < 1e-8

    def test_valeur_approx_gaussienne(self, pnl_gaussien):
        """
        Pour des P&L ~ N(0, 5000^2), la VaR 95% doit être proche de
        5000 * z_0.95 = 5000 * 1.645 ≈ 8225 EUR.
        """
        from scipy.stats import norm
        res = var_es_historique(pnl_gaussien, 0.95, 1_000_000, 1)
        attendu = 5_000 * norm.ppf(0.95)
        # Tolérance relative de 5%
        assert abs(res.var - attendu) / attendu < 0.05


# =============================================================================
# Tests VaR paramétrique
# =============================================================================

class TestVaRParametrique:

    def test_var_positive(self):
        res = var_es_parametrique(0.0, 0.01, 1_000_000, 0.95, 1)
        assert res.var > 0

    def test_es_superieur_var(self):
        res = var_es_parametrique(0.0, 0.01, 1_000_000, 0.99, 1)
        assert res.es > res.var

    def test_var_formule_correcte(self):
        """
        Pour mu=0, sigma=0.01 : VaR 95% = sigma * z_0.95 * V_0
        = 0.01 * 1.6449 * 1_000_000 ≈ 16449 EUR.
        """
        from scipy.stats import norm
        sigma = 0.01
        v0    = 1_000_000
        alpha = 0.95
        res   = var_es_parametrique(0.0, sigma, v0, alpha, 1)
        attendu = sigma * norm.ppf(alpha) * v0
        np.testing.assert_allclose(res.var, attendu, rtol=1e-6)

    def test_es_formule_correcte(self):
        """
        Pour mu=0 : ES = sigma * phi(z_alpha) / (1-alpha) * V_0.
        """
        from scipy.stats import norm
        sigma = 0.01
        v0    = 1_000_000
        alpha = 0.99
        res   = var_es_parametrique(0.0, sigma, v0, alpha, 1)
        z = norm.ppf(alpha)
        attendu = sigma * norm.pdf(z) / (1 - alpha) * v0
        np.testing.assert_allclose(res.es, attendu, rtol=1e-6)

    def test_mu_negatif_augmente_var(self):
        """Rendement espéré négatif => VaR plus grande."""
        r_neutre = var_es_parametrique(0.0,   0.01, 1e6, 0.99, 1)
        r_neg    = var_es_parametrique(-0.01, 0.01, 1e6, 0.99, 1)
        assert r_neg.var > r_neutre.var


# =============================================================================
# Tests VaR Monte Carlo
# =============================================================================

class TestVaRMonteCarlo:

    def test_var_positive(self, sim_mc):
        res = var_es_monte_carlo(sim_mc, 1_000_000, 0.95)
        assert res.var > 0

    def test_es_superieur_var(self, sim_mc):
        res = var_es_monte_carlo(sim_mc, 1_000_000, 0.99)
        assert res.es >= res.var

    def test_var99_superieur_var95(self, sim_mc):
        r95 = var_es_monte_carlo(sim_mc, 1_000_000, 0.95)
        r99 = var_es_monte_carlo(sim_mc, 1_000_000, 0.99)
        assert r99.var >= r95.var

    def test_methode_label(self, sim_mc):
        res = var_es_monte_carlo(sim_mc, 1_000_000, 0.99)
        assert res.methode == "monte_carlo"

    def test_ratio_es_var_superieur_1(self, sim_mc):
        res = var_es_monte_carlo(sim_mc, 1_000_000, 0.99)
        assert res.ratio_es_var >= 1.0 - 1e-8


# =============================================================================
# Tests backtesting
# =============================================================================

class TestBacktesting:

    def test_backtesting_frequence_proche_theorique(self, pnl_gaussien):
        """
        Pour des P&L i.i.d. gaussiens et une VaR parfaitement calibrée,
        la fréquence d'exceptions doit être proche de 5%.
        """
        from scipy.stats import norm
        sigma = pnl_gaussien.std()
        var_calibree = np.full(len(pnl_gaussien), abs(sigma * norm.ppf(0.05)))
        res = backtester_var(pnl_gaussien, var_calibree, 0.95)
        # La fréquence observée doit être proche de 5%
        assert abs(res["freq_obs_exception"] - 0.05) < 0.02

    def test_tailles_differentes_leve_erreur(self, pnl_gaussien):
        var_mauvaise_taille = np.zeros(10)
        with pytest.raises(ValueError):
            backtester_var(pnl_gaussien, var_mauvaise_taille, 0.95)
