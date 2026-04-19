"""
plots.py — Génération des graphiques
=====================================
Ce module centralise toutes les visualisations du projet.
Chaque fonction génère et sauvegarde une figure matplotlib.

Figures produites
-----------------
1. distribution_pnl        : Histogramme/densité du P&L simulé avec VaR/ES
2. heatmap_correlation      : Heatmap de la matrice de corrélation
3. evolution_prix           : Évolution des prix normalisés des actifs
4. comparaison_methodes     : VaR/ES comparées entre les trois méthodes
5. sensibilite_volatilite   : VaR vs facteur de volatilité
6. sensibilite_correlation  : VaR vs facteur de corrélation
7. sensibilite_horizon      : VaR vs horizon (illustration règle sqrt)
8. sensibilite_confiance    : VaR vs niveau de confiance
9. rendements_historiques   : Série temporelle des rendements du portefeuille
10. attribution_risque      : Contribution marginale par actif

Style global
------------
On utilise uniquement matplotlib (pas de seaborn) pour minimiser les
dépendances. Le style est sobre et lisible, adapté à un rapport académique.
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Backend non-interactif (pour scripts sans écran)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

logger = logging.getLogger("var_mc.plots")

# Palette de couleurs sobre (accessible daltonisme)
COULEURS = {
    "primaire":    "#1f4e79",   # Bleu marine
    "secondaire":  "#c00000",   # Rouge foncé
    "tertiaire":   "#2e7d32",   # Vert foncé
    "accent":      "#e65100",   # Orange
    "neutre":      "#546e7a",   # Gris-bleu
    "fond":        "#f5f5f5",   # Fond clair
}


def _style_base(fig: plt.Figure, ax: plt.Axes, titre: str) -> None:
    """Applique un style de base cohérent à tous les graphiques."""
    ax.set_title(titre, fontsize=13, fontweight="bold", pad=12, color="#1a1a1a")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.set_facecolor(COULEURS["fond"])
    fig.patch.set_facecolor("white")


def sauvegarder(fig: plt.Figure, chemin: Path, dpi: int = 150) -> None:
    """Sauvegarde et ferme une figure."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(chemin, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    logger.info(f"Figure sauvegardée : {chemin}")


# =============================================================================
# 1. Distribution des P&L avec VaR et ES
# =============================================================================

def tracer_distribution_pnl(
    pnl: np.ndarray,
    var_hist: float,
    var_param: float,
    var_mc: float,
    es_mc: float,
    niveau_confiance: float,
    valeur_initiale: float,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    Histogramme de la distribution des P&L simulés avec les seuils VaR/ES.

    Lecture du graphique
    --------------------
    - Les barres représentent la fréquence relative des P&L simulés.
    - La zone rouge (à gauche) représente les scénarios de perte dépassant la VaR.
    - Les lignes verticales indiquent la VaR selon chaque méthode.
    - La zone hachurée orange indique l'ES (espérance des pertes extrêmes).
    """
    alpha_pct = int(niveau_confiance * 100)
    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogramme
    n_bins = min(200, len(pnl) // 100)
    ax.hist(
        pnl,
        bins=n_bins,
        density=True,
        color=COULEURS["primaire"],
        alpha=0.55,
        label="Distribution P&L (Monte Carlo)",
        zorder=2,
    )

    # Zone de perte extrême (gauche de la VaR MC)
    limite = -var_mc
    pnl_min = pnl.min()
    ax.axvspan(pnl_min, limite, alpha=0.15, color=COULEURS["secondaire"], zorder=1,
               label=f"Zone perte > VaR MC ({alpha_pct}%)")

    # Lignes VaR
    ax.axvline(-var_hist,  color=COULEURS["tertiaire"],  ls="--", lw=2.0,
               label=f"VaR Historique  : {var_hist:>8,.0f} EUR")
    ax.axvline(-var_param, color=COULEURS["accent"],     ls="-.", lw=2.0,
               label=f"VaR Paramétrique: {var_param:>8,.0f} EUR")
    ax.axvline(-var_mc,    color=COULEURS["secondaire"], ls="-",  lw=2.5,
               label=f"VaR Monte Carlo : {var_mc:>8,.0f} EUR")
    ax.axvline(-es_mc,     color="#6a1a4c",              ls=":",  lw=2.5,
               label=f"ES Monte Carlo  : {es_mc:>8,.0f} EUR")

    # Annotation
    pct_loss = (pnl < -var_mc).mean() * 100
    ax.text(
        -var_mc * 1.02, ax.get_ylim()[1] * 0.5,
        f"α={alpha_pct}%\n{pct_loss:.1f}% scénarios\n< VaR",
        fontsize=8, color=COULEURS["secondaire"], ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
    )

    ax.set_xlabel(f"P&L en EUR (portefeuille {valeur_initiale/1e6:.0f}M EUR)", fontsize=10)
    ax.set_ylabel("Densité", fontsize=10)
    ax.legend(fontsize=9, loc="upper left", framealpha=0.85)
    _style_base(fig, ax, f"Distribution des P&L — VaR et ES à {alpha_pct}%")
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 2. Heatmap de corrélation
# =============================================================================

def tracer_heatmap_correlation(
    corr: np.ndarray,
    tickers: list[str],
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    Heatmap de la matrice de corrélation.

    Lecture
    -------
    - Couleurs chaudes (rouge) : corrélations positives élevées → faible diversification.
    - Couleurs froides (bleu) : corrélations négatives → couverture naturelle.
    - Les valeurs affichées dans chaque cellule sont les coefficients de Pearson.
    """
    n = len(tickers)
    fig, ax = plt.subplots(figsize=(7, 6))

    # Colormap centrée sur 0
    cmap = plt.cm.RdBu_r
    im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, shrink=0.85, label="Corrélation de Pearson")

    # Annotations numériques
    for i in range(n):
        for j in range(n):
            val = corr[i, j]
            couleur_texte = "white" if abs(val) > 0.6 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=10, color=couleur_texte, fontweight="bold")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(tickers, fontsize=10, rotation=20)
    ax.set_yticklabels(tickers, fontsize=10)
    _style_base(fig, ax, "Matrice de corrélation des rendements")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 3. Évolution des prix normalisés
# =============================================================================

def tracer_evolution_prix(
    prix: pd.DataFrame,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    Évolution des prix normalisés (base 100 au départ).

    Lecture
    -------
    Permet de comparer visuellement les performances relatives des actifs.
    Un actif à 120 a gagné 20% depuis le début de la période.
    """
    prix_norm = prix / prix.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(12, 5))

    couleurs_lignes = plt.cm.tab10(np.linspace(0, 0.8, len(prix.columns)))
    for col, couleur in zip(prix.columns, couleurs_lignes):
        ax.plot(prix_norm.index, prix_norm[col], label=col, lw=1.8, color=couleur)

    ax.axhline(100, color="gray", ls="--", lw=1, alpha=0.5, label="Base 100")
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Valeur (base 100)", fontsize=10)
    ax.legend(fontsize=9, loc="upper left")
    _style_base(fig, ax, "Évolution des actifs du portefeuille (base 100)")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 4. Comparaison des méthodes VaR/ES
# =============================================================================

def tracer_comparaison_methodes(
    df_resultats: pd.DataFrame,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    Graphique en barres groupées comparant VaR et ES par méthode et niveau de confiance.
    """
    methodes = df_resultats["Méthode"].unique()
    niveaux  = df_resultats["Niveau confiance"].unique()
    n_niveaux = len(niveaux)

    fig, axes = plt.subplots(1, n_niveaux, figsize=(6 * n_niveaux, 6), sharey=False)
    if n_niveaux == 1:
        axes = [axes]

    couleurs_methodes = {
        "historique":   COULEURS["tertiaire"],
        "parametrique": COULEURS["accent"],
        "monte_carlo":  COULEURS["secondaire"],
    }

    for idx_ax, (ax, niveau) in enumerate(zip(axes, niveaux)):
        data_n = df_resultats[df_resultats["Niveau confiance"] == niveau]
        x      = np.arange(len(data_n))
        width  = 0.35

        bars_var = ax.bar(
            x - width/2, data_n["VaR (EUR)"], width,
            label="VaR", color=[couleurs_methodes.get(m.lower(), COULEURS["primaire"])
                                  for m in data_n["Méthode"]],
            alpha=0.85, edgecolor="white",
        )
        bars_es = ax.bar(
            x + width/2, data_n["ES (EUR)"], width,
            label="ES", color=[couleurs_methodes.get(m.lower(), COULEURS["primaire"])
                                 for m in data_n["Méthode"]],
            alpha=0.45, edgecolor="white", hatch="///",
        )

        ax.set_xticks(x)
        ax.set_xticklabels(data_n["Méthode"], fontsize=9, rotation=10)
        ax.set_ylabel("Perte estimée (EUR)", fontsize=9)
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
        )
        _style_base(fig, ax, f"Niveau de confiance : {niveau}")
        ax.legend(fontsize=9)

    fig.suptitle("Comparaison VaR / ES — Trois méthodes", fontsize=14,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 5. Sensibilité à la volatilité
# =============================================================================

def tracer_sensibilite_volatilite(
    df_sensib: pd.DataFrame,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    VaR Monte Carlo en fonction du facteur de volatilité appliqué.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    niveaux = df_sensib["Niveau confiance"].unique()
    couleurs = plt.cm.Reds(np.linspace(0.4, 0.9, len(niveaux)))

    for niveau, couleur in zip(niveaux, couleurs):
        data = df_sensib[df_sensib["Niveau confiance"] == niveau]
        ax.plot(data["Facteur volatilité"], data["VaR MC (EUR)"],
                marker="o", lw=2, color=couleur, label=f"VaR MC {niveau}")
        ax.fill_between(data["Facteur volatilité"], data["VaR MC (EUR)"],
                        data["ES MC (EUR)"], alpha=0.15, color=couleur)

    ax.axvline(1.0, color="gray", ls="--", lw=1.2, label="Baseline (x1)")
    ax.set_xlabel("Facteur multiplicateur de volatilité", fontsize=10)
    ax.set_ylabel("VaR Monte Carlo (EUR)", fontsize=10)
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
    )
    _style_base(fig, ax, "Sensibilité de la VaR à la volatilité")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 6. Sensibilité à la corrélation
# =============================================================================

def tracer_sensibilite_correlation(
    df_sensib: pd.DataFrame,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    VaR Monte Carlo en fonction du facteur de corrélation appliqué.
    Illustre la perte de diversification lors d'une crise de marché.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    niveaux = df_sensib["Niveau confiance"].unique()
    couleurs = plt.cm.Blues(np.linspace(0.4, 0.9, len(niveaux)))

    for niveau, couleur in zip(niveaux, couleurs):
        data = df_sensib[df_sensib["Niveau confiance"] == niveau]
        ax.plot(data["Facteur corrélation"], data["VaR MC (EUR)"],
                marker="s", lw=2, color=couleur, label=f"VaR MC {niveau}")

    ax.axvline(1.0, color="gray", ls="--", lw=1.2, label="Corrélations historiques")
    ax.axvline(0.0, color=COULEURS["tertiaire"], ls=":", lw=1.2, label="Décorrélation totale")
    ax.set_xlabel("Facteur multiplicateur des corrélations", fontsize=10)
    ax.set_ylabel("VaR Monte Carlo (EUR)", fontsize=10)
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
    )
    _style_base(fig, ax, "Sensibilité de la VaR aux corrélations")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 7. Sensibilité à l'horizon
# =============================================================================

def tracer_sensibilite_horizon(
    df_sensib: pd.DataFrame,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    VaR Monte Carlo vs horizon, comparée à la règle racine carrée.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    niveaux = df_sensib["Niveau confiance"].unique()
    couleurs = plt.cm.Greens(np.linspace(0.4, 0.9, len(niveaux)))

    for niveau, couleur in zip(niveaux, couleurs):
        data = df_sensib[df_sensib["Niveau confiance"] == niveau].sort_values("Horizon (jours)")
        ax.plot(data["Horizon (jours)"], data["VaR MC (EUR)"],
                marker="^", lw=2, color=couleur, label=f"VaR MC {niveau}")

    # Courbe théorique racine carrée (normalisée sur la VaR 1j à 99%)
    if len(df_sensib) > 0:
        ref = df_sensib[
            (df_sensib["Niveau confiance"] == df_sensib["Niveau confiance"].iloc[-1]) &
            (df_sensib["Horizon (jours)"] == 1)
        ]["VaR MC (EUR)"].values
        if len(ref) > 0:
            horizons_th = np.linspace(1, df_sensib["Horizon (jours)"].max(), 50)
            ax.plot(horizons_th, ref[0] * np.sqrt(horizons_th),
                    color="gray", ls="--", lw=1.5, label="Règle √h (théorique)")

    ax.set_xlabel("Horizon (jours ouvrés)", fontsize=10)
    ax.set_ylabel("VaR Monte Carlo (EUR)", fontsize=10)
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
    )
    _style_base(fig, ax, "Sensibilité de la VaR à l'horizon temporel")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 8. Sensibilité au niveau de confiance
# =============================================================================

def tracer_sensibilite_confiance(
    df_sensib: pd.DataFrame,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    VaR et ES en fonction du niveau de confiance, pour les trois méthodes.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    couleurs_methodes = {
        "Historique":   COULEURS["tertiaire"],
        "Paramétrique": COULEURS["accent"],
        "Monte Carlo":  COULEURS["secondaire"],
    }
    methodes = df_sensib["Méthode"].unique()

    for ax, metrique, titre in zip(
        axes, ["VaR (EUR)", "ES (EUR)"], ["Value-at-Risk", "Expected Shortfall"]
    ):
        for methode in methodes:
            data = df_sensib[df_sensib["Méthode"] == methode].sort_values("Niveau confiance")
            ax.plot(
                data["Niveau confiance"] * 100, data[metrique],
                marker="o", lw=2, markersize=5,
                color=couleurs_methodes.get(methode, COULEURS["neutre"]),
                label=methode,
            )
        ax.set_xlabel("Niveau de confiance (%)", fontsize=10)
        ax.set_ylabel(f"{titre} (EUR)", fontsize=10)
        ax.legend(fontsize=9)
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
        )
        _style_base(fig, ax, f"{titre} selon le niveau de confiance")

    fig.suptitle("Sensibilité au niveau de confiance — VaR et ES", fontsize=13,
                 fontweight="bold")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 9. Rendements historiques du portefeuille
# =============================================================================

def tracer_rendements_portfolio(
    rendements: pd.Series,
    var_95: float,
    var_99: float,
    valeur_initiale: float,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    Série temporelle des rendements quotidiens du portefeuille.
    Les dépassements de VaR sont mis en évidence.
    """
    fig, ax = plt.subplots(figsize=(13, 5))
    pnl = rendements * valeur_initiale

    ax.bar(pnl.index, pnl, width=1, color=np.where(pnl >= 0, COULEURS["tertiaire"],
                                                      COULEURS["secondaire"]), alpha=0.6)
    ax.axhline(-var_95, color=COULEURS["accent"],    ls="--", lw=1.5, label=f"VaR 95% : {var_95:,.0f}")
    ax.axhline(-var_99, color=COULEURS["secondaire"], ls="-",  lw=1.5, label=f"VaR 99% : {var_99:,.0f}")
    ax.axhline(0, color="black", ls="-", lw=0.7, alpha=0.4)

    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("P&L journalier (EUR)", fontsize=10)
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
    )
    _style_base(fig, ax, "P&L quotidien du portefeuille — Comparaison aux seuils VaR")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)


# =============================================================================
# 10. Attribution marginale du risque
# =============================================================================

def tracer_attribution_risque(
    tickers: list[str],
    contrib_pct: np.ndarray,
    poids: np.ndarray,
    chemin: Path,
    dpi: int = 150,
) -> None:
    """
    Graphique en barres des contributions au risque par actif.
    Compare les poids du portefeuille et les contributions à la VaR.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(tickers))
    width = 0.35

    ax.bar(x - width/2, poids * 100, width, label="Poids (%)",
           color=COULEURS["primaire"], alpha=0.75)
    ax.bar(x + width/2, contrib_pct, width, label="Contribution VaR (%)",
           color=COULEURS["secondaire"], alpha=0.75)

    ax.set_xticks(x)
    ax.set_xticklabels(tickers, fontsize=10)
    ax.set_ylabel("Pourcentage (%)", fontsize=10)
    ax.axhline(0, color="black", lw=0.7, alpha=0.4)
    ax.legend(fontsize=9)
    _style_base(fig, ax, "Attribution marginale du risque par actif")
    fig.tight_layout()
    sauvegarder(fig, chemin, dpi)
