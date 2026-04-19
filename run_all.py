"""
run_all.py — Point d'entrée unique du pipeline
================================================
Ce script orchestre l'intégralité du projet dans l'ordre suivant :

  Étape 1  : Chargement de la configuration
  Étape 2  : Initialisation (logger, seed, dossiers de sortie)
  Étape 3  : Chargement des données de prix
  Étape 4  : Construction du portefeuille
  Étape 5  : Calibration des paramètres des rendements
  Étape 6  : Calcul de la VaR et ES historique
  Étape 7  : Calcul de la VaR et ES paramétrique
  Étape 8  : Simulation Monte Carlo
  Étape 9  : Calcul de la VaR et ES Monte Carlo
  Étape 10 : Tableau comparatif des méthodes
  Étape 11 : Analyses de sensibilité
  Étape 12 : Attribution marginale du risque
  Étape 13 : Backtesting simplifié
  Étape 14 : Génération des figures
  Étape 15 : Sauvegarde des tableaux CSV
  Étape 16 : Génération du rapport final

Utilisation
-----------
    python run_all.py
    python run_all.py --config config.yaml   # config alternative

Reproductibilité
----------------
Toutes les simulations utilisent une graine fixe (config.yaml > simulation > seed).
Deux exécutions successives avec la même configuration produisent exactement
les mêmes résultats numériques.
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Ajout du répertoire racine au PYTHONPATH (si lancé depuis un sous-dossier)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.utils import (
    charger_config,
    initialiser_logger,
    fixer_seed,
    creer_dossiers_sortie,
    chemin_figure,
    chemin_table,
)
from src.data_loader import charger_prix, calculer_rendements_log
from src.portfolio import portfolio_depuis_config, portfolio_equipondere
from src.returns_model import calibrer_parametres, tester_normalite
from src.simulation import simuler_monte_carlo
from src.risk_metrics import (
    var_es_historique,
    var_es_parametrique,
    var_es_monte_carlo,
    calculer_toutes_mesures,
    backtester_var,
    attribution_marginale_risque,
)
from src.sensitivity import (
    sensibilite_volatilite,
    sensibilite_correlation,
    sensibilite_horizon,
    sensibilite_niveau_confiance,
    comparer_portefeuilles,
)
from src import plots
from src.report import generer_rapport


# =============================================================================
# Argument parsing
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Moteur Monte Carlo de VaR et Expected Shortfall"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Chemin vers le fichier de configuration YAML (défaut: config.yaml)",
    )
    return parser.parse_args()


# =============================================================================
# Pipeline principal
# =============================================================================

def main():
    t_debut = time.time()

    # -------------------------------------------------------------------------
    # Étape 1 : Configuration
    # -------------------------------------------------------------------------
    args = parse_args()
    config = charger_config(args.config)

    # -------------------------------------------------------------------------
    # Étape 2 : Initialisation
    # -------------------------------------------------------------------------
    creer_dossiers_sortie(config)
    logger = initialiser_logger(
        nom="var_mc",
        niveau=config["logging"]["niveau"],
        fichier_log=config["logging"]["fichier_log"],
        afficher_console=config["logging"]["afficher_console"],
    )
    seed = config["simulation"]["seed"]
    fixer_seed(seed)
    logger.info("=" * 65)
    logger.info("  MOTEUR MONTE CARLO — VaR / ES — DÉMARRAGE DU PIPELINE")
    logger.info("=" * 65)
    logger.info(f"Configuration chargée depuis : {args.config}")
    logger.info(f"Portefeuille : {config['portfolio']['name']}")
    logger.info(f"Simulations  : {config['simulation']['n_simulations']:,}")
    logger.info(f"Seed         : {seed}")

    dpi = config["outputs"]["dpi"]

    # -------------------------------------------------------------------------
    # Étape 3 : Données
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 3 : Chargement des données")
    prix = charger_prix(config)
    rendements = calculer_rendements_log(prix)

    # -------------------------------------------------------------------------
    # Étape 4 : Portefeuille
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 4 : Construction du portefeuille")
    ptf = portfolio_depuis_config(config)
    print(ptf.afficher_composition())

    rendements_ptf = ptf.calculer_rendements(rendements)
    pnl_historique = ptf.pnl_absolu(rendements_ptf).values
    stats_actifs   = ptf.statistiques_actifs(rendements)
    stats_ptf      = ptf.statistiques_portfolio(rendements_ptf)

    logger.info(f"Rendement annualisé : {stats_ptf['rendement_annualise']*100:.2f}%")
    logger.info(f"Volatilité annualisée : {stats_ptf['volatilite_annualisee']*100:.2f}%")

    # -------------------------------------------------------------------------
    # Étape 5 : Calibration
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 5 : Calibration des paramètres")
    params = calibrer_parametres(rendements, tickers=ptf.tickers)

    # Test de normalité (informatif)
    df_normalite = tester_normalite(rendements[ptf.tickers])
    logger.info("Tests de normalité (Jarque-Bera) :\n" + df_normalite.to_string())

    # Paramètres du portefeuille agrégé
    poids = ptf.vecteur_poids
    mu_ptf    = float(poids @ params.mu)
    sigma_ptf = float(np.sqrt(poids @ params.cov @ poids))
    horizon   = config["simulation"]["horizon_jours"]
    niveaux   = config["risk"]["niveaux_confiance"]

    # -------------------------------------------------------------------------
    # Étape 6 : VaR historique
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 6 : VaR et ES historique")
    resultats_hist = {}
    for alpha in niveaux:
        resultats_hist[alpha] = var_es_historique(
            pnl_historique, alpha, ptf.valeur_initiale, horizon
        )
        logger.info(
            f"  VaR historique {alpha*100:.0f}% ({horizon}j) = "
            f"{resultats_hist[alpha].var:>10,.0f} EUR  |  "
            f"ES = {resultats_hist[alpha].es:>10,.0f} EUR"
        )

    # -------------------------------------------------------------------------
    # Étape 7 : VaR paramétrique
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 7 : VaR et ES paramétrique (gaussienne)")
    resultats_param = {}
    for alpha in niveaux:
        resultats_param[alpha] = var_es_parametrique(
            mu_ptf, sigma_ptf, ptf.valeur_initiale, alpha, horizon
        )
        logger.info(
            f"  VaR param.    {alpha*100:.0f}% ({horizon}j) = "
            f"{resultats_param[alpha].var:>10,.0f} EUR  |  "
            f"ES = {resultats_param[alpha].es:>10,.0f} EUR"
        )

    # -------------------------------------------------------------------------
    # Étape 8 : Simulation Monte Carlo
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 8 : Simulation Monte Carlo")
    n_sim    = config["simulation"]["n_simulations"]
    distrib  = config["simulation"]["distribution"]
    df_stud  = config["simulation"]["student_df"]

    sim_mc = simuler_monte_carlo(
        params=params,
        poids=poids,
        valeur_initiale=ptf.valeur_initiale,
        n_simulations=n_sim,
        horizon_jours=horizon,
        distribution=distrib,
        student_df=df_stud,
        seed=seed,
    )
    stats_sim = sim_mc.statistiques()
    logger.info(f"  P&L moyen simulé  : {stats_sim['mean_pnl']:>10,.0f} EUR")
    logger.info(f"  P&L std simulé    : {stats_sim['std_pnl']:>10,.0f} EUR")
    logger.info(f"  P&L min simulé    : {stats_sim['min_pnl']:>10,.0f} EUR")
    logger.info(f"  Skewness          : {stats_sim['skewness']:>10.4f}")
    logger.info(f"  Kurtosis (excès)  : {stats_sim['kurtosis']:>10.4f}")

    # -------------------------------------------------------------------------
    # Étape 9 : VaR et ES Monte Carlo
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 9 : VaR et ES Monte Carlo")
    resultats_mc = {}
    for alpha in niveaux:
        resultats_mc[alpha] = var_es_monte_carlo(
            sim_mc, ptf.valeur_initiale, alpha
        )
        logger.info(
            f"  VaR MC          {alpha*100:.0f}% ({horizon}j) = "
            f"{resultats_mc[alpha].var:>10,.0f} EUR  |  "
            f"ES = {resultats_mc[alpha].es:>10,.0f} EUR"
        )

    # -------------------------------------------------------------------------
    # Étape 10 : Tableau comparatif
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 10 : Tableau comparatif des méthodes")
    df_comparaison = calculer_toutes_mesures(
        pnl_historique=pnl_historique,
        mu_portfolio=mu_ptf,
        sigma_portfolio=sigma_ptf,
        resultats_mc=sim_mc,
        valeur_initiale=ptf.valeur_initiale,
        niveaux_confiance=niveaux,
        horizon_jours=horizon,
    )
    print("\n" + "=" * 65)
    print("  TABLEAU COMPARATIF VaR / ES")
    print("=" * 65)
    print(df_comparaison.to_string(index=False))
    print("=" * 65 + "\n")

    if config["outputs"]["sauvegarder_csv"]:
        df_comparaison.to_csv(chemin_table("comparaison_var_es", config), index=False)

    # -------------------------------------------------------------------------
    # Étape 11 : Analyses de sensibilité
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 11 : Analyses de sensibilité")

    df_sensib_vol = sensibilite_volatilite(
        params_base=params,
        poids=poids,
        valeur_initiale=ptf.valeur_initiale,
        facteurs_vol=config["sensitivity"]["chocs_volatilite"],
        niveaux_confiance=niveaux,
        n_simulations=n_sim,
        horizon_jours=horizon,
        seed=seed,
    )

    df_sensib_corr = sensibilite_correlation(
        params_base=params,
        poids=poids,
        valeur_initiale=ptf.valeur_initiale,
        facteurs_corr=config["sensitivity"]["chocs_correlation"],
        niveaux_confiance=niveaux,
        n_simulations=n_sim,
        horizon_jours=horizon,
        seed=seed,
    )

    df_sensib_horiz = sensibilite_horizon(
        params_base=params,
        poids=poids,
        valeur_initiale=ptf.valeur_initiale,
        horizons=config["sensitivity"]["horizons_jours"],
        niveaux_confiance=niveaux,
        n_simulations=n_sim,
        seed=seed,
    )

    df_sensib_conf = sensibilite_niveau_confiance(
        resultats_mc=sim_mc,
        pnl_historique=pnl_historique,
        mu_portfolio=mu_ptf,
        sigma_portfolio=sigma_ptf,
        valeur_initiale=ptf.valeur_initiale,
        niveaux=config["sensitivity"]["niveaux_confiance_range"],
        horizon_jours=horizon,
    )

    # Comparaison équipondéré vs. utilisateur
    ptf_eq   = portfolio_equipondere(ptf.tickers, valeur_initiale=ptf.valeur_initiale)
    poids_eq = ptf_eq.vecteur_poids
    df_comp_ptf = comparer_portefeuilles(
        params_base=params,
        poids_user=poids,
        poids_eq=poids_eq,
        valeur_initiale=ptf.valeur_initiale,
        niveaux_confiance=niveaux,
        n_simulations=n_sim,
        horizon_jours=horizon,
        seed=seed,
    )

    # Sauvegarde CSV
    if config["outputs"]["sauvegarder_csv"]:
        df_sensib_vol.to_csv(chemin_table("sensibilite_volatilite", config), index=False)
        df_sensib_corr.to_csv(chemin_table("sensibilite_correlation", config), index=False)
        df_sensib_horiz.to_csv(chemin_table("sensibilite_horizon", config), index=False)
        df_sensib_conf.to_csv(chemin_table("sensibilite_confiance", config), index=False)
        df_comp_ptf.to_csv(chemin_table("comparaison_portefeuilles", config), index=False)

    # -------------------------------------------------------------------------
    # Étape 12 : Attribution marginale du risque
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 12 : Attribution marginale du risque")
    attr = attribution_marginale_risque(
        rendements_actifs=sim_mc.rendements_actifs,
        poids=poids,
        valeur_initiale=ptf.valeur_initiale,
        niveau_confiance=0.99,
    )
    df_attr = pd.DataFrame({
        "Actif":                ptf.tickers,
        "Poids (%)":            (poids * 100).round(1),
        "Contrib. marginale":   attr["contrib_marginale"].round(2),
        "Contrib. totale (EUR)": attr["contrib_totale"].round(0),
        "Contrib. totale (%)":  attr["contrib_pct"].round(2),
    })
    print("\nAttribution marginale du risque (VaR 99%) :")
    print(df_attr.to_string(index=False))
    if config["outputs"]["sauvegarder_csv"]:
        df_attr.to_csv(chemin_table("attribution_risque", config), index=False)

    # -------------------------------------------------------------------------
    # Étape 13 : Backtesting
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 13 : Backtesting de la VaR")
    # On utilise une VaR constante calibrée sur l'échantillon entier (in-sample)
    # Dans un contexte réel, on utiliserait une fenêtre glissante (out-of-sample)
    resultats_bt = {}
    for alpha in niveaux:
        var_constante = np.full(len(pnl_historique), resultats_hist[alpha].var)
        resultats_bt[alpha] = backtester_var(pnl_historique, var_constante, alpha)

    # -------------------------------------------------------------------------
    # Étape 14 : Figures
    # -------------------------------------------------------------------------
    logger.info("\n>>> Étape 14 : Génération des figures")

    # Figure 1 : Distribution des P&L
    for alpha in niveaux:
        plots.tracer_distribution_pnl(
            pnl=sim_mc.pnl,
            var_hist=resultats_hist[alpha].var,
            var_param=resultats_param[alpha].var,
            var_mc=resultats_mc[alpha].var,
            es_mc=resultats_mc[alpha].es,
            niveau_confiance=alpha,
            valeur_initiale=ptf.valeur_initiale,
            chemin=chemin_figure(f"distribution_pnl_{int(alpha*100)}pct", config),
            dpi=dpi,
        )

    # Figure 2 : Heatmap corrélation
    plots.tracer_heatmap_correlation(
        corr=params.corr,
        tickers=ptf.tickers,
        chemin=chemin_figure("heatmap_correlation", config),
        dpi=dpi,
    )

    # Figure 3 : Évolution des prix
    plots.tracer_evolution_prix(
        prix=prix,
        chemin=chemin_figure("evolution_prix", config),
        dpi=dpi,
    )

    # Figure 4 : Comparaison méthodes
    plots.tracer_comparaison_methodes(
        df_resultats=df_comparaison,
        chemin=chemin_figure("comparaison_methodes", config),
        dpi=dpi,
    )

    # Figure 5 : Sensibilité volatilité
    plots.tracer_sensibilite_volatilite(
        df_sensib=df_sensib_vol,
        chemin=chemin_figure("sensibilite_volatilite", config),
        dpi=dpi,
    )

    # Figure 6 : Sensibilité corrélation
    plots.tracer_sensibilite_correlation(
        df_sensib=df_sensib_corr,
        chemin=chemin_figure("sensibilite_correlation", config),
        dpi=dpi,
    )

    # Figure 7 : Sensibilité horizon
    plots.tracer_sensibilite_horizon(
        df_sensib=df_sensib_horiz,
        chemin=chemin_figure("sensibilite_horizon", config),
        dpi=dpi,
    )

    # Figure 8 : Sensibilité niveau de confiance
    plots.tracer_sensibilite_confiance(
        df_sensib=df_sensib_conf,
        chemin=chemin_figure("sensibilite_confiance", config),
        dpi=dpi,
    )

    # Figure 9 : Rendements historiques
    plots.tracer_rendements_portfolio(
        rendements=rendements_ptf,
        var_95=resultats_hist[0.95].var,
        var_99=resultats_hist[0.99].var,
        valeur_initiale=ptf.valeur_initiale,
        chemin=chemin_figure("rendements_portfolio", config),
        dpi=dpi,
    )

    # Figure 10 : Attribution risque
    plots.tracer_attribution_risque(
        tickers=ptf.tickers,
        contrib_pct=attr["contrib_pct"],
        poids=poids,
        chemin=chemin_figure("attribution_risque", config),
        dpi=dpi,
    )

    # -------------------------------------------------------------------------
    # Étape 15 : Tableaux complémentaires
    # -------------------------------------------------------------------------
    if config["outputs"]["sauvegarder_csv"]:
        stats_actifs.to_csv(chemin_table("statistiques_actifs", config))
        params.to_dataframe().to_csv(chemin_table("parametres_calibres", config))
        df_normalite.to_csv(chemin_table("tests_normalite", config))
        df_attr.to_csv(chemin_table("attribution_risque", config), index=False)

    # -------------------------------------------------------------------------
    # Étape 16 : Rapport final
    # -------------------------------------------------------------------------
    if config["outputs"]["generer_rapport"]:
        logger.info("\n>>> Étape 16 : Génération du rapport final")
        chemin_rapport = Path(config["outputs"]["dossier_reports"]) / "final_report.md"
        generer_rapport(
            config=config,
            stats_actifs=stats_actifs,
            params_df=params.to_dataframe(),
            corr=params.corr,
            tickers=ptf.tickers,
            df_resultats=df_comparaison,
            df_vol=df_sensib_vol,
            df_corr=df_sensib_corr,
            df_horizon=df_sensib_horiz,
            resultats_backtesting=resultats_bt.get(0.99),
            chemin=chemin_rapport,
        )

    # -------------------------------------------------------------------------
    # Résumé final
    # -------------------------------------------------------------------------
    t_fin = time.time()
    duree = t_fin - t_debut
    logger.info("\n" + "=" * 65)
    logger.info("  PIPELINE TERMINÉ")
    logger.info(f"  Durée d'exécution : {duree:.1f} secondes")
    logger.info(f"  Figures    -> {config['outputs']['dossier_figures']}/")
    logger.info(f"  Tableaux   -> {config['outputs']['dossier_tables']}/")
    logger.info(f"  Rapport    -> {config['outputs']['dossier_reports']}/final_report.md")
    logger.info(f"  Log        -> {config['logging']['fichier_log']}")
    logger.info("=" * 65)

    return {
        "comparaison": df_comparaison,
        "sensibilite_vol": df_sensib_vol,
        "sensibilite_corr": df_sensib_corr,
        "sensibilite_horiz": df_sensib_horiz,
        "attribution": df_attr,
        "backtesting": resultats_bt,
    }


if __name__ == "__main__":
    main()
