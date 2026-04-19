# Vue d'ensemble du projet : Moteur Monte Carlo de VaR et Expected Shortfall

## Ce qu'est ce projet en une phrase

Ce projet est un moteur de calcul de risque de marché qui mesure, via trois méthodes (historique, paramétrique et Monte Carlo), combien un portefeuille de cinq actifs financiers peut perdre sur un horizon donné avec une certaine probabilité — et ce que l'on peut espérer perdre en moyenne dans les pires cas.

---

## Pourquoi ce projet est utile

### Le problème de fond

Tout gérant de portefeuille, toute banque, tout fonds d'investissement fait face à la même question fondamentale : **combien puis-je perdre ?** La réponse n'est jamais certaine, mais elle doit être chiffrée. Les régulateurs (Bâle III, Solvabilité II) exigent que les institutions financières quantifient leur exposition au risque de marché de façon rigoureuse.

La Value at Risk (VaR) est depuis les années 1990 l'outil de référence pour cette quantification. Sa popularité tient à sa simplicité d'interprétation : « avec une probabilité de 99%, je ne perdrai pas plus de X euros demain. » Mais cet outil a ses limites, notamment le fait qu'il ne dit rien sur ce qui se passe au-delà du seuil. L'Expected Shortfall (ES) — aussi appelé CVaR ou Conditional VaR — comble cette lacune en mesurant la perte moyenne dans les scénarios extrêmes.

### Ce que ce projet apporte concrètement

1. **Comparaison de trois méthodes** : le projet ne se contente pas d'une seule approche. Il implémente les trois grandes familles de calcul de VaR et permet de comparer leurs résultats, leurs hypothèses et leurs comportements face à des changements de paramètres.

2. **Simulation Monte Carlo réaliste** : avec 50 000 scénarios et une distribution Student-t multivariée (qui capture les queues épaisses observées sur les marchés), le moteur de simulation va au-delà de la simple hypothèse gaussienne.

3. **Backtesting rigoureux** : le test de Kupiec valide statistiquement que le modèle n'est ni trop conservateur ni trop laxiste.

4. **Analyse de sensibilité** : comprendre comment la VaR réagit à des variations de volatilité, de corrélation, d'horizon ou de niveau de confiance est essentiel pour la gestion du risque.

5. **Attribution marginale** : identifier quel actif contribue le plus au risque du portefeuille permet de prendre des décisions de rééquilibrage informées.

---

## Le portefeuille étudié

Le portefeuille de référence est constitué de cinq actifs diversifiés, couvrant différentes classes d'actifs :

| Actif   | Description                        | Poids | Exposition (sur 1M EUR) |
|---------|------------------------------------|-------|--------------------------|
| SPY     | ETF S&P 500 (actions US)           | 30%   | 300 000 EUR              |
| EFA     | ETF actions internationales        | 20%   | 200 000 EUR              |
| AGG     | ETF obligations US                 | 25%   | 250 000 EUR              |
| GLD     | ETF or                             | 15%   | 150 000 EUR              |
| EURUSD  | Taux de change EUR/USD             | 10%   | 100 000 EUR              |

La valeur totale du portefeuille est de **1 000 000 EUR**. Cette diversification entre actions, obligations, matières premières et devises représente une allocation typique d'un fonds multi-actifs modéré.

---

## Les résultats obtenus

Voici les résultats numériques produits par le moteur sur données réelles :

### VaR à 1 jour

| Méthode              | VaR 95%    | VaR 99%    |
|----------------------|------------|------------|
| Historique           | 9 590 EUR  | 13 795 EUR |
| Paramétrique (gauss) | 9 277 EUR  | 13 059 EUR |
| Monte Carlo          | 9 372 EUR  | 13 162 EUR |

La VaR MC à 99% de **13 162 EUR** signifie : avec 99% de probabilité, le portefeuille ne perdra pas plus de 13 162 EUR le lendemain. En pourcentage : **1,32% de la valeur du portefeuille**.

### Expected Shortfall (Monte Carlo)

| Niveau | ES         |
|--------|------------|
| 95%    | 11 712 EUR |
| 99%    | 14 993 EUR |

L'ES à 99% signifie : **dans les 1% pires scénarios, on perd en moyenne 14 993 EUR**.

### Backtesting Kupiec

| Niveau | Exceptions | Taux observé | Taux théorique | Verdict  |
|--------|------------|--------------|----------------|----------|
| 95%    | 51/1008    | 5,06%        | 5,00%          | VALIDE   |
| 99%    | 11/1008    | 1,09%        | 1,00%          | VALIDE   |

Le modèle est statistiquement valide : il n'est ni trop optimiste ni trop pessimiste.

---

## Les grandes étapes du pipeline

Le fichier `run_all.py` orchestre l'ensemble du pipeline en 16 étapes séquentielles. Voici les grandes phases :

### Phase 1 — Acquisition et préparation des données (étapes 1-3)
- **Chargement** : téléchargement des prix historiques via Yahoo Finance (ou lecture depuis cache)
- **Calcul des rendements** : transformation des prix en rendements logarithmiques journaliers
- **Calibration du portefeuille** : calcul de la matrice de variance-covariance, de la corrélation, du rendement et de la volatilité du portefeuille

### Phase 2 — Calcul des métriques de risque (étapes 4-7)
- **VaR historique** : tri des rendements historiques, lecture du quantile
- **VaR paramétrique** : application de la formule analytique sous hypothèse gaussienne
- **Simulation Monte Carlo** : génération de 50 000 scénarios via décomposition de Cholesky
- **Expected Shortfall** : calcul de la moyenne des pertes au-delà de la VaR pour chaque méthode

### Phase 3 — Validation et analyse (étapes 8-12)
- **Backtesting** : test de Kupiec sur série historique
- **Analyses de sensibilité** : variation de volatilité, corrélation, horizon, niveau de confiance
- **Attribution marginale** : contribution de chaque actif au risque total

### Phase 4 — Visualisation et rapport (étapes 13-16)
- **Graphiques** : distribution P&L, heatmaps, courbes de sensibilité
- **Rapport** : synthèse CSV et console des résultats

---

## Le rôle de chaque module

### `config.yaml`
Le fichier de configuration central. Il définit : les actifs et leurs poids, la valeur du portefeuille, les horizons, les niveaux de confiance, le nombre de simulations, les dates de la période d'estimation, et tous les paramètres techniques. **Modifier ce fichier suffit pour changer entièrement le comportement du système** sans toucher au code.

### `src/utils.py`
Fonctions utilitaires partagées : chargement du fichier de configuration YAML, configuration du logging, gestion des chemins de fichiers, fonctions de formatage. Ce module est importé par tous les autres.

### `src/data_loader.py`
Responsable de l'acquisition des données. Se connecte à Yahoo Finance via `yfinance`, télécharge les prix ajustés des clôtures pour chaque actif sur la période définie, gère le cache local pour éviter les téléchargements répétés, et effectue les vérifications de qualité (valeurs manquantes, cohérence des dates).

### `src/portfolio.py`
Construit la vision portefeuille à partir des données individuelles. Calcule : les rendements du portefeuille pondérés, le vecteur de rendements espérés, la matrice de variance-covariance, la volatilité du portefeuille, et les corrélations entre actifs. C'est ici que les données individuelles deviennent un objet portefeuille cohérent.

### `src/returns_model.py`
Modélise la distribution des rendements. Implémente l'estimation de la distribution gaussienne multivariée et de la distribution Student-t multivariée. Calibre les paramètres (moyenne, covariance, degrés de liberté pour Student). Effectue la décomposition de Cholesky qui est au cœur de la simulation.

### `src/simulation.py`
Le coeur du moteur Monte Carlo. Génère les 50 000 trajectoires de rendements simulés en utilisant la décomposition de Cholesky pour reproduire la structure de corrélation. Calcule les pertes et profits simulés du portefeuille pour chaque scénario. Gère les deux modes (gaussien et Student-t).

### `src/risk_metrics.py`
Calcule toutes les métriques de risque : VaR historique, VaR paramétrique gaussienne, VaR Monte Carlo, Expected Shortfall pour chaque méthode. Implémente également l'ajustement pour horizon multi-jours (règle de la racine carrée du temps). C'est le module qui produit les chiffres finaux.

### `src/sensitivity.py`
Analyse comment les métriques de risque varient en fonction des paramètres. Implémente les analyses de sensibilité à la volatilité (chocs de +/- 20%), à la corrélation (de 0 à 0.9), à l'horizon (1, 5, 10, 20 jours), et au niveau de confiance (90% à 99.9%). Calcule aussi l'attribution marginale du risque par actif.

### `src/plots.py`
Génère toutes les visualisations du projet : histogramme de la distribution P&L simulée avec marquage de la VaR et de l'ES, heatmap de la matrice de corrélation, graphiques de sensibilité, barres d'attribution marginale. Utilise `matplotlib` et `seaborn`.

### `src/report.py`
Compile et formate tous les résultats en un rapport structuré. Exporte les tableaux en CSV dans le dossier `outputs/`, génère un résumé console formaté, et prépare les données pour des rapports plus élaborés si besoin.

### `run_all.py`
Le script principal qui orchestre l'ensemble du pipeline. Il appelle les modules dans le bon ordre, passe les données d'un module à l'autre, gère les erreurs, et enregistre les résultats à chaque étape. C'est le point d'entrée unique pour exécuter le projet.

---

## Ce qu'il faut retenir pour une présentation de 2 minutes

Si vous deviez présenter ce projet en 2 minutes, voici les points essentiels à couvrir :

**1. Le contexte (20 secondes)**
> "Ce projet quantifie le risque de marché d'un portefeuille multi-actifs de 1 million d'euros. La question centrale est : combien peut-on perdre demain ?"

**2. La méthode (40 secondes)**
> "Nous calculons la VaR et l'Expected Shortfall par trois approches : historique, paramétrique gaussienne, et Monte Carlo avec 50 000 simulations. Pour la simulation, nous utilisons une décomposition de Cholesky pour reproduire fidèlement les corrélations entre actifs."

**3. Les résultats (30 secondes)**
> "Notre VaR Monte Carlo à 99% sur 1 jour est de 13 162 euros, soit 1,32% du portefeuille. En d'autres termes, il y a 1% de chance de perdre plus de 13 162 euros demain. L'Expected Shortfall à 99% est de 14 993 euros — c'est ce qu'on perd en moyenne dans ces 1% de mauvais jours."

**4. La validation (20 secondes)**
> "Le modèle est validé par un backtesting de Kupiec sur 1008 jours. On observe 51 exceptions à 95% et 11 à 99%, soit des taux de 5,06% et 1,09% — parfaitement alignés avec les niveaux théoriques."

**5. Les apports (10 secondes)**
> "Le projet inclut aussi des analyses de sensibilité et une attribution marginale du risque par actif."

---

## Limitations importantes à avoir en tête

Ce projet, bien que complet et fonctionnel, repose sur plusieurs hypothèses simplificatrices qu'il est honnête de mentionner :

- **Portefeuille statique** : les poids ne changent pas pendant la simulation. En réalité, un gestionnaire rééquilibre son portefeuille.
- **Stationnarité** : on suppose que la distribution historique reste valable dans le futur. Les régimes de marché (crise, calme) ne sont pas modélisés.
- **Liquidité parfaite** : on suppose pouvoir vendre n'importe quelle quantité sans impact de marché.
- **Pas de VaR intra-journalière** : on raisonne à la clôture journalière.
- **Corrélations stables** : la matrice de corrélation est supposée constante, ce qui est faux en période de stress (les corrélations montent vers 1).

Ces limitations sont discutées en détail dans le fichier `05_limits_and_extensions.md`.

---

## Structure des fichiers du projet

```
projet/
├── config.yaml                    # Configuration centralisée
├── run_all.py                     # Pipeline principal (16 étapes)
├── requirements.txt               # Dépendances Python
├── src/
│   ├── utils.py                   # Utilitaires partagés
│   ├── data_loader.py             # Chargement des données
│   ├── portfolio.py               # Construction du portefeuille
│   ├── returns_model.py           # Modélisation des rendements
│   ├── simulation.py              # Moteur Monte Carlo
│   ├── risk_metrics.py            # Calcul VaR et ES
│   ├── sensitivity.py             # Analyses de sensibilité
│   ├── plots.py                   # Visualisations
│   └── report.py                  # Génération du rapport
├── data/                          # Données téléchargées (cache)
├── outputs/                       # Résultats et graphiques
│   ├── figures/                   # Graphiques PNG
│   └── tables/                    # Tableaux CSV
├── tests/                         # Tests unitaires
└── docs/                          # Cette documentation
```

---

## Ordre de lecture recommandé de la documentation

Pour comprendre ce projet en profondeur, lisez les fichiers dans cet ordre :

1. **Ce fichier** (`00_big_picture.md`) — Vue d'ensemble, 20 minutes
2. `01_theory_from_scratch.md` — Théorie complète, 45 minutes
3. `03_code_walkthrough.md` — Guide de lecture du code, 30 minutes
4. `02_math_details.md` — Maths détaillées, 30 minutes
5. `04_results_interpretation.md` — Lecture des résultats, 20 minutes
6. `05_limits_and_extensions.md` — Limites et extensions, 15 minutes
7. `06_interview_questions_answers.md` — Préparation entretien, 60 minutes

Consultez `09_reading_guide.md` pour des parcours adaptés selon votre objectif et votre temps disponible.
