# Guide de lecture du code

Ce document accompagne la lecture du projet tel qu'il est implemente dans le depot. Il suit le pipeline `run_all.py`, puis renvoie vers les modules principaux de `src/`.

## Vue d'ensemble

```text
run_all.py
  -> src/utils.py          configuration, logging, chemins
  -> src/data_loader.py    donnees de prix et rendements log
  -> src/portfolio.py      portefeuille, poids, P&L
  -> src/returns_model.py  calibration mu, sigma, covariance, correlation
  -> src/risk_metrics.py   VaR, ES, backtesting, attribution
  -> src/simulation.py     Monte Carlo normal ou Student-t
  -> src/sensitivity.py    scenarios de sensibilite
  -> src/plots.py          figures
  -> src/report.py         rapport Markdown
```

Le point d'entree unique est:

```bash
python run_all.py
```

La configuration centrale est `config.yaml`. Les resultats generes sont ecrits dans `outputs/`, mais ces fichiers sont ignorés par Git car ils sont reproductibles.

## Configuration

La section portefeuille de `config.yaml` definit la valeur initiale, la devise et les poids:

```yaml
portfolio:
  name: "Portefeuille Multi-Actifs M1"
  currency: "EUR"
  valeur_initiale: 1_000_000
  actifs:
    SPY: 0.30
    EFA: 0.20
    AGG: 0.25
    GLD: 0.15
    EURUSD: 0.10
```

La section simulation controle le nombre de scenarios, l'horizon, la distribution et la graine:

```yaml
simulation:
  n_simulations: 50000
  seed: 42
  horizon_jours: 1
  distribution: "normal"
  student_df: 5
```

Par defaut, les donnees viennent de `data/examples/example_prices.csv`, qui est un jeu de donnees synthetiques. Le mode `live` existe via `yfinance`, mais il est optionnel.

## `run_all.py`

`run_all.py` orchestre toutes les etapes:

1. Charge `config.yaml`.
2. Cree les dossiers de sortie.
3. Initialise le logger.
4. Charge les prix.
5. Calcule les rendements logarithmiques.
6. Construit le portefeuille.
7. Calibre les parametres de rendements.
8. Calcule VaR/ES historique et parametrique.
9. Lance la simulation Monte Carlo.
10. Calcule VaR/ES Monte Carlo.
11. Produit les analyses de sensibilite.
12. Calcule l'attribution marginale du risque.
13. Lance un backtesting Kupiec simplifie.
14. Genere figures, tableaux et rapport.

Le script retourne aussi un dictionnaire de resultats si `main()` est appele depuis Python.

## `src/utils.py`

Fonctions transverses:

- `charger_config`: lit un YAML avec `yaml.safe_load`.
- `initialiser_logger`: configure logging console/fichier.
- `fixer_seed`: fixe la graine globale NumPy.
- `creer_dossiers_sortie`: cree les dossiers `outputs`.
- `chemin_figure` et `chemin_table`: construisent les chemins de sortie.
- `verifier_poids`: valide que les poids somment a 1.

Le module ne contient pas de logique financiere; il sert de socle technique.

## `src/data_loader.py`

La fonction principale est `charger_prix(config)`.

En mode `example`, elle lit:

```text
data/examples/example_prices.csv
```

Si le fichier manque, le script `data/examples/generate_example_data.py` regenere automatiquement les donnees synthetiques.

En mode `live`, le module tente d'importer `yfinance` et de telecharger les prix. Le ticker `EURUSD` est transforme en `EURUSD=X` pour Yahoo Finance.

Le controle qualite verifie notamment:

- ordre chronologique des dates;
- forward-fill des valeurs manquantes;
- absence de NaN apres correction;
- prix strictement positifs.

Les rendements sont calcules par:

```python
rendements = np.log(prix / prix.shift(1)).dropna()
```

## `src/portfolio.py`

La classe `Portfolio` represente:

- le nom du portefeuille;
- les poids par ticker;
- la valeur initiale;
- la devise.

La methode `calculer_rendements` combine les rendements actifs:

```python
r_portfolio = rendements_actifs[self.tickers].values @ self.vecteur_poids
```

La methode `pnl_absolu` convertit ensuite les rendements en P&L:

```python
pnl = rendement_portefeuille * valeur_initiale
```

La convention du projet est: perte positive dans les resultats VaR/ES, P&L negatif dans les distributions de P&L.

## `src/returns_model.py`

`calibrer_parametres` estime:

- `mu`: rendement moyen journalier par actif;
- `sigma`: volatilite journaliere par actif;
- `cov`: matrice de covariance journaliere;
- `corr`: matrice de correlation;
- `n_obs`: nombre d'observations.

Le module contient aussi `tester_normalite`, qui applique Jarque-Bera et Shapiro sur les rendements, puis `echelonner_parametres`, qui applique:

```text
mu_h = mu_j * h
cov_h = cov_j * h
```

## `src/simulation.py`

`simuler_monte_carlo` est le coeur numerique du projet.

Algorithme:

1. Echelonner `mu` et `cov` a l'horizon choisi.
2. Calculer une decomposition de Cholesky robuste.
3. Generer des innovations normales ou Student-t avec `np.random.default_rng(seed)`.
4. Injecter la covariance:

```python
rendements_actifs = mu_h + (innovations @ L.T)
```

5. Agreger par les poids:

```python
rendements_portfolio = rendements_actifs @ poids
pnl = rendements_portfolio * valeur_initiale
```

Le resultat est un objet `ResultatsSimulation` contenant la distribution des P&L simules, les rendements simules et les metadonnees de simulation.

## `src/risk_metrics.py`

Le module applique la convention:

```text
VaR_alpha = -quantile_{1-alpha}(P&L)
```

Les trois methodes principales sont:

- `var_es_historique`: quantiles empiriques sur les P&L historiques.
- `var_es_parametrique`: formule analytique sous hypothese normale.
- `var_es_monte_carlo`: quantiles empiriques sur les P&L simules.

Le module fournit aussi:

- `calculer_toutes_mesures`: tableau comparatif des methodes.
- `backtester_var`: test de Kupiec simplifie par comptage des exceptions.
- `attribution_marginale_risque`: contribution marginale numerique a la VaR.

## `src/sensitivity.py`

Ce module stresse les hypotheses du modele:

- volatilites multipliees par des facteurs;
- correlations hors diagonale multipliees par des facteurs;
- horizons de 1, 5, 10, 21 jours;
- niveaux de confiance de 90% a 99.9%;
- comparaison entre portefeuille utilisateur et portefeuille equipondere.

Les matrices de covariance stressees sont reconstruites a partir des volatilites et correlations, puis regularisees si necessaire.

## `src/plots.py` et `src/report.py`

`plots.py` genere les figures PNG:

- distributions de P&L;
- heatmap de correlation;
- evolution des prix;
- comparaison des methodes;
- sensibilites;
- attribution du risque.

`report.py` assemble un rapport Markdown dans:

```text
outputs/reports/final_report.md
```

## Tests

Les tests couvrent:

- construction du portefeuille;
- formules VaR/ES;
- coherence ES >= VaR;
- convergence Monte Carlo;
- effet de diversification;
- invariance a l'ordre des actifs;
- reproductibilite via seed.

Commande:

```bash
python -m pytest -q
```

