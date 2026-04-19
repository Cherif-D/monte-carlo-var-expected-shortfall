"""
test_portfolio.py — Tests unitaires du module portfolio.py
===========================================================
Vérifie la construction du portefeuille, les calculs de rendements
et la cohérence des statistiques.
"""

import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.portfolio import Portfolio, portfolio_depuis_config, portfolio_equipondere
from src.utils import verifier_poids


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def poids_test():
    return {"SPY": 0.40, "AGG": 0.35, "GLD": 0.25}


@pytest.fixture
def ptf_simple(poids_test):
    return Portfolio(nom="Test", poids=poids_test, valeur_initiale=100_000.0)


@pytest.fixture
def rendements_test():
    np.random.seed(0)
    dates = pd.bdate_range("2022-01-03", periods=252)
    data = {
        "SPY": np.random.normal(0.0004, 0.01, 252),
        "AGG": np.random.normal(0.0001, 0.003, 252),
        "GLD": np.random.normal(0.0002, 0.008, 252),
    }
    return pd.DataFrame(data, index=dates)


# =============================================================================
# Tests construction
# =============================================================================

class TestPortfolioConstruction:

    def test_poids_valides(self, poids_test):
        """La somme des poids doit être exactement 1."""
        ptf = Portfolio(nom="T", poids=poids_test)
        assert abs(sum(ptf.poids.values()) - 1.0) < 1e-9

    def test_poids_invalides_leve_erreur(self):
        """Des poids ne sommant pas à 1 doivent lever ValueError."""
        poids_invalides = {"SPY": 0.5, "AGG": 0.3}  # somme = 0.8
        with pytest.raises(ValueError, match="somment"):
            Portfolio(nom="T", poids=poids_invalides)

    def test_tickers_dans_bon_ordre(self, ptf_simple):
        """Les tickers doivent respecter l'ordre du dictionnaire."""
        assert ptf_simple.tickers == ["SPY", "AGG", "GLD"]

    def test_vecteur_poids_correct(self, ptf_simple, poids_test):
        """Le vecteur numpy doit correspondre aux poids du dictionnaire."""
        w = ptf_simple.vecteur_poids
        assert len(w) == 3
        assert abs(w[0] - poids_test["SPY"]) < 1e-9
        assert abs(w.sum() - 1.0) < 1e-9

    def test_valeur_initiale_defaut(self):
        """La valeur initiale par défaut doit être 1 000 000."""
        ptf = Portfolio(nom="T", poids={"A": 0.5, "B": 0.5})
        assert ptf.valeur_initiale == 1_000_000.0


# =============================================================================
# Tests calcul des rendements
# =============================================================================

class TestRendementsPortfolio:

    def test_rendements_shape(self, ptf_simple, rendements_test):
        """Le résultat doit avoir autant de lignes que les rendements."""
        r = ptf_simple.calculer_rendements(rendements_test)
        assert len(r) == len(rendements_test)

    def test_rendements_combinaison_lineaire(self, ptf_simple, rendements_test):
        """r_portfolio = sum_i(w_i * r_i) exactement."""
        r_ptf = ptf_simple.calculer_rendements(rendements_test)
        w = ptf_simple.vecteur_poids
        r_expected = rendements_test[ptf_simple.tickers].values @ w
        np.testing.assert_allclose(r_ptf.values, r_expected, rtol=1e-10)

    def test_actif_manquant_leve_erreur(self, ptf_simple):
        """Un actif absent des rendements doit lever KeyError."""
        rendements_incomplets = pd.DataFrame({"SPY": [0.01], "AGG": [0.005]})
        with pytest.raises(KeyError):
            ptf_simple.calculer_rendements(rendements_incomplets)

    def test_pnl_absolu(self, ptf_simple, rendements_test):
        """PnL = rendement * valeur_initiale."""
        r_ptf = ptf_simple.calculer_rendements(rendements_test)
        pnl   = ptf_simple.pnl_absolu(r_ptf)
        np.testing.assert_allclose(pnl.values, r_ptf.values * ptf_simple.valeur_initiale)


# =============================================================================
# Tests statistiques
# =============================================================================

class TestStatistiquesPortfolio:

    def test_statistiques_colonnes(self, ptf_simple, rendements_test):
        """Les statistiques doivent contenir les colonnes attendues."""
        stats = ptf_simple.statistiques_actifs(rendements_test)
        assert "Rendement moyen (j)" in stats.columns
        assert "Volatilité (j)" in stats.columns
        assert "Skewness" in stats.columns

    def test_statistiques_index_tickers(self, ptf_simple, rendements_test):
        """L'index des statistiques doit être les tickers."""
        stats = ptf_simple.statistiques_actifs(rendements_test)
        assert set(stats.index) == set(ptf_simple.tickers)

    def test_stats_portfolio_coherentes(self, ptf_simple, rendements_test):
        """Les statistiques du portefeuille agrégé doivent être cohérentes."""
        r_ptf  = ptf_simple.calculer_rendements(rendements_test)
        stats  = ptf_simple.statistiques_portfolio(r_ptf)
        assert stats["n_observations"] == len(rendements_test)
        assert stats["volatilite_journaliere"] > 0
        assert abs(stats["rendement_annualise"] - stats["rendement_moyen_journalier"] * 252) < 1e-9


# =============================================================================
# Tests factory
# =============================================================================

class TestFactory:

    def test_portfolio_depuis_config(self):
        config = {
            "portfolio": {
                "name": "Test Config",
                "actifs": {"A": 0.6, "B": 0.4},
                "valeur_initiale": 500_000,
                "currency": "EUR",
            }
        }
        ptf = portfolio_depuis_config(config)
        assert ptf.nom == "Test Config"
        assert ptf.valeur_initiale == 500_000
        assert ptf.poids["A"] == 0.6

    def test_portfolio_equipondere(self):
        tickers = ["X", "Y", "Z"]
        ptf = portfolio_equipondere(tickers)
        for t in tickers:
            assert abs(ptf.poids[t] - 1/3) < 1e-9
        assert abs(sum(ptf.poids.values()) - 1.0) < 1e-9
