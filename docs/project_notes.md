# Notes de projet : choix de conception et points techniques

## 1. Choix architecturaux

### 1.1 Séparation configuration / code

**Décision** : tout ce qui est paramétrable (actifs, poids, horizons, niveaux de confiance, nombre de simulations, dates) est défini dans `config.yaml`.

**Justification** : facilite les tests de sensibilité au niveau de la configuration sans toucher au code. Permet à un analyste non-développeur de modifier les paramètres. Réduit les risques de régression lors de modifications du code.

**Alternative considérée** : hard-coder les paramètres dans `run_all.py`. Rejeté car cela rendrait le code difficile à tester et à maintenir.

### 1.2 Architecture modulaire (9 modules)

**Décision** : séparer data_loader, portfolio, returns_model, simulation, risk_metrics, sensitivity, plots, report.

**Justification** : chaque module a une responsabilité unique (principe SRP — Single Responsibility Principle). Facilite les tests unitaires (on peut tester `risk_metrics.py` indépendamment de `data_loader.py`). Facilite la réutilisation (on peut importer uniquement les modules nécessaires).

**Alternative considérée** : un seul fichier `main.py` de 800 lignes. Rejeté car illisible et difficile à déboguer.

### 1.3 Graine aléatoire fixe

**Décision** : utiliser `config['simulation']['seed']` avec `seed = 42`. Le pipeline fixe aussi la graine globale via `fixer_seed`, et la simulation Monte Carlo utilise `np.random.default_rng(seed)`.

**Justification** : assure la reproductibilité exacte des résultats. Facilite le débogage (mêmes simulations à chaque exécution). Permet de comparer les résultats entre différentes configurations en gardant les simulations identiques.

**Inconvénient** : perd l'aspect "vraiment aléatoire". En production, on pourrait vouloir utiliser plusieurs graines et prendre la moyenne.

---

## 2. Choix méthodologiques

### 2.1 Log-returns vs rendements arithmétiques

**Décision** : utiliser les log-returns $r_t = \ln(P_t/P_{t-1})$.

**Justification** : additifs dans le temps (simplification des calculs multi-périodes), non bornés par -100% (propriété économique des prix positifs), meilleur comportement statistique pour la modélisation gaussienne.

**Limite** : pour des options ou des positions à levier, la distinction log/arithmétique devient plus importante. Pour un portefeuille d'ETF, la différence est négligeable sur des rendements journaliers (< 5%).

### 2.2 Distribution Monte Carlo par défaut

**Décision** : utiliser la distribution gaussienne multivariée par défaut, avec une option Student-t contrôlée par `simulation.distribution` et `simulation.student_df` dans `config.yaml`.

**Justification** : la gaussienne donne un point de comparaison analytique simple avec la VaR paramétrique. La Student-t reste disponible pour épaissir les queues de distribution lorsque l'objectif est d'illustrer un stress de queues plus réaliste.

**Alternative considérée** : estimer automatiquement les degrés de liberté de la Student-t par maximum de vraisemblance. Rejeté pour garder le projet lisible et reproductible dans une version pédagogique.

### 2.3 50 000 simulations

**Décision** : $N = 50\,000$ simulations Monte Carlo.

**Justification** : compromis entre précision et temps de calcul. L'erreur standard sur la VaR à 99% est d'environ ±60 EUR (< 0.5%). Le temps de calcul est de l'ordre de 1 à 3 secondes avec NumPy vectorisé — acceptable pour un pipeline non temps-réel.

**Sensibilité** : tests avec $N = 10\,000$ (bruit visible), $N = 100\,000$ (précision améliorée mais temps ×2). Pour une production à haute fréquence, 10 000 suffiraient ; pour la validation de modèle, 100 000+ seraient préférables.

### 2.4 Fenêtre d'estimation de 4 ans (~1000 jours)

**Décision** : utiliser environ 4 ans de données historiques pour l'estimation des paramètres.

**Justification** : trade-off entre représentativité (période longue) et réactivité aux changements de régime (période courte). 4 ans capture plusieurs cycles de marché. La fenêtre inclut COVID-19 (2020) et la hausse des taux (2022), ce qui donne une estimation "conservatrice" des paramètres de risque.

**Alternative** : fenêtre glissante de 250 jours (1 an). Plus réactive, mais plus volatile dans ses estimations. À envisager comme extension.

---

## 3. Points techniques notables

### 3.1 Performance de NumPy pour la simulation

La simulation Monte Carlo profite pleinement de la vectorisation NumPy. La génération de 50 000 × 5 nombres aléatoires et la multiplication matricielle `Z @ L.T` sont des opérations vectorisées qui s'exécutent en microsecondes par simulation.

```python
# Approche non-vectorisée (lente) : 50 000 boucles
for i in range(50000):
    z = rng.standard_normal(5)
    r = mean + L @ z  # 5 opérations
    
# Approche vectorisée (rapide) : une seule opération BLAS
Z = rng.standard_normal((50000, 5))        # matrice 50000×5
R = mean + Z @ L.T                          # BLAS niveau 3, très rapide
```

Le gain de performance est typiquement 100x à 1000x entre les deux approches.

### 3.2 Cache des données

Le mode par défaut utilise un CSV local d'exemple, ce qui rend le projet exécutable sans connexion internet. Le mode `live` via Yahoo Finance est disponible mais optionnel.

**Point d'attention** : aucun cache persistant de donnees live n'est implemente dans la version actuelle. Une extension naturelle serait d'ajouter un cache invalide automatiquement lorsque les tickers ou la plage de dates changent.

### 3.3 Convention de signe

**Convention choisie** : **perte positive**. La variable `losses` dans le code représente $L = -\text{P\&L}$. Positif = perte, négatif = gain.

Cette convention est dominante dans les textes de risk management (on parle de "perte", pas de "rendement négatif"). Elle simplifie la lecture : `np.percentile(losses, 99)` donne directement la VaR à 99% (le 99ème percentile des pertes).

**Piège** : si on confond les conventions, la VaR sera calculée comme un gain (un nombre négatif), ce qui est absurde. Toujours vérifier que `VaR > 0`.

### 3.4 Normalisation des poids dans l'attribution marginale

Lors du calcul de la contribution marginale, on choque le poids d'un actif de ±$\delta$ = 1% et on renormalise. Cette renormalisation est nécessaire pour maintenir $\sum w_i = 1$.

```python
w_up = weights.copy()
w_up[i] += delta
w_up /= w_up.sum()  # Renormalisation indispensable
```

Sans renormalisation, le portefeuille aurait une valeur totale de 101% (ou 99%), ce qui serait incohérent.

---

## 4. Évolutions potentielles

### 4.1 Court terme (quelques jours de travail)

- Ajouter l'ES à 97.5% (niveau FRTB) : trivial, modifier un paramètre dans config
- Backtesting Christoffersen (conditional coverage) : 20 lignes de code
- Graphique QQ-plot des rendements vs Student-t : pour valider visuellement la distribution
- Export HTML du rapport : utiliser `pandas.to_html()` ou un template Jinja2

### 4.2 Moyen terme (quelques semaines)

- Modèle GARCH(1,1) : utiliser `arch` (bibliothèque Python), calibrer séparément sur chaque actif, simuler des trajectoires 10 jours conditionnellement à la volatilité courante
- Backtesting out-of-sample : séparer estimation (2020-2022) et backtesting (2023-2024)
- Interface Streamlit : formulaire web pour modifier les paramètres et visualiser les résultats

### 4.3 Long terme (quelques mois)

- Copules de Student-t ou Clayton pour remplacer la corrélation linéaire
- Ajout d'actifs : obligations d'entreprises, marchés émergents, Bitcoin
- Full revaluation pour portefeuilles avec options (requiert un modèle de pricing)
- Intégration d'un flux de données temps-réel (Bloomberg, Refinitiv)

---

## 5. Décisions documentées pour les choix contestables

### Pourquoi forward-fill pour les données manquantes ?

Alternative : supprimer les jours avec des actifs manquants. Problème : on perdrait ~5% des données (jours fériés locaux), réduisant l'efficacité de l'estimation. Le forward-fill introduit des log-returns nuls artificiels, ce qui légèrement réduit la variance estimée — biais conservateur acceptable.

### Pourquoi ne pas utiliser `scipy.stats.multivariate_t` pour la simulation ?

La bibliothèque `scipy` fournit des outils pour la distribution Student-t multivariée, mais l'implémentation manuelle (génération gaussienne + chi-carré) est plus transparente pédagogiquement et plus facilement modifiable. Pour une application en production, utiliser scipy serait préférable.

### Pourquoi la règle $\sqrt{T}$ plutôt qu'une simulation multi-jours ?

La règle $\sqrt{T}$ est simple, standard et permet une comparaison directe avec les exigences réglementaires (Bâle II utilise explicitement cette règle). Une simulation multi-jours serait plus précise mais plus complexe à implémenter et à valider. C'est une extension naturelle (voir `05_limits_and_extensions.md`).
