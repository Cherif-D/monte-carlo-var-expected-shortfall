"""
report.py — Génération du rapport final Markdown
=================================================
Ce module génère automatiquement un rapport Markdown dans
outputs/reports/final_report.md.

Le rapport synthétise :
- la composition du portefeuille,
- les paramètres calibrés,
- les résultats VaR/ES des trois méthodes,
- les résultats des analyses de sensibilité,
- une interprétation automatique,
- les limites et extensions.

Approche
--------
Le rapport est généré par concaténation de sections en Markdown pur.
Chaque section est une fonction qui retourne une chaîne de caractères.
L'assemblage final est écrit dans un fichier .md.
"""

import logging
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger("var_mc.report")


# =============================================================================
# Formatage utilitaire
# =============================================================================

def _fmt_eur(v: float) -> str:
    """Formate un montant en EUR."""
    return f"{v:,.0f} EUR"


def _fmt_pct(v: float, decimales: int = 2) -> str:
    """Formate un pourcentage."""
    return f"{v:.{decimales}f}%"


# =============================================================================
# Sections du rapport
# =============================================================================

def _df_to_markdown(df: pd.DataFrame) -> str:
    """Conversion DataFrame -> tableau Markdown sans dépendance externe (tabulate)."""
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep    = "|" + "|".join([" --- " for _ in cols]) + "|"
    rows   = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join([header, sep] + rows)


def _section_entete(config: dict) -> str:
    return f"""# Rapport de Risque — Moteur Monte Carlo de VaR et Expected Shortfall

**Date de génération :** {date.today().strftime("%d %B %Y")}
**Portefeuille :** {config['portfolio']['name']}
**Valeur initiale :** {config['portfolio']['valeur_initiale']:,} {config['portfolio']['currency']}
**Nombre de simulations :** {config['simulation']['n_simulations']:,}
**Horizon VaR :** {config['simulation']['horizon_jours']} jour(s)
**Distribution utilisée :** {config['simulation']['distribution'].capitalize()}

---

"""


def _section_composition(config: dict, stats_actifs: pd.DataFrame) -> str:
    lignes = ["## 1. Composition du portefeuille\n"]
    lignes.append("### Allocation\n")
    lignes.append("| Actif | Poids | Exposition (EUR) | Rendement annuel | Volatilité annuelle |")
    lignes.append("|-------|------:|----------------:|----------------:|--------------------:|")

    for ticker, poids in config["portfolio"]["actifs"].items():
        expo = poids * config["portfolio"]["valeur_initiale"]
        if ticker in stats_actifs.index:
            mu_a  = stats_actifs.loc[ticker, "Rendement moyen (a)"] * 100
            sig_a = stats_actifs.loc[ticker, "Volatilité (a)"] * 100
        else:
            mu_a = sig_a = float("nan")
        lignes.append(
            f"| {ticker} | {poids*100:.1f}% | {expo:>12,.0f} | "
            f"{mu_a:>+.2f}% | {sig_a:.2f}% |"
        )

    lignes.append("\n")
    return "\n".join(lignes)


def _section_parametres(params_df: pd.DataFrame, corr: np.ndarray, tickers: list[str]) -> str:
    lignes = ["## 2. Paramètres calibrés\n"]
    lignes.append("### Statistiques descriptives des rendements\n")
    lignes.append(_df_to_markdown(params_df.reset_index().rename(columns={"index": "Actif"})))
    lignes.append("\n")
    lignes.append("### Matrice de corrélation\n")

    header = "| Actif | " + " | ".join(tickers) + " |"
    sep    = "|-------|" + "-------|" * len(tickers)
    lignes.append(header)
    lignes.append(sep)
    for i, t in enumerate(tickers):
        row = f"| **{t}** | " + " | ".join(f"{corr[i, j]:.3f}" for j in range(len(tickers))) + " |"
        lignes.append(row)

    lignes.append("\n")
    return "\n".join(lignes)


def _section_resultats(df_resultats: pd.DataFrame) -> str:
    lignes = ["## 3. Résultats VaR et Expected Shortfall\n"]
    lignes.append(
        "> Les valeurs sont exprimées en EUR (perte positive = perte de valeur du portefeuille).\n"
    )

    # Tableau formaté
    df_affiche = df_resultats.copy()
    if "VaR (EUR)" in df_affiche.columns:
        df_affiche["VaR (EUR)"] = df_affiche["VaR (EUR)"].apply(lambda v: f"{v:,.0f}")
    if "ES (EUR)" in df_affiche.columns:
        df_affiche["ES (EUR)"] = df_affiche["ES (EUR)"].apply(lambda v: f"{v:,.0f}")

    lignes.append(_df_to_markdown(df_affiche))

    lignes.append("\n")
    lignes.append("### Interprétation\n")
    lignes.append(
        "La **VaR historique** s'appuie uniquement sur les données passées sans hypothèse "
        "distributionnelle. La **VaR paramétrique gaussienne** suppose des rendements "
        "normalement distribués et fournit une formule analytique fermée. "
        "La **VaR Monte Carlo** utilise la distribution empirique des scénarios simulés "
        "et constitue l'estimateur le plus flexible des trois.\n"
    )
    lignes.append(
        "L'**Expected Shortfall** (ES, également appelé CVaR) mesure la perte espérée "
        "*au-delà* de la VaR. Elle est toujours supérieure ou égale à la VaR et fournit "
        "une information sur la sévérité des pertes extrêmes, pas seulement leur seuil.\n"
    )
    return "\n".join(lignes)


def _section_sensibilite(
    df_vol: pd.DataFrame,
    df_corr: pd.DataFrame,
    df_horizon: pd.DataFrame,
) -> str:
    lignes = ["## 4. Analyses de sensibilité\n"]

    lignes.append("### 4.1 Sensibilité à la volatilité\n")
    lignes.append(
        "Le tableau suivant montre comment la VaR évolue lorsqu'on multiplie "
        "les volatilités historiques par un facteur allant de 0.5× à 2×.\n"
    )
    lignes.append(_df_to_markdown(df_vol))
    lignes.append("\n")

    lignes.append("### 4.2 Sensibilité aux corrélations\n")
    lignes.append(
        "L'augmentation des corrélations en période de stress réduit la diversification "
        "et augmente mécaniquement la VaR du portefeuille.\n"
    )
    lignes.append(_df_to_markdown(df_corr))
    lignes.append("\n")

    lignes.append("### 4.3 Sensibilité à l'horizon\n")
    lignes.append(
        "Sous l'hypothèse i.i.d., la VaR à l'horizon *h* est approximée par "
        "VaR_h = VaR_1j × √h (règle racine carrée du temps).\n"
    )
    lignes.append(_df_to_markdown(df_horizon))
    lignes.append("\n")

    return "\n".join(lignes)


def _section_backtesting(resultats_bt: dict | None) -> str:
    if resultats_bt is None:
        return "## 5. Backtesting\n\n*Non effectué.*\n\n"

    lignes = ["## 5. Backtesting de la VaR (Kupiec, 1995)\n"]
    lignes.append(
        "Le test de Kupiec évalue si la fréquence observée d'exceptions est "
        "statistiquement compatible avec la probabilité théorique (1 - alpha).\n"
    )
    for key, val in resultats_bt.items():
        lignes.append(f"- **{key}** : {val}")
    lignes.append("\n")
    return "\n".join(lignes)


def _section_limites() -> str:
    return """## 6. Limites et extensions

### Limites du modèle actuel

1. **Hypothèse gaussienne** : les rendements réels présentent des queues plus épaisses
   que la loi normale (kurtosis > 3). La VaR paramétrique gaussienne sous-estime
   systématiquement le risque extrême. L'extension Student-t corrige partiellement ce biais.

2. **Stationnarité** : le modèle suppose que les paramètres (mu, sigma, corrélations)
   sont constants dans le temps. En pratique, la volatilité est hétéroscédastique
   (effet GARCH) et les corrélations varient selon les régimes de marché.

3. **Portefeuille statique** : les poids ne sont pas rééquilibrés. Cette hypothèse
   est acceptable pour des horizons courts (< 10 jours) mais devient irréaliste
   pour des horizons plus longs.

4. **Absence de liquidité et coûts de transaction** : le modèle ne tient pas compte
   des coûts de débouclement d'une position en situation de stress.

5. **Données synthétiques** : les données d'exemple sont générées par GBM et ne
   reflètent pas toutes les caractéristiques des données réelles (sauts, fat tails).

### Extensions naturelles

- Modèle à volatilité stochastique (GARCH, EGARCH) pour mieux capturer le clustering de volatilité.
- Distribution de Student-t multivariée ou copules pour les queues épaisses.
- Monte Carlo conditionnel (scenarios de stress basés sur des événements historiques).
- Rééquilibrage dynamique du portefeuille.
- Calcul de la VaR incrémentale / marginale et de la contribution au risque.
- Extension aux produits dérivés (options, swaps) via valorisation Monte Carlo.

"""


def _section_conclusion(config: dict, df_resultats: pd.DataFrame) -> str:
    # Extraire la VaR MC 99%
    masque = (
        (df_resultats["Méthode"] == "monte_carlo") &
        (df_resultats["Niveau confiance"] == "99.0%")
    )
    if masque.any():
        var_mc_99 = df_resultats.loc[masque, "VaR (EUR)"].values[0]
        pct_var_99 = df_resultats.loc[masque, "VaR (%)"].values[0]
        texte_var = (
            f"La VaR Monte Carlo à 99% sur 1 jour est estimée à "
            f"**{var_mc_99:,} EUR** ({pct_var_99:.2f}% de la valeur du portefeuille)."
        )
    else:
        texte_var = "Les résultats sont détaillés dans le tableau de synthèse ci-dessus."

    return f"""## 7. Conclusion

Ce projet a permis de mettre en œuvre un moteur complet de calcul de la VaR et de
l'Expected Shortfall pour un portefeuille multi-actifs de {config['portfolio']['valeur_initiale']:,} EUR.

{texte_var}

Les trois méthodes (historique, paramétrique, Monte Carlo) fournissent des estimations
cohérentes. Les divergences observées reflètent les différentes hypothèses sous-jacentes
et illustrent l'importance de ne pas se fier à une seule méthode.

L'analyse de sensibilité confirme que la VaR est fortement dépendante du niveau de
volatilité et des corrélations entre actifs. En particulier, la corrélation croissante
en périodes de stress peut entraîner une augmentation significative du risque par
rapport aux conditions normales.

Ce travail constitue une base solide pour des développements ultérieurs vers des
modèles plus sophistiqués (GARCH, Student-t, copules, stress-testing réglementaire).

---

*Rapport généré automatiquement par run_all.py — Projet M1 Finance Quantitative.*
"""


# =============================================================================
# Génération complète
# =============================================================================

def generer_rapport(
    config: dict,
    stats_actifs: pd.DataFrame,
    params_df: pd.DataFrame,
    corr: np.ndarray,
    tickers: list[str],
    df_resultats: pd.DataFrame,
    df_vol: pd.DataFrame,
    df_corr: pd.DataFrame,
    df_horizon: pd.DataFrame,
    resultats_backtesting: dict | None = None,
    chemin: Path | None = None,
) -> str:
    """
    Assemble et écrit le rapport final Markdown.

    Paramètres
    ----------
    (voir les fonctions de section individuelles)
    chemin : Path | None
        Chemin de sauvegarde. Si None, retourne uniquement la chaîne.

    Retourne
    --------
    str
        Contenu complet du rapport en Markdown.
    """
    sections = [
        _section_entete(config),
        _section_composition(config, stats_actifs),
        _section_parametres(params_df, corr, tickers),
        _section_resultats(df_resultats),
        _section_sensibilite(df_vol, df_corr, df_horizon),
        _section_backtesting(resultats_backtesting),
        _section_limites(),
        _section_conclusion(config, df_resultats),
    ]

    rapport = "\n".join(sections)

    if chemin is not None:
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(rapport, encoding="utf-8")
        logger.info(f"Rapport final généré : {chemin}")

    return rapport
