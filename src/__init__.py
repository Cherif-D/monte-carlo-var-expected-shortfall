"""
src/ — Moteur Monte Carlo de VaR et Expected Shortfall
=======================================================
Package principal du projet. Contient tous les modules métier.

Modules
-------
utils         : Fonctions utilitaires (logging, config, seeds)
data_loader   : Chargement et validation des données de prix
portfolio     : Représentation et valorisation du portefeuille
returns_model : Calibration des paramètres statistiques des rendements
simulation    : Moteur de simulation Monte Carlo (GBM, Cholesky)
risk_metrics  : Calcul de VaR et ES (historique, paramétrique, MC)
sensitivity   : Analyses de sensibilité paramétriques
plots         : Génération de tous les graphiques
report        : Génération du rapport final Markdown
"""

__version__ = "1.0.0"
__author__  = "Projet M1 Finance Quantitative"
