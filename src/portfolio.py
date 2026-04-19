"""
portfolio.py — Représentation et valorisation du portefeuille
=============================================================
Ce module définit la classe Portfolio, objet central du projet.

Un portefeuille est défini par :
  - une liste d'actifs (tickers),
  - des pondérations (poids),
  - une valeur nominale initiale.

La classe Portfolio est responsable de :
  - calculer les rendements agrégés du portefeuille,
  - calculer le P&L (profit and loss),
  - fournir des statistiques descriptives,
  - supporter la comparaison entre plusieurs allocations.

Hypothèses importantes
----------------------
  - Portefeuille statique : les poids ne sont PAS rééquilibrés au cours du temps.
    (hypothèse simplificatrice standard pour la VaR de court terme)
  - Valorisation en devises homogènes (EUR dans notre config par défaut).
  - Rendements supposés être les log-rendements des actifs.
  - La pondération s'applique sur la valeur de marché, pas sur le nombre de titres.
"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.utils import verifier_poids

logger = logging.getLogger("var_mc.portfolio")


# =============================================================================
# Classe principale
# =============================================================================

@dataclass
class Portfolio:
    """
    Représentation d'un portefeuille multi-actifs.

    Attributs
    ---------
    nom : str
        Nom descriptif du portefeuille.
    poids : dict[str, float]
        Dictionnaire {ticker: poids}. Les poids doivent sommer à 1.
    valeur_initiale : float
        Valeur nominale du portefeuille en devise de référence (EUR).
    devise : str
        Devise de référence (informatif).
    """

    nom: str
    poids: dict[str, float]
    valeur_initiale: float = 1_000_000.0
    devise: str = "EUR"

    # Attributs calculés (non fournis à la construction)
    _rendements_actifs: pd.DataFrame = field(default=None, repr=False, init=False)
    _rendements_portfolio: pd.Series  = field(default=None, repr=False, init=False)

    def __post_init__(self):
        """Validation automatique après construction."""
        verifier_poids(self.poids)
        logger.info(
            f"Portefeuille '{self.nom}' initialisé : "
            f"{len(self.poids)} actifs, "
            f"valeur = {self.valeur_initiale:,.0f} {self.devise}"
        )

    # ------------------------------------------------------------------
    # Propriétés
    # ------------------------------------------------------------------

    @property
    def tickers(self) -> list[str]:
        """Liste ordonnée des tickers du portefeuille."""
        return list(self.poids.keys())

    @property
    def vecteur_poids(self) -> np.ndarray:
        """Poids sous forme de vecteur numpy (même ordre que self.tickers)."""
        return np.array([self.poids[t] for t in self.tickers])

    # ------------------------------------------------------------------
    # Calcul des rendements
    # ------------------------------------------------------------------

    def calculer_rendements(self, rendements_actifs: pd.DataFrame) -> pd.Series:
        """
        Calcule les rendements agrégés du portefeuille.

        Méthode : combinaison linéaire des rendements individuels,
        pondérée par les poids du portefeuille.

        Formule :
            r_p,t = sum_i (w_i * r_i,t)

        où w_i est le poids de l'actif i et r_i,t son rendement au temps t.

        Hypothèse : cette formule est exacte pour les rendements simples
        et une bonne approximation pour les log-rendements sur des horizons courts.

        Paramètres
        ----------
        rendements_actifs : pd.DataFrame
            DataFrame de rendements (lignes = dates, colonnes = tickers).

        Retourne
        --------
        pd.Series
            Série des rendements quotidiens du portefeuille.
        """
        # Vérification de la présence de tous les actifs
        manquants = [t for t in self.tickers if t not in rendements_actifs.columns]
        if manquants:
            raise KeyError(
                f"Actifs manquants dans les rendements : {manquants}. "
                "Vérifiez la cohérence entre config.yaml et les données."
            )

        # Sélectionner les colonnes dans le bon ordre
        r = rendements_actifs[self.tickers]
        w = self.vecteur_poids

        # Combinaison linéaire : matrice (T x n) @ vecteur (n,) = vecteur (T,)
        r_portfolio = r.values @ w
        serie = pd.Series(r_portfolio, index=r.index, name=self.nom)

        self._rendements_actifs   = r
        self._rendements_portfolio = serie

        logger.debug(
            f"Rendements portfolio calculés : "
            f"moyenne={serie.mean():.5f}, vol={serie.std():.5f}"
        )
        return serie

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    def pnl_absolu(self, rendements_portfolio: pd.Series) -> pd.Series:
        """
        Convertit les rendements en P&L absolus (en devise).

        Formule : PnL_t = r_p,t * V_0

        où V_0 est la valeur initiale du portefeuille.

        Note : cette approximation est valide pour des horizons courts
        (1 à 10 jours) où les rendements sont faibles. Pour des horizons
        plus longs, il faudrait utiliser la valeur de marché courante.

        Paramètres
        ----------
        rendements_portfolio : pd.Series
            Rendements du portefeuille.

        Retourne
        --------
        pd.Series
            P&L en unités de devise (EUR).
        """
        return rendements_portfolio * self.valeur_initiale

    # ------------------------------------------------------------------
    # Statistiques descriptives
    # ------------------------------------------------------------------

    def statistiques_actifs(
        self,
        rendements_actifs: pd.DataFrame,
        annualisation: int = 252,
    ) -> pd.DataFrame:
        """
        Calcule les statistiques descriptives des rendements par actif.

        Paramètres
        ----------
        rendements_actifs : pd.DataFrame
            Rendements journaliers.
        annualisation : int
            Nombre de jours ouvrés par an (252 par convention).

        Retourne
        --------
        pd.DataFrame
            Tableau récapitulatif (actifs en lignes, stats en colonnes).
        """
        r = rendements_actifs[self.tickers]

        stats = pd.DataFrame(index=self.tickers)
        stats["Rendement moyen (j)"]  = r.mean()
        stats["Volatilité (j)"]        = r.std()
        stats["Rendement moyen (a)"]  = r.mean() * annualisation
        stats["Volatilité (a)"]        = r.std() * np.sqrt(annualisation)
        stats["Skewness"]              = r.skew()
        stats["Kurtosis exc."]         = r.kurtosis()   # kurtosis excess (0 = normale)
        stats["Poids (%)"]             = [self.poids[t] * 100 for t in self.tickers]
        stats["Exposition (EUR)"]      = [
            self.poids[t] * self.valeur_initiale for t in self.tickers
        ]

        return stats.round(6)

    def statistiques_portfolio(
        self,
        rendements_portfolio: pd.Series,
        annualisation: int = 252,
    ) -> dict:
        """
        Calcule les statistiques descriptives du portefeuille agrégé.

        Retourne
        --------
        dict
            Dictionnaire de statistiques clés.
        """
        r = rendements_portfolio
        stats = {
            "rendement_moyen_journalier":  float(r.mean()),
            "volatilite_journaliere":      float(r.std()),
            "rendement_annualise":         float(r.mean() * annualisation),
            "volatilite_annualisee":       float(r.std() * np.sqrt(annualisation)),
            "skewness":                    float(r.skew()),
            "kurtosis_exces":              float(r.kurtosis()),
            "min":                         float(r.min()),
            "max":                         float(r.max()),
            "n_observations":              len(r),
            "sharpe_empirique":            float(
                r.mean() / r.std() * np.sqrt(annualisation)
                if r.std() > 0 else np.nan
            ),
        }
        return stats

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------

    def afficher_composition(self) -> str:
        """Retourne une représentation textuelle de la composition."""
        lignes = [
            f"\n{'='*55}",
            f"  Portefeuille : {self.nom}",
            f"  Valeur initiale : {self.valeur_initiale:>15,.0f} {self.devise}",
            f"{'='*55}",
            f"  {'Actif':<12} {'Poids':>8}  {'Exposition':>15}",
            f"  {'-'*40}",
        ]
        for t, w in self.poids.items():
            expo = w * self.valeur_initiale
            lignes.append(f"  {t:<12} {w*100:>7.1f}%  {expo:>15,.0f} {self.devise}")
        lignes.append(f"  {'-'*40}")
        lignes.append(
            f"  {'TOTAL':<12} {100.0:>7.1f}%  {self.valeur_initiale:>15,.0f} {self.devise}"
        )
        lignes.append(f"{'='*55}\n")
        return "\n".join(lignes)


# =============================================================================
# Factory depuis config
# =============================================================================

def portfolio_depuis_config(config: dict) -> Portfolio:
    """
    Construit un objet Portfolio à partir de la configuration.

    Paramètres
    ----------
    config : dict
        Configuration complète du projet.

    Retourne
    --------
    Portfolio
    """
    cfg_ptf = config["portfolio"]
    return Portfolio(
        nom=cfg_ptf["name"],
        poids=cfg_ptf["actifs"],
        valeur_initiale=cfg_ptf["valeur_initiale"],
        devise=cfg_ptf["currency"],
    )


def portfolio_equipondere(tickers: list[str], **kwargs) -> Portfolio:
    """
    Crée un portefeuille équipondéré (benchmark de comparaison).

    Paramètres
    ----------
    tickers : list[str]
        Liste des actifs.
    **kwargs : dict
        Arguments supplémentaires passés à Portfolio (nom, valeur_initiale...).

    Retourne
    --------
    Portfolio
    """
    n = len(tickers)
    poids = {t: 1.0 / n for t in tickers}
    return Portfolio(
        nom=kwargs.get("nom", "Portefeuille Équipondéré"),
        poids=poids,
        valeur_initiale=kwargs.get("valeur_initiale", 1_000_000.0),
        devise=kwargs.get("devise", "EUR"),
    )
