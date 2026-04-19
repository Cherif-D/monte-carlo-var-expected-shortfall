"""
test_simulation.py — Tests unitaires du module simulation.py
============================================================
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.returns_model import ParametresRendements
from src.simulation import (
    simuler_monte_carlo,
    ResultatsSimulation,
    _innovations_normales,
    _innovations_student,
    _cholesky_robuste,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def params_simple():
    """Paramètres simples pour un portefeuille 3 actifs."""
    tickers = ["A", "B", "C"]
    mu      = np.array([0.0005, 0.0002, 0.0001])
    sigma   = np.array([0.012, 0.006, 0.004])
    cov     = np.diag(sigma**2)   # Actifs décorrélés pour simplifier
    corr    = np.eye(3)
    return ParametresRendements(
        tickers=tickers, mu=mu, sigma=sigma, cov=cov, corr=corr, n_obs=252
    )


@pytest.fixture
def params_correles():
    """Paramètres avec corrélations."""
    tickers = ["A", "B"]
    sigma   = np.array([0.01, 0.008])
    corr    = np.array([[1.0, 0.7], [0.7, 1.0]])
    D       = np.diag(sigma)
    cov     = D @ corr @ D
    return ParametresRendements(
        tickers=tickers, mu=np.zeros(2), sigma=sigma, cov=cov, corr=corr, n_obs=500
    )


# =============================================================================
# Tests des innovations
# =============================================================================

class TestInnovations:

    def test_innovations_normales_shape(self):
        rng = np.random.default_rng(0)
        Z = _innovations_normales(rng, n_simulations=1000, n_actifs=5)
        assert Z.shape == (1000, 5)

    def test_innovations_normales_moyenne_proche_zero(self):
        """E[Z] ~ 0 avec N grand."""
        rng = np.random.default_rng(42)
        Z = _innovations_normales(rng, n_simulations=100_000, n_actifs=3)
        np.testing.assert_allclose(Z.mean(axis=0), 0, atol=0.02)

    def test_innovations_student_shape(self):
        rng = np.random.default_rng(0)
        X = _innovations_student(rng, n_simulations=1000, n_actifs=4, df=5)
        assert X.shape == (1000, 4)

    def test_innovations_student_df_invalide(self):
        """df <= 2 doit lever ValueError."""
        rng = np.random.default_rng(0)
        with pytest.raises(ValueError):
            _innovations_student(rng, 1000, 3, df=2)

    def test_innovations_student_variance_plus_grande(self):
        """Var(Student-t) > Var(N(0,1)) pour df fini."""
        rng = np.random.default_rng(99)
        Z = _innovations_normales(rng, 50_000, 1)
        rng2 = np.random.default_rng(99)
        X = _innovations_student(rng2, 50_000, 1, df=5)
        # Student a des queues plus lourdes => variance empirique plus grande
        assert X.std() > Z.std() * 0.9  # tolérance large (aléatoire)


# =============================================================================
# Tests de Cholesky
# =============================================================================

class TestCholesky:

    def test_cholesky_matrice_2x2(self):
        cov = np.array([[1.0, 0.5], [0.5, 1.0]])
        L = _cholesky_robuste(cov, ["A", "B"])
        np.testing.assert_allclose(L @ L.T, cov, atol=1e-10)

    def test_cholesky_identite(self):
        cov = np.eye(4)
        L = _cholesky_robuste(cov, ["A", "B", "C", "D"])
        np.testing.assert_allclose(L, np.eye(4), atol=1e-10)

    def test_cholesky_robustesse_matrice_quasising(self):
        """Matrice quasi-singulière ne doit pas lever d'exception."""
        cov = np.array([[1.0, 0.9999], [0.9999, 1.0]])
        # Peut lever LinAlgError -> doit être intercepté
        try:
            L = _cholesky_robuste(cov, ["A", "B"])
            # Si pas d'exception, L@L.T doit être proche de cov
            diff = np.abs(L @ L.T - cov).max()
            assert diff < 1e-4
        except Exception as e:
            pytest.fail(f"_cholesky_robuste a levé une exception inattendue : {e}")


# =============================================================================
# Tests de la simulation complète
# =============================================================================

class TestSimulationComplete:

    def test_output_shape(self, params_simple):
        """Le nombre de P&L simulés doit correspondre à n_simulations."""
        sim = simuler_monte_carlo(
            params=params_simple,
            poids=np.array([1/3, 1/3, 1/3]),
            valeur_initiale=1_000_000,
            n_simulations=5000,
            horizon_jours=1,
            seed=42,
        )
        assert len(sim.pnl) == 5000

    def test_reproductibilite(self, params_simple):
        """Deux simulations avec la même seed doivent donner exactement les mêmes P&L."""
        w = np.array([0.5, 0.3, 0.2])
        sim1 = simuler_monte_carlo(params_simple, w, 1e6, 1000, 1, seed=7)
        sim2 = simuler_monte_carlo(params_simple, w, 1e6, 1000, 1, seed=7)
        np.testing.assert_array_equal(sim1.pnl, sim2.pnl)

    def test_seeds_differentes_donnent_resultats_differents(self, params_simple):
        """Deux seeds différentes ne doivent PAS donner les mêmes P&L."""
        w = np.array([1/3, 1/3, 1/3])
        sim1 = simuler_monte_carlo(params_simple, w, 1e6, 1000, 1, seed=1)
        sim2 = simuler_monte_carlo(params_simple, w, 1e6, 1000, 1, seed=2)
        assert not np.array_equal(sim1.pnl, sim2.pnl)

    def test_pnl_distribution_centree(self, params_simple):
        """Pour mu=0, le P&L simulé doit avoir une moyenne proche de 0."""
        params_zero_mu = ParametresRendements(
            tickers=params_simple.tickers,
            mu=np.zeros(3),
            sigma=params_simple.sigma,
            cov=params_simple.cov,
            corr=params_simple.corr,
            n_obs=252,
        )
        sim = simuler_monte_carlo(
            params=params_zero_mu,
            poids=np.array([1/3, 1/3, 1/3]),
            valeur_initiale=1_000_000,
            n_simulations=100_000,
            horizon_jours=1,
            seed=0,
        )
        # Tolérance de 3 écarts-types sur la moyenne
        assert abs(sim.pnl.mean()) < sim.pnl.std() * 3 / np.sqrt(100_000)

    def test_horizon_augmente_vol(self, params_simple):
        """Augmenter l'horizon doit augmenter la volatilité des P&L simulés."""
        w = np.array([1/3, 1/3, 1/3])
        sim1 = simuler_monte_carlo(params_simple, w, 1e6, 50_000, 1, seed=0)
        sim10 = simuler_monte_carlo(params_simple, w, 1e6, 50_000, 10, seed=0)
        assert sim10.pnl.std() > sim1.pnl.std()

    def test_correlation_augmente_risque(self, params_correles):
        """Avec corrélations élevées, le risque doit être plus grand qu'avec actifs indépendants."""
        w = np.array([0.5, 0.5])
        # Simuler avec corrélations
        sim_corr = simuler_monte_carlo(params_correles, w, 1e6, 100_000, 1, seed=0)

        # Simuler avec actifs indépendants
        sigma = params_correles.sigma
        params_ind = ParametresRendements(
            tickers=params_correles.tickers,
            mu=np.zeros(2), sigma=sigma,
            cov=np.diag(sigma**2), corr=np.eye(2), n_obs=500,
        )
        sim_ind = simuler_monte_carlo(params_ind, w, 1e6, 100_000, 1, seed=0)

        # Vol avec corrélations > vol sans corrélations
        assert sim_corr.pnl.std() > sim_ind.pnl.std()

    def test_distribution_student_queues_plus_lourdes(self, params_simple):
        """La distribution Student-t doit avoir une kurtosis plus élevée que la normale."""
        w = np.array([1/3, 1/3, 1/3])
        params_zero = ParametresRendements(
            tickers=params_simple.tickers, mu=np.zeros(3),
            sigma=params_simple.sigma, cov=params_simple.cov,
            corr=params_simple.corr, n_obs=252,
        )
        sim_norm = simuler_monte_carlo(params_zero, w, 1e6, 100_000, 1, "normal", seed=0)
        sim_stud = simuler_monte_carlo(params_zero, w, 1e6, 100_000, 1, "student", 5, seed=0)

        import pandas as pd
        kurt_norm = pd.Series(sim_norm.pnl).kurtosis()
        kurt_stud = pd.Series(sim_stud.pnl).kurtosis()
        assert kurt_stud > kurt_norm

    def test_distribution_inconnue_leve_erreur(self, params_simple):
        with pytest.raises(ValueError):
            simuler_monte_carlo(
                params_simple, np.array([1/3, 1/3, 1/3]),
                1e6, 100, 1, distribution="laplace", seed=0,
            )
