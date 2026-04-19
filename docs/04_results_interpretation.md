# Apprendre à lire les résultats

## Introduction

Calculer une VaR est une chose. Savoir l'interpréter, la communiquer et en tirer des conclusions pertinentes en est une autre. Ce document vous apprend à lire les résultats produits par notre moteur, à comprendre ce qu'ils signifient vraiment, et à éviter les pièges d'interprétation courants.

---

## 1. Le tableau récapitulatif VaR / ES

### Notre tableau de résultats

| Méthode              | VaR 95%    | VaR 99%    | ES 95%     | ES 99%     |
|----------------------|------------|------------|------------|------------|
| Historique           | 9 590 EUR  | 13 795 EUR | —          | —          |
| Paramétrique (Gauss) | 9 277 EUR  | 13 059 EUR | —          | —          |
| Monte Carlo          | 9 372 EUR  | 13 162 EUR | 11 712 EUR | 14 993 EUR |

Portefeuille de 1 000 000 EUR, horizon 1 jour.

### Comment lire ce tableau

**Ligne par ligne** :
- La VaR historique à 99% (13 795 EUR) signifie que sur les 1008 jours historiques observés, seulement 10 jours (1%) ont vu une perte supérieure à 13 795 EUR.
- La VaR paramétrique à 99% (13 059 EUR) est calculée par formule analytique en supposant que les rendements sont gaussiens.
- La VaR Monte Carlo à 99% (13 162 EUR) est le 99ème percentile de 50 000 scénarios simulés.

**Colonne par colonne** :
- La VaR à 95% capture les "mauvais jours ordinaires" — des pertes qu'on peut voir en moyenne une fois par mois de trading (20 jours × 5% = 1 fois par mois).
- La VaR à 99% capture les "très mauvais jours" — des pertes qu'on peut voir environ 2,5 fois par an (252 jours × 1% ≈ 2,5 fois).

### La convergence des trois méthodes

Que les trois méthodes donnent des résultats proches (9 277 à 9 590 EUR à 95%, 13 059 à 13 795 EUR à 99%) est un **signal positif de robustesse**. Cela indique que :

1. La distribution des rendements de ce portefeuille est raisonnablement proche d'une gaussienne (pas de queues trop épaisses)
2. La période historique est suffisamment représentative
3. Le modèle de simulation est bien calibré

Si les trois méthodes donnaient des résultats très différents (par exemple, historique à 10 000 EUR et MC à 20 000 EUR), cela indiquerait soit un problème de calibration, soit une structure de rendements fortement non-gaussienne.

### L'écart entre méthodes : que nous dit-il ?

**Historique > Monte Carlo** à 99% (13 795 vs 13 162) :
Cet écart de ~5% est normal. La VaR historique est sensible à la présence d'un ou deux jours de crise dans la fenêtre historique (qui "tendent" la queue). La VaR MC lisse cet effet grâce aux 50 000 scénarios.

**Paramétrique < Monte Carlo** (13 059 vs 13 162) :
La VaR MC est légèrement supérieure à la VaR paramétrique. Cela indique que notre distribution simulée (Student-t) a des queues légèrement plus épaisses que la gaussienne, ce qui se traduit par une VaR plus élevée dans les scénarios extrêmes.

---

## 2. L'Expected Shortfall : aller au-delà de la VaR

### Nos résultats ES

| Niveau | VaR MC     | ES MC      | Dépassement moyen | Ratio ES/VaR |
|--------|------------|------------|-------------------|--------------|
| 95%    | 9 372 EUR  | 11 712 EUR | +2 340 EUR        | 1.25         |
| 99%    | 13 162 EUR | 14 993 EUR | +1 831 EUR        | 1.14         |

### Ce que signifient ces chiffres

**L'ES à 95% = 11 712 EUR** signifie : dans les 5% pires scénarios (soit environ 1 jour sur 20), on perd en moyenne 11 712 EUR. La dispersion est grande : certains de ces jours on perd "seulement" 9 400 EUR (juste au-dessus de la VaR), d'autres on perd 15 000 ou 20 000 EUR.

**L'ES à 99% = 14 993 EUR** signifie : dans les 1% pires scénarios (soit environ 2 à 3 jours par an), on perd en moyenne 14 993 EUR. C'est 1 831 EUR de plus que ce que la VaR laissait entendre.

### Pourquoi l'ES à 99% est plus proche de la VaR à 99% qu'à 95% ?

C'est contre-intuitif mais correct. Le ratio ES/VaR diminue quand le niveau de confiance augmente : 1.25 à 95% contre 1.14 à 99%.

**Explication** : à 95%, il reste beaucoup de scénarios dans la queue (5% = 2 500 scénarios sur 50 000), et ils sont très dispersés (allant de la VaR jusqu'aux pires cas extrêmes). À 99%, la queue est plus concentrée (1% = 500 scénarios), et le "saut" entre la VaR et l'ES est relativement plus petit. Mathématiquement, le ratio ES/VaR tend vers 1 quand $\alpha \to 1$.

### Ce que l'ES apporte que la VaR ne donne pas

Imaginons deux portefeuilles A et B avec la même VaR à 99% de 13 000 EUR :

- Portefeuille A : dans les 1% pires cas, perd entre 13 000 et 14 000 EUR (queue fine)
- Portefeuille B : dans les 1% pires cas, perd entre 13 000 et 50 000 EUR avec une probabilité faible de 40 000+ EUR (queue épaisse)

La VaR ne distingue pas A et B. L'ES distingue : ES(A) ≈ 13 500 EUR, ES(B) ≈ 18 000 EUR. Portefeuille B est bien plus dangereux.

---

## 3. La distribution P&L : comment lire l'histogramme

### Description du graphique

Le graphique `pnl_distribution.png` montre :
- **L'histogramme** des 50 000 P&L simulés (en EUR). La forme est approximativement en cloche, centrée légèrement au-dessus de 0 (rendement espéré légèrement positif).
- **La ligne rouge pointillée** (VaR à 99%) à -13 162 EUR : à gauche de cette ligne se trouvent les 500 pires scénarios (1%).
- **La ligne orange pointillée** (VaR à 95%) à -9 372 EUR : à gauche se trouvent les 2 500 pires scénarios (5%).
- **La zone rouge ombrée** à l'extrême gauche : c'est la région des pertes extrêmes que mesure l'ES à 99%.

### Ce qu'on doit remarquer sur ce graphique

**1. La queue gauche est plus épaisse que la queue droite**
La distribution n'est pas parfaitement symétrique. La queue gauche (pertes extrêmes) s'étend plus loin que la queue droite (gains extrêmes). C'est la signature de l'asymétrie négative (skewness < 0) des marchés financiers : les krachs sont plus violents que les bulles.

**2. Le pic central est aigu**
La distribution est leptokurtique : plus haute au centre et plus épaisse dans les queues qu'une gaussienne de même variance. Beaucoup de journées sont "tranquilles" (rendement proche de 0) et de rares journées sont "catastrophiques".

**3. La VaR n'est pas dans la queue extrême**
La VaR à 99% (ligne rouge) n'est pas du tout au bout de la queue gauche — il y a des scénarios beaucoup plus extrêmes. C'est précisément ce que l'ES mesure : la profondeur de cette queue extrême.

---

## 4. La heatmap des corrélations

### Comment lire ce graphique

La heatmap affiche la matrice de corrélation $5 \times 5$ de nos actifs, avec un gradient de couleur allant du bleu foncé (corrélation -1) au rouge foncé (corrélation +1), en passant par le blanc (corrélation 0).

**Ce qu'on s'attend à voir** :
- **Diagonale rouge** : chaque actif est parfaitement corrélé avec lui-même (corrélation = 1)
- **SPY-EFA rouge vif** : les deux ETF actions sont fortement corrélés (~0.80)
- **SPY-AGG bleu/blanc** : actions et obligations peu ou négativement corrélées
- **GLD légèrement bleu** : l'or est peu corrélé avec les autres actifs

### Ce que les corrélations impliquent pour la VaR

La VaR du portefeuille (13 162 EUR) est nettement inférieure à la somme des VaR individuelles. Si tous les actifs avaient une corrélation de 1, la VaR serait la somme pondérée des VaR individuelles — bien plus élevée. Les corrélations faibles (et parfois négatives) entre obligations, or et actions créent un **bénéfice de diversification** considérable.

**Attention au piège des corrélations stables** : ces corrélations sont estimées en période normale. En période de crise (2008, 2020), les corrélations entre actifs risqués tendent à se rapprocher de 1 — c'est précisément quand on a le plus besoin de diversification qu'elle disparaît. La heatmap ne montre qu'une photo en conditions normales.

---

## 5. Les graphiques de sensibilité

### Sensibilité à la volatilité

Ce graphique montre la VaR en fonction d'un facteur de choc appliqué à toutes les volatilités. Sous hypothèse gaussienne, la relation est **linéaire** : multiplier les volatilités par 2 multiplie la VaR par 2.

**Ce qu'on doit retenir** : si la volatilité de marché double (comme pendant une crise), notre VaR double aussi. Une VaR de 13 162 EUR en conditions normales devient ~26 000 EUR en conditions de stress avec une volatilité doublée.

**Lecture pratique** : ce graphique aide à comprendre l'impact d'un régime de forte volatilité (type VIX à 40 vs VIX à 15).

### Sensibilité à la corrélation

Ce graphique montre la VaR en fonction du niveau de corrélation uniforme entre actifs. La relation est **croissante et convexe** : augmenter les corrélations augmente la VaR, et l'effet s'accélère quand les corrélations approchent de 1.

**Cas extrêmes** :
- Corrélation 0 : chaque actif est indépendant, la diversification joue à plein
- Corrélation 1 : pas de diversification, la VaR est maximale

**Interprétation** : ce graphique illustre visuellement le "risque de corrélation" — le risque que les corrélations montent en période de crise et que la diversification disparaisse.

### Sensibilité à l'horizon

Ce graphique montre la VaR en fonction de l'horizon $T$ (1, 5, 10, 20 jours). La croissance suit la **règle de la racine carrée** : $\text{VaR}(T) = \text{VaR}(1) \times \sqrt{T}$.

| Horizon | Facteur $\sqrt{T}$ | VaR estimée |
|---------|--------------------|-------------|
| 1 jour  | 1.00               | 13 162 EUR  |
| 5 jours | 2.24               | 29 483 EUR  |
| 10 jours| 3.16               | 41 592 EUR  |
| 20 jours| 4.47               | 58 834 EUR  |

**Ce que ça signifie** : le risque croît avec le temps, mais de moins en moins vite (racine carrée, pas linéaire). Sur 20 jours, on risque 4.47 fois plus que sur 1 jour, pas 20 fois plus.

### Sensibilité au niveau de confiance

Ce graphique montre la VaR en fonction du niveau de confiance (de 90% à 99.9%). La courbe est **croissante et convexe** : pour aller de 95% à 99%, la VaR augmente modérément (+40%) ; pour aller de 99% à 99.9%, elle augmente beaucoup plus (+50% supplémentaires).

**Ce que ça signifie** : les événements très rares sont très coûteux. La VaR à 99.9% est une mesure de stress extrême — pertinente pour la réassurance ou les stress tests réglementaires, pas pour le pilotage quotidien.

---

## 6. Les graphiques d'attribution marginale

### Barres d'attribution

Le graphique `marginal_contribution.png` montre la contribution de chaque actif au risque total (VaR), en EUR et en pourcentage.

**Lecture** : un actif dont la contribution est de 30% signifie que si on supprimait cet actif du portefeuille (en le remplaçant par du cash), la VaR baisserait d'environ 30%.

**Ce qu'on s'attend à voir** :
- SPY (30% du portefeuille) contribue probablement plus que ses 30% en valeur, car c'est l'actif le plus volatil
- AGG (25% en obligations) contribue probablement moins que ses 25%, car les obligations sont peu volatiles et peu corrélées
- EURUSD (10%) contribue peu, car le forex est peu corrélé avec le reste

### Implication pour la gestion du risque

Si l'analyse révèle que SPY contribue à 50% du risque tout en représentant 30% du portefeuille, cela suggère une **surdiversification insuffisante** sur les actions US. Un gestionnaire pourrait vouloir réduire SPY ou acheter une protection (put sur S&P 500).

---

## 7. Les résultats de backtesting

### Notre tableau de backtesting

| Niveau de confiance | Jours backtestés | Exceptions observées | Taux observé | Taux théorique | Décision    |
|---------------------|------------------|----------------------|--------------|----------------|-------------|
| 95%                 | 1008             | 51                   | 5.06%        | 5.00%          | VALIDE (H₀) |
| 99%                 | 1008             | 11                   | 1.09%        | 1.00%          | VALIDE (H₀) |

### Comment interpréter "VALIDE"

"VALIDE" signifie que l'écart entre le taux observé et le taux théorique est statistiquement non significatif au niveau de 5%. En d'autres termes : l'écart peut s'expliquer par le hasard seul (fluctuations d'échantillonnage), sans qu'il soit nécessaire de remettre en cause le modèle.

**Ce que ça ne signifie pas** : "VALIDE" ne signifie pas que le modèle est parfait ou qu'il ne peut pas échouer dans le futur. C'est une validation sur la période backtestée (les 1008 jours de données historiques).

### Nuances importantes

**51 exceptions à 95%** : on en attendait $1008 \times 5\% = 50.4$ en théorie. On en observe 51. L'écart est d'exactement $+0.6$ exception — négligeable.

**11 exceptions à 99%** : on en attendait $1008 \times 1\% = 10.08$ en théorie. On en observe 11. L'écart est de $+0.92$ exception — là aussi négligeable.

**Un modèle trop conservateur** (trop peu d'exceptions) serait aussi problématique qu'un modèle trop optimiste : il immobiliserait inutilement du capital en exigeant des réserves excessives.

### Ce que le backtesting ne teste pas

Le test de Kupiec teste uniquement le **taux global** d'exceptions, pas leur clustering. Il est possible d'avoir 51 exceptions à 95% mais que ces 51 jours arrivent tous consécutivement lors d'une crise (ce serait un très mauvais signe, signe que les corrélations ont changé de régime). Le test de Christoffersen, non implémenté ici, testerait également l'indépendance des exceptions.

---

## 8. Pièges d'interprétation fréquents

### Piège 1 : "La VaR est la perte maximale"

**FAUX.** La VaR à 99% signifie que la perte **peut dépasser** ce montant avec 1% de probabilité. Dans ces 1% de cas extrêmes, la perte peut être beaucoup plus élevée. C'est exactement ce que mesure l'ES.

**Comment l'éviter** : toujours dire "la perte ne dépassera pas X avec une probabilité de 99%", jamais "la perte maximale est X".

### Piège 2 : "Une VaR plus élevée = un portefeuille plus risqué"

Ceci n'est pas toujours vrai si l'on compare des portefeuilles de tailles différentes. La VaR en euros dépend de la valeur du portefeuille. Un portefeuille de 2 millions avec une VaR de 20 000 EUR a le même risque **relatif** qu'un portefeuille de 1 million avec une VaR de 10 000 EUR.

**Comment l'éviter** : toujours exprimer la VaR aussi en pourcentage de la valeur du portefeuille. Notre VaR MC à 99% = 13 162 EUR = **1.32%** du portefeuille.

### Piège 3 : "La VaR historique est la plus fiable car elle utilise des vraies données"

La VaR historique est limitée aux événements passés. Si une crise sans précédent se produit, la VaR historique ne peut pas l'anticiper. De plus, elle est **très sensible à la fenêtre** : inclure la crise COVID de mars 2020 dans la fenêtre donne une VaR historique beaucoup plus élevée qu'une fenêtre qui l'exclut.

**Comment l'éviter** : considérer les trois méthodes comme complémentaires, pas comme concurrentes. La VaR historique capture les événements réels passés, la VaR MC explore des scénarios au-delà du passé.

### Piège 4 : "Le modèle est validé, donc il est correct"

Le test de Kupiec valide le modèle sur la période historique testée. Il ne garantit pas la validité future. Les modèles de VaR ont régulièrement échoué lors de crises (2008, 2020) car leurs hypothèses de stationnarité et de gaussianité étaient violées.

**Comment l'éviter** : compléter le backtesting statistique par des stress tests (scénarios de crise hypothétiques) et des reverse stress tests (quels scénarios rendraient le portefeuille insolvable ?).

### Piège 5 : "Notre VaR est conservative parce que nous utilisons la distribution Student-t"

La Student-t donne des queues plus épaisses que la gaussienne, donc une VaR plus élevée — c'est vrai. Mais une VaR plus élevée n'est pas synonyme de "meilleure" : elle immobilise plus de capital. Une VaR correcte est une VaR calibrée pour refléter fidèlement le vrai risque, ni trop haute ni trop basse.

---

## 9. Comment commenter les résultats à l'oral

### Formulation recommandée

Au lieu de dire :
> "La VaR est de 13 162 euros."

Dire :
> "Notre modèle estime qu'avec une probabilité de 99%, le portefeuille ne perdra pas plus de **13 162 euros en une journée**, soit **1,32% de sa valeur**. En d'autres termes, sur 100 jours de trading, on s'attend à observer au maximum une journée où la perte dépasse ce seuil."

Pour l'ES :
> "Dans les 1% pires scénarios, la perte moyenne est de **14 993 euros**, soit environ **1 831 euros de plus** que la VaR ne le laissait entendre. C'est une information importante : la VaR fixe un seuil, mais l'ES indique ce qu'on risque vraiment si on franchit ce seuil."

Pour le backtesting :
> "Sur 1008 jours historiques, on a observé 51 exceptions à la VaR à 95% contre 50,4 attendues théoriquement. Cet écart est statistiquement non significatif selon le test de Kupiec — le modèle est donc **validé empiriquement** sur la période d'estimation."

### Réponses aux questions difficiles

**Q : "Est-ce que votre portefeuille est bien diversifié ?"**

Réponse : "La convergence des trois méthodes (historique, paramétrique, Monte Carlo) et les résultats de l'attribution marginale suggèrent une diversification raisonnable. Le bénéfice de diversification peut être estimé en comparant notre VaR de 13 162 EUR à la somme des VaR individuelles pondérées, qui serait significativement plus élevée. Cependant, la diversification disparaît en période de crise quand les corrélations augmentent — c'est une limite connue de notre approche."

**Q : "Quelle méthode vous fait le plus confiance ?"**

Réponse : "Les trois méthodes sont complémentaires. Je fais confiance à leur convergence : le fait qu'elles donnent des résultats proches (9 277 à 9 590 EUR à 95%) renforce la fiabilité de l'estimation. Si elles divergeaient significativement, ce serait un signal d'alerte. La méthode Monte Carlo avec Student-t est conceptuellement la plus riche car elle capture les queues épaisses, mais elle dépend de la qualité de la calibration."
