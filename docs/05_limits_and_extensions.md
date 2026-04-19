# Limites honnêtes et extensions naturelles

## Préambule

Un bon travail académique ou professionnel en finance quantitative ne consiste pas seulement à présenter des résultats flatteurs — il consiste aussi à identifier honnêtement les limites du modèle, les hypothèses qu'on a faites et leurs implications. Ce document adopte délibérément une posture critique vis-à-vis du projet.

Cela ne diminue pas la valeur du travail réalisé. Au contraire, une critique rigoureuse montre une compréhension profonde des outils.

---

## 1. Les hypothèses fortes du modèle

### 1.1 Stationnarité des rendements

**L'hypothèse** : on suppose que la distribution des rendements est la même aujourd'hui qu'il y a 4 ans. On estime la matrice de covariance sur l'ensemble de la période historique et on l'applique pour les simulations futures.

**Pourquoi c'est discutable** : les marchés financiers traversent des **régimes** distincts — des périodes de faible volatilité (comme 2017-2019) et des périodes de forte volatilité (mars 2020, fin 2022). La volatilité du S&P 500 mesurée par le VIX peut passer de 12 à 80 en quelques jours.

**Impact concret** : si la période historique inclut 2020 (COVID) et 2022 (inflation/guerre), notre matrice de covariance sera "contaminée" par ces événements extrêmes et donnera une VaR trop élevée pour des conditions normales. À l'inverse, une fenêtre 2015-2019 (période très calme) donnera une VaR trop basse pour des conditions de stress.

**Ce qu'on aurait pu faire** : utiliser une fenêtre glissante (rolling window) de 250 jours, ou un modèle à régimes (Hidden Markov Model) qui distingue les états de marché "calme" et "agité".

### 1.2 Indépendance temporelle des rendements (i.i.d.)

**L'hypothèse** : les rendements journaliers sont supposés indépendants dans le temps. Cela justifie la règle de la racine carrée pour l'extension à des horizons multi-jours.

**Pourquoi c'est discutable** : les rendements financiers présentent deux violations bien documentées de l'i.i.d. :

1. **Clustering de volatilité** : les grandes variations (positives ou négatives) tendent à se suivre. Après un jour de forte baisse, la probabilité d'une autre grande variation est plus élevée qu'en temps normal. C'est le phénomène capturé par les modèles GARCH.

2. **Autocorrélation négative à très court terme** : sur des horizons intra-journaliers, les rendements présentent souvent une légère autocorrélation négative (mean-reversion de court terme due aux market makers).

**Impact concret** : la règle $\text{VaR}(T) = \text{VaR}(1) \times \sqrt{T}$ peut surestimer la VaR si la mean-reversion domine, ou la sous-estimer si le clustering de volatilité domine. En pratique, les deux effets se compensent partiellement, mais l'hypothèse reste approximative.

### 1.3 Portefeuille statique

**L'hypothèse** : les poids du portefeuille (30% SPY, 20% EFA, etc.) sont fixés et ne changent pas pendant l'horizon de calcul.

**Pourquoi c'est discutable** : en réalité, un gérant de portefeuille :
- Rééquilibre périodiquement (mensuellement ou trimestriellement) pour revenir aux poids cibles
- Réajuste ses positions en fonction des signaux de marché
- Gère les flux entrants et sortants (souscriptions/rachats des clients)

**Impact concret** : une perte de 5% sur SPY en une journée fait passer le poids effectif en actions à moins de 30%. Le lendemain, le portefeuille n'est plus le même qu'au départ. Notre VaR à 10 jours suppose que rien ne change — ce qui est irréaliste.

**Ce qu'on aurait pu faire** : simuler des trajectoires de 10 jours en rééquilibrant quotidiennement, ou modéliser le comportement du gérant (stratégie de rééquilibrage threshold).

### 1.4 Liquidité parfaite

**L'hypothèse** : on suppose qu'on peut vendre n'importe quelle quantité de n'importe quel actif immédiatement au prix de marché, sans coût ni impact de prix.

**Pourquoi c'est discutable** : pour un portefeuille de 1 million d'euros en ETF liquides (SPY, EFA, AGG), l'hypothèse est raisonnable. Mais pour des tailles plus importantes ou des actifs moins liquides (small caps, obligations d'entreprises), la liquidation peut :
- Prendre plusieurs jours (risque de liquidité)
- Faire bouger le marché contre soi (impact de prix, surtout pour des positions de grande taille)

**Ce qu'on aurait pu faire** : intégrer un **horizon de liquidation** spécifique à chaque actif, ou appliquer un ajustement de liquidité à la VaR (Liquidity-Adjusted VaR, LVaR).

### 1.5 Absence de modèle de coûts de transaction

Le projet ignore entièrement les coûts de transaction (bid-ask spread, commissions, taxes). Pour un ETF comme SPY, le spread est de l'ordre de 0.01% — négligeable. Mais pour des actifs moins liquides ou des stratégies à fort turnover, les coûts de transaction peuvent réduire significativement le rendement net.

### 1.6 Paramètres fixes (absence d'incertitude d'estimation)

**L'hypothèse** : les paramètres estimés ($\boldsymbol{\mu}$, $\boldsymbol{\Sigma}$, $\nu$) sont traités comme connus avec certitude. On ne prend pas en compte leur incertitude d'estimation.

**Pourquoi c'est discutable** : l'estimateur de la moyenne journalière a une erreur standard de ~0.03% (voir `02_math_details.md`). La matrice de covariance est également estimée avec une incertitude. Ignorer cette incertitude conduit à des VaR qui sont elles-mêmes incertaines — et cette incertitude sur la VaR n'est pas reportée.

**Ce qu'on aurait pu faire** : méthodes bootstrap pour construire des intervalles de confiance sur la VaR, ou approche bayésienne avec des distributions *a priori* sur les paramètres.

---

## 2. Les biais identifiés

### 2.1 Biais de la fenêtre temporelle

La VaR dépend fortement de la période historique choisie. Sur les données de 2020-2024 qui incluent la crise COVID (volatilité exceptionnelle) et la période post-COVID (hausse des marchés), nos résultats peuvent ne pas être représentatifs d'une "condition normale" de marché.

**Test de robustesse** : recalculer la VaR sur différentes fenêtres (2015-2019, 2018-2022, 2019-2023) et vérifier la stabilité des résultats. Si la VaR varie du simple au double selon la fenêtre, c'est un signal de fragilité.

### 2.2 Biais de "look-ahead" dans le backtesting

Il y a potentiellement un **biais de look-ahead** dans notre backtesting : on estime la VaR sur les données historiques et on backteste sur les mêmes données. Un backtesting rigoureusement out-of-sample utiliserait des données hors de la période d'estimation.

**En pratique** : si on estime sur 2020-2023 et backteste sur 2020-2023, les résultats sont (artificiellement) bons car le modèle a été calibré sur exactement les données testées. Un backtesting sur 2024 (données non vues) serait plus informatif.

### 2.3 Biais de survivance

Yahoo Finance fournit des données pour des actifs qui existent et sont liquides *aujourd'hui*. Des actifs qui ont disparu (faillittes, delisting) ne sont pas dans notre base de données. Notre univers d'actifs (SPY, EFA, AGG, GLD, EURUSD) est composé d'ETF très stables, donc ce biais est mineur ici. Pour des portefeuilles d'actions individuelles, il serait bien plus sérieux.

---

## 3. Ce que le projet ne fait pas

### 3.1 Modélisation de la dynamique temporelle de la volatilité (GARCH)

Le modèle GARCH (Generalized Autoregressive Conditional Heteroskedasticity) modélise le fait que la volatilité varie dans le temps et présente de la persistance. En périodes de crise, la volatilité monte et reste élevée plusieurs semaines ; en périodes calmes, elle est basse.

Un modèle GARCH(1,1) pour la volatilité du portefeuille aurait la forme :
$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

où $\epsilon_t$ est le choc de rendement. Ce modèle permettrait des **VaR conditionnelles** qui varient chaque jour en fonction du régime de volatilité actuel — bien plus réalistes que notre VaR unconditionnelle.

### 3.2 Modélisation de la dépendance par copules

Notre modèle suppose que la structure de dépendance entre actifs est entièrement capturée par la corrélation linéaire (matrice de Pearson). Or, il est connu que la dépendance entre actifs financiers est **asymétrique** : la corrélation est plus forte lors des fortes baisses (queue gauche) que lors des fortes hausses.

Les **copules** permettent de modéliser cette dépendance non-linéaire. Par exemple, une copule de Clayton a une forte dépendance dans la queue inférieure (co-mouvements négatifs) mais peu de dépendance dans la queue supérieure — ce qui reflète mieux le comportement observé des marchés en crise.

### 3.3 Scénarios historiques de stress

Le projet calcule une VaR "statistique" basée sur une distribution calibrée. Il ne calcule pas de **VaR historique par scénario**, qui consiste à rejouer des épisodes de crise historiques précis et à mesurer ce que le portefeuille actuel aurait subi :
- Crise des subprimes (septembre-octobre 2008)
- Flash crash (mai 2010)
- Crise de la zone euro (2011)
- COVID-19 (mars 2020)
- Krach obligataire (2022)

Ces scénarios historiques sont souvent exigés par les régulateurs et constituent une communication plus intuitive que des quantiles statistiques.

### 3.4 Gestion des options et produits dérivés

Notre modèle calcule le P&L comme une simple multiplication : $\text{P\&L} = V \times r_p$. Cette approximation est valide pour un portefeuille de positions linéaires (actions, ETF, devises, obligations sans embedded options). Pour des positions en options, le P&L est non-linéaire (effet du gamma, du vega), et une approche **full revaluation** serait nécessaire : recalculer la valeur de chaque option dans chaque scénario simulé avec un modèle de pricing.

### 3.5 Risques opérationnels et de contrepartie

Le projet se concentre exclusivement sur le **risque de marché**. En pratique, les institutions financières doivent aussi mesurer :
- Le **risque de crédit** (défaut d'une contrepartie)
- Le **risque opérationnel** (fraudes, erreurs système)
- Le **risque de liquidité** (incapacité à se financer)

Bâle III exige des charges en capital pour ces trois types de risque.

---

## 4. Extensions naturelles du projet

### 4.1 Modèle GARCH pour la volatilité conditionnelle

**Implémentation** : utiliser `arch` (bibliothèque Python) pour calibrer un modèle GARCH(1,1) sur chaque actif, puis simuler des trajectoires de 10 jours en tenant compte de la dynamique de la volatilité.

**Impact attendu** : la VaR conditionnelle serait plus haute en période de stress et plus basse en période de calme. Le backtesting serait amélioré car le modèle s'adapterait aux changements de régime.

### 4.2 Copules pour la structure de dépendance

**Implémentation** : utiliser `copulas` (bibliothèque Python) pour ajuster une copule de Student-t (ou de Clayton pour la queue gauche) aux données historiques. Générer les scénarios avec la copule plutôt qu'avec la corrélation linéaire.

**Impact attendu** : des VaR plus élevées, surtout pour les niveaux de confiance très élevés (99.5%, 99.9%), car la dépendance dans la queue gauche serait mieux capturée.

### 4.3 Scénarios de stress hypothétiques

**Implémentation** : définir dans `config.yaml` des scénarios de choc par actif (ex: SPY -20%, AGG +5%, GLD +15%, EURUSD -5%) et calculer le P&L du portefeuille sous chaque scénario.

**Intérêt** : ces analyses de "what-if" sont très utiles pour la communication aux clients et aux régulateurs, et pour tester la robustesse du portefeuille à des événements spécifiques.

### 4.4 Rééquilibrage dynamique

**Implémentation** : modifier `simulation.py` pour simuler des trajectoires de 10 jours où les poids sont rééquilibrés chaque jour (ou lorsqu'ils s'écartent trop des cibles).

**Impact attendu** : la VaR à 10 jours serait différente — potentiellement plus faible car le rééquilibrage contraint les dérives de poids.

### 4.5 Extension à un plus grand univers d'actifs

Ajouter des actifs : obligations d'entreprises (LQD), immobilier (VNQ), marchés émergents (EEM), pétrole (USO), cryptomonnaies (BTC). Cela nécessite une gestion plus soignée de la matrice de covariance (régularisation Ledoit-Wolf si $n$ devient grand) et de la liquidité.

### 4.6 Interface web ou tableau de bord

Transformer le projet en une application interactive (Streamlit, Dash) où un utilisateur peut modifier les poids et l'horizon en temps réel et voir les métriques se mettre à jour. Ce serait une démonstration forte pour un entretien.

### 4.7 Machine learning pour la prévision de la VaR

Au lieu de supposer une distribution paramétrique, utiliser un modèle de forêts aléatoires ou de réseau de neurones récurrent (LSTM) pour prédire directement la VaR conditionnelle à $t+1$ en fonction des caractéristiques observées à $t$ (rendement récent, VIX, spread de crédit, etc.).

---

## 5. Mise en perspective : ce que la VaR ne capte pas

### 5.1 Les événements de type "cygne noir"

Les "black swans" de Nassim Taleb sont des événements extrêmes, rares et imprévisibles. Le 11 septembre 2001, la crise Lehman (2008), le Flash Crash (2010), et le COVID (2020) étaient tous considérés comme pratiquement impossibles avant qu'ils ne surviennent. Aucun modèle de VaR historique ou paramétrique ne peut les anticiper par définition.

### 5.2 La VaR comme outil de communication

La VaR est souvent critiquée en tant que mesure de risque (elle ne mesure pas la perte au-delà du quantile), mais elle reste indispensable comme outil de **communication** : elle exprime le risque en unités monétaires compréhensibles par des non-spécialistes. La plupart des professionnels du risque utilisent à la fois la VaR et l'ES, les stress tests et des mesures qualitatives.

### 5.3 Le paradoxe de Goodhart

"When a measure becomes a target, it ceases to be a good measure." En finance, les banques qui gèrent leur risque en minimisant leur VaR peuvent inadvertamment concentrer leur portefeuille dans des actifs qui ont la même VaR faible mais dont les corrélations augmentent en période de crise — exactement le moment où on en a le plus besoin. La réglementation fondée sur la VaR peut créer des incitations perverses.

---

## Résumé des limites et extensions

| Limitation | Sévérité | Extension proposée |
|------------|----------|-------------------|
| Stationnarité | Élevée | Fenêtre glissante, régimes markoviens |
| i.i.d. rendements | Moyenne | GARCH(1,1) pour volatilité conditionnelle |
| Portefeuille statique | Moyenne | Simulation avec rééquilibrage dynamique |
| Corrélation linéaire | Moyenne | Copules de Student-t ou Clayton |
| Gaussianité (déjà partiellement corrigée) | Faible à moyenne | Déjà corrigée par Student-t |
| Pas de scénarios historiques | Faible | Module de stress testing |
| Incertitude sur les paramètres | Faible | Bootstrap des intervalles de confiance |
| Liquidité parfaite | Faible (pour ETF) | LVaR pour actifs illiquides |
