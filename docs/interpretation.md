# Interprétation des résultats et conclusion

## 1. Ce que signifient nos résultats numériques

### 1.1 Les chiffres clés

Notre moteur de calcul, appliqué à un portefeuille de 1 000 000 EUR réparti entre 5 classes d'actifs, produit les résultats suivants sur un horizon d'un jour :

**Value at Risk** :

| Méthode        | VaR 95%    | VaR 99%    |
|----------------|------------|------------|
| Historique     | 9 590 EUR  | 13 795 EUR |
| Paramétrique   | 9 277 EUR  | 13 059 EUR |
| Monte Carlo    | 9 372 EUR  | 13 162 EUR |

**Expected Shortfall (Monte Carlo)** :

| Niveau | ES         |
|--------|------------|
| 95%    | 11 712 EUR |
| 99%    | 14 993 EUR |

### 1.2 Lecture de la VaR à 99%

La VaR Monte Carlo à 99% de **13 162 EUR** (soit **1,32%** du portefeuille) se lit ainsi :

> Sur 100 jours de trading ordinaires, on s'attend à ce que 99 d'entre eux se terminent avec une perte inférieure à 13 162 EUR. Un seul jour sur 100 — soit environ 2 à 3 jours par an — la perte dépassera ce seuil.

Ce chiffre doit être mis en perspective :
- En annualisé : 13 162 × $\sqrt{252}$ ≈ 208 900 EUR de VaR annuelle à 99% (hypothèse i.i.d.)
- Comme fraction du portefeuille : 1,32% par jour, soit ~21% annualisé — un niveau de risque modéré pour un portefeuille diversifié

### 1.3 Lecture de l'Expected Shortfall

L'ES à 99% de **14 993 EUR** signifie :

> Dans les 1% de scénarios les plus défavorables — environ 2 à 3 fois par an — la perte journalière moyenne est de 14 993 EUR.

L'écart entre ES et VaR à 99% (14 993 - 13 162 = 1 831 EUR) représente ce que la VaR "cachait" sur la sévérité des pertes extrêmes. C'est modeste ici car notre distribution simulée (Student-t avec $\nu \approx 6$) n'est pas extrêmement leptokurtique.

---

## 2. Signification de la convergence des trois méthodes

Le fait que les trois méthodes donnent des résultats proches est un résultat en lui-même. Analysons les écarts :

**À 95%** : historique (9 590) > MC (9 372) > paramétrique (9 277), écart max = 3,4%

**À 99%** : historique (13 795) > MC (13 162) > paramétrique (13 059), écart max = 5,6%

**Interprétation** :
- Les écarts sont faibles, ce qui valide la robustesse des estimations
- La méthode historique est systématiquement la plus haute : la fenêtre historique (incluant COVID-19 et la hausse des taux de 2022) contient des journées extrêmes qui tirent le quantile empirique vers le haut
- La méthode paramétrique est systématiquement la plus basse : la gaussienne sous-estime légèrement les queues
- La méthode Monte Carlo (Student-t) est intermédiaire : elle corrige partiellement la sous-estimation gaussienne

---

## 3. Signification du backtesting

Le backtesting Kupiec valide notre modèle : 51/1008 exceptions à 95% (5,06%) et 11/1008 à 99% (1,09%). Ces taux sont statistiquement indistinguables des taux théoriques de 5% et 1%.

**Ce résultat est encourageant car** :
- Il indique que le modèle est bien calibré — ni trop optimiste (trop peu d'exceptions) ni trop pessimiste (trop d'exceptions)
- Il est obtenu sur une période qui inclut des événements de stress significatifs (COVID-19, inflation/hausse des taux), ce qui est un test sévère

**Limite importante** : le backtesting est conduit in-sample (sur les mêmes données que l'estimation). Un test out-of-sample (estimer sur 2020-2022, tester sur 2023-2024) serait plus probant mais nécessiterait des données plus récentes.

---

## 4. Comment lire les résultats de sensibilité

### 4.1 Sensibilité à la volatilité

Un doublement de la volatilité (choc ×2) implique un doublement de la VaR paramétrique. Ce résultat est exact sous hypothèse gaussienne (la VaR est linéaire en $\sigma$). Pour la méthode Monte Carlo, la relation est aussi approximativement linéaire.

**Implication pratique** : en mars 2020, la volatilité des marchés d'actions a approximativement triplé (VIX passant de 15 à 80). Notre VaR serait passée de ~9 000 EUR à ~27 000 EUR à 95%, soit une consommation de capital multipliée par 3 en quelques semaines.

### 4.2 Sensibilité à la corrélation

Passer d'une corrélation uniforme de 0 à 0.9 augmente la VaR d'environ 50% à 60%. Ce résultat illustre l'importance cruciale de la diversification : si toutes les corrélations montaient à 1 (scenario de crise totale), la VaR atteindrait son maximum (somme pondérée des VaR individuelles).

---

## 5. Limites du projet

### 5.1 Hypothèses simplificatrices

Ce projet repose sur plusieurs hypothèses qui limitent sa portée pratique :

1. **Stationnarité** : la distribution des rendements est supposée constante dans le temps. En réalité, les régimes de marché changent.
2. **Portefeuille statique** : les poids ne changent pas. Un gérant rééquilibre son portefeuille.
3. **Corrélations constantes** : les corrélations sont estimées en période normale. En période de crise, elles augmentent (Flight to Quality).
4. **Liquidité parfaite** : on suppose pouvoir vendre sans impact de prix.

### 5.2 Ce que le projet ne mesure pas

- Le risque de crédit et de contrepartie
- Le risque de liquidité
- Le risque opérationnel
- Les effets non-linéaires (options, obligations avec embedded options)
- Le risque de modèle lui-même

---

## 6. Extensions naturelles

Les extensions les plus directement utiles seraient :

1. **GARCH(1,1)** : modéliser la volatilité conditionnelle pour des VaR qui varient quotidiennement selon l'état du marché
2. **Copules de Student-t** : mieux capturer la dépendance de queue entre actifs en période de stress
3. **Scénarios de stress historiques** : rejouer les crises de 2008, 2020 sur le portefeuille actuel
4. **Backtesting out-of-sample** : valider le modèle sur des données hors de la période d'estimation
5. **Attribution de performance** : décomposer les gains et pertes par facteur de risque

---

## 7. Conclusion

Ce projet démontre la faisabilité d'un moteur de calcul de VaR et ES en Python, robuste et entièrement paramétrable. Les résultats obtenus — VaR MC 99% à 13 162 EUR (1,32%) et ES MC 99% à 14 993 EUR pour un portefeuille de 1 million d'euros — sont cohérents entre les trois méthodes et validés statistiquement par le test de Kupiec.

La convergence des méthodes historique, paramétrique et Monte Carlo autour de valeurs proches constitue le signal de confiance le plus important : elle indique que la distribution des rendements de ce portefeuille diversifié est raisonnablement bien approximée par une loi normale ou Student-t multivariée, et que la période historique est suffisamment représentative.

Les limites identifiées (stationnarité, corrélations fixes, portefeuille statique) sont connues dans la littérature et constituent un agenda clair pour des extensions futures. En l'état, ce projet constitue une base solide et pédagogiquement complète pour comprendre et mettre en œuvre les méthodes de mesure du risque de marché les plus utilisées dans l'industrie financière.
