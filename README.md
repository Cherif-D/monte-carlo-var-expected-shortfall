# Moteur Monte Carlo de VaR et Expected Shortfall

Projet Python de risk management pour estimer la Value-at-Risk (VaR) et l'Expected Shortfall (ES) d'un portefeuille multi-actifs. Le pipeline couvre trois approches de mesure du risque: historique, parametrique gaussienne et Monte Carlo, avec analyses de sensibilite, attribution marginale du risque, backtesting de Kupiec, figures et rapport Markdown.

## Ce que fait le projet

- Chargement et controle de donnees de prix multi-actifs.
- Construction d'un portefeuille pondere depuis `config.yaml`.
- Calibration des rendements, volatilites, covariance et correlations.
- Calcul VaR/ES historique, parametrique et Monte Carlo.
- Simulation Monte Carlo normale ou Student-t.
- Analyses de sensibilite: volatilite, correlation, horizon, niveau de confiance.
- Attribution marginale du risque par actif.
- Backtesting simplifie de la VaR.
- Generation automatique de tableaux CSV, figures PNG et rapport Markdown.
- Tests unitaires et tests de coherence mathematique.

## Point important sur les donnees

Par defaut, le projet utilise `data/examples/example_prices.csv`, un jeu de donnees synthetiques genere par mouvement brownien geometrique. Les tickers ressemblent a des actifs de marche (`SPY`, `EFA`, `AGG`, `GLD`, `EURUSD`), mais les prix fournis ne sont pas des prix historiques reels.

Le code contient aussi un mode `live` via `yfinance`, mais il est optionnel et non active par defaut. Pour l'utiliser, installer `yfinance`, passer `data.mode` a `live` dans `config.yaml`, puis verifier les tickers et les dates.

Ce projet est pedagogique et ne constitue pas un conseil financier.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Sur Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Pour lancer les tests:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Utilisation

Lancer le pipeline complet:

```bash
python run_all.py
```

Avec une configuration alternative:

```bash
python run_all.py --config config.yaml
```

Les sorties sont creees automatiquement dans `outputs/` quand le pipeline est lance:

- `outputs/figures/` pour les graphiques.
- `outputs/tables/` pour les tableaux CSV.
- `outputs/reports/final_report.md` pour le rapport.
- `outputs/logs/run.log` pour les logs.

Le dossier `outputs/` est ignore par Git car son contenu est regenerable.

## Resultats de reference

Avec la configuration par defaut, le pipeline produit notamment:

- VaR Monte Carlo 95% sur 1 jour: environ 9 372 EUR.
- ES Monte Carlo 95% sur 1 jour: environ 11 712 EUR.
- VaR Monte Carlo 99% sur 1 jour: environ 13 162 EUR.
- ES Monte Carlo 99% sur 1 jour: environ 14 993 EUR.

Les chiffres peuvent legerement varier si la configuration, les donnees ou la version des dependances changent.

## Structure

```text
.
├── config.yaml
├── run_all.py
├── requirements.txt
├── requirements-dev.txt
├── data/
│   └── examples/
├── src/
│   ├── data_loader.py
│   ├── portfolio.py
│   ├── returns_model.py
│   ├── simulation.py
│   ├── risk_metrics.py
│   ├── sensitivity.py
│   ├── plots.py
│   ├── report.py
│   └── utils.py
└── tests/
```

## Validation

Validation locale effectuee avec Python 3.12:

```text
63 passed
```

Le pipeline complet `python run_all.py` s'execute egalement avec succes et regenere les sorties.

## Limites connues

- Les donnees par defaut sont synthetiques.
- Le modele suppose des parametres stationnaires.
- La VaR parametrique repose sur une hypothese gaussienne.
- Le backtesting actuel est in-sample et simplifie.
- Les couts de transaction, la liquidite et les produits derives ne sont pas modelises.

## Licence

Aucune licence open source n'est fournie pour l'instant. Ajouter une licence explicite avant de reutiliser ou redistribuer le projet dans un contexte public large.
