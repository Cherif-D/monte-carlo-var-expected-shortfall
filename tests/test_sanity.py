"""
test_sanity.py — Tests de cohérence globale du pipeline
=======================================================
Ces tests vérifient des propriétés mathématiques fondamentales :
  - la VaR est cohérente avec la règle racine carrée,
  - l'ES est toujours >= VaR,
  - les résultats sont stables avec un grand nombre de simulations,
  - les résultats sont indépendants de l'ordre des actifs dans le portefeuille,
  - la diversification réduit effectivement le risque.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.returns_model import ParametresRendements
from src.simulation import simuler_monte_carlo
from src.risk_metrics import var_es_monte_carlo, var_es_parametrique


# =============================================================================
# Fixture : paramètres simples décorrélés
# =============================================================================

@pytest.fixture
def params_2actifs():
    sigma = np.array([0.012, 0.008])
    cov   = np.diag(sigma**2)
    return ParametresRendements(
        tickers=["X", "Y"],
        mu=np.zeros(2),
        sigma=sigma,
        cov=cov,
        corr=np.eye(2),
        n_obs=500,
    )


# =============================================================================
# Propriété 1 : ES >= VaR pour tout niveau de confiance
# =============================================================================

class TestESSuperioriteVaR:

    @pytest.mark.parametrize("alpha", [0.90, 0.95, 0.99, 0.999])
    def test_es_geq_var_mc(self, params_2actifs, alpha):
        """ES >= VaR pour tout alpha, en MC."""
        sim = simuler_monte_carlo(params_2actifs, np.array([0.5, 0.5]),
                                   1_000_000, 100_000, 1, seed=42)
        res = var_es_monte_carlo(sim, 1_000_000, alpha)
        assert res.es >= res.var - 1.0  # tolérance 1 EUR (arrondi)

    @pytest.mark.parametrize("alpha", [0.90, 0.95, 0.99])
    def test_es_geq_var_parametrique(self, alpha):
        """ES >= VaR pour tout alpha, en paramétrique."""
        res = var_es_parametrique(0.0, 0.01, 1_000_000, alpha, 1)
        assert res.es >= res.var - 1e-6


# =============================================================================
# Propriété 2 : Règle racine carrée du temps (approximation)
# =============================================================================

class TestRegleRacineCarre:

    def test_sqrt_time_approx(self, params_2actifs):
        """
        VaR_h ≈ VaR_1 * sqrt(h).
        Pour h=4, VaR_4 doit être proche de 2 * VaR_1.
        Tolérance : 10% (la MC n'est qu'une approximation).
        """
        w = np.array([0.5, 0.5])
        sim_1 = simuler_monte_carlo(params_2actifs, w, 1e6, 200_000, 1, seed=0)
        sim_4 = simuler_monte_carlo(params_2actifs, w, 1e6, 200_000, 4, seed=1)

        var_1 = var_es_monte_carlo(sim_1, 1e6, 0.99).var
        var_4 = var_es_monte_carlo(sim_4, 1e6, 0.99).var

        ratio = var_4 / var_1
        assert 1.7 < ratio < 2.3, (
            f"Règle racine carrée : VaR_4 / VaR_1 = {ratio:.3f} (attendu ≈ 2.0)"
        )


# =============================================================================
# Propriété 3 : Diversification réduit le risque
# =============================================================================

class TestDiversification:

    def test_diversification_reduit_var(self):
        """
        Un portefeuille diversifié (poids égaux) doit avoir une VaR inférieure
        à un portefeuille concentré sur un seul actif, si les actifs sont
        décorrélés et ont des volatilités similaires.
        """
        sigma = np.array([0.02, 0.02])
        cov   = np.diag(sigma**2)
        params = ParametresRendements(
            tickers=["A", "B"], mu=np.zeros(2),
            sigma=sigma, cov=cov, corr=np.eye(2), n_obs=500,
        )

        # Portefeuille concentré sur A
        w_concentre = np.array([1.0, 0.0])
        # Portefeuille diversifié
        w_diversifie = np.array([0.5, 0.5])

        v0 = 1_000_000
        sim_c = simuler_monte_carlo(params, w_concentre, v0, 100_000, 1, seed=0)
        sim_d = simuler_monte_carlo(params, w_diversifie, v0, 100_000, 1, seed=0)

        var_c = var_es_monte_carlo(sim_c, v0, 0.99).var
        var_d = var_es_monte_carlo(sim_d, v0, 0.99).var

        # Le portefeuille diversifié doit avoir une VaR inférieure
        # (actifs décorrélés : VaR_div ≈ VaR_conc / sqrt(2) ≈ 0.71 * VaR_conc)
        assert var_d < var_c

    def test_ratio_diversification(self):
        """
        Pour 2 actifs identiques décorrélés, VaR_div / VaR_conc ≈ 1/sqrt(2).
        """
        sigma = np.array([0.015, 0.015])
        cov   = np.diag(sigma**2)
        params = ParametresRendements(
            tickers=["A", "B"], mu=np.zeros(2),
            sigma=sigma, cov=cov, corr=np.eye(2), n_obs=500,
        )
        v0 = 1_000_000

        sim_c = simuler_monte_carlo(params, np.array([1.0, 0.0]), v0, 200_000, 1, seed=0)
        sim_d = simuler_monte_carlo(params, np.array([0.5, 0.5]), v0, 200_000, 1, seed=0)

        var_c = var_es_monte_carlo(sim_c, v0, 0.99).var
        var_d = var_es_monte_carlo(sim_d, v0, 0.99).var
        ratio = var_d / var_c

        # Théoriquement 1/sqrt(2) ≈ 0.707
        assert 0.60 < ratio < 0.80, (
            f"Ratio de diversification = {ratio:.3f} (attendu ≈ 0.707)"
        )


# =============================================================================
# Propriété 4 : Convergence MC avec N grand
# =============================================================================

class TestConvergenceMC:

    def test_convergence_var(self):
        """
        La VaR MC doit converger vers la VaR analytique quand N -> infini.
        Pour une loi gaussienne N(0, sigma), on connaît la VaR analytique.
        """
        sigma = 0.01
        v0    = 1_000_000
        alpha = 0.99

        # VaR analytique
        from scipy.stats import norm
        var_analytique = sigma * norm.ppf(alpha) * v0

        params = ParametresRendements(
            tickers=["A"],
            mu=np.array([0.0]),
            sigma=np.array([sigma]),
            cov=np.array([[sigma**2]]),
            corr=np.eye(1),
            n_obs=500,
        )

        sim = simuler_monte_carlo(params, np.array([1.0]), v0, 500_000, 1, seed=0)
        var_mc = var_es_monte_carlo(sim, v0, alpha).var

        # Tolérance de 2% sur la VaR
        erreur_relative = abs(var_mc - var_analytique) / var_analytique
        assert erreur_relative < 0.02, (
            f"VaR MC = {var_mc:,.0f}, VaR analytique = {var_analytique:,.0f}, "
            f"erreur = {erreur_relative*100:.2f}%"
        )


# =============================================================================
# Propriété 5 : Invariance à l'ordre des actifs (symétrie)
# =============================================================================

class TestSymetrie:

    def test_invariance_ordre_actifs(self):
        """
        Permuter l'ordre des actifs (en permutant les poids de la même façon)
        ne doit PAS changer la VaR du portefeuille.
        """
        sigma = np.array([0.01, 0.02])
        corr  = np.array([[1.0, 0.4], [0.4, 1.0]])
        D     = np.diag(sigma)
        cov   = D @ corr @ D

        params_AB = ParametresRendements(
            tickers=["A", "B"], mu=np.zeros(2),
            sigma=sigma, cov=cov, corr=corr, n_obs=500,
        )
        # Permutation : B puis A
        sigma_perm = sigma[[1, 0]]
        cov_perm   = cov[np.ix_([1, 0], [1, 0])]
        corr_perm  = corr[np.ix_([1, 0], [1, 0])]
        params_BA  = ParametresRendements(
            tickers=["B", "A"], mu=np.zeros(2),
            sigma=sigma_perm, cov=cov_perm, corr=corr_perm, n_obs=500,
        )

        w = np.array([0.4, 0.6])
        w_perm = w[[1, 0]]  # On permute aussi les poids

        v0 = 1_000_000
        sim_AB = simuler_monte_carlo(params_AB, w,      v0, 100_000, 1, seed=99)
        sim_BA = simuler_monte_carlo(params_BA, w_perm, v0, 100_000, 1, seed=99)

        var_AB = var_es_monte_carlo(sim_AB, v0, 0.99).var
        var_BA = var_es_monte_carlo(sim_BA, v0, 0.99).var

        np.testing.assert_allclose(var_AB, var_BA, rtol=0.01)


# =============================================================================
# Tests d'import et structure du projet
# =============================================================================

class TestImports:

    def test_imports_principaux(self):
        """Tous les modules principaux doivent s'importer sans erreur."""
        import src.utils
        import src.data_loader
        import src.portfolio
        import src.returns_model
        import src.simulation
        import src.risk_metrics
        import src.sensitivity
        import src.plots
        import src.report

    def test_version_definie(self):
        import src
        assert hasattr(src, "__version__")
        assert isinstance(src.__version__, str)
