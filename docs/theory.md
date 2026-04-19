# Documentation théorique : VaR et Expected Shortfall

## 1. Introduction et contexte réglementaire

### 1.1 Pourquoi mesurer le risque de marché ?

La gestion du risque de marché est au cœur de toute activité financière institutionnelle. Les banques, compagnies d'assurance et fonds de gestion sont exposés à des mouvements défavorables des prix de marché — actions, obligations, devises, matières premières. Quantifier cette exposition est une exigence à la fois prudentielle (protection contre la faillite), réglementaire (Bâle III, Solvabilité II) et économique (optimisation du capital alloué).

### 1.2 L'histoire de la VaR

La Value at Risk (VaR) a été popularisée par J.P. Morgan en 1994 avec le système RiskMetrics, qui permettait pour la première fois à une grande banque de synthétiser son exposition globale au risque de marché en un seul chiffre. Cette approche, simple et communicable, a rapidement été adoptée par l'industrie et institutionnalisée par le Comité de Bâle dans l'Amendement de 1996 (Bâle I, risque de marché).

Bâle II (2004) a renforcé les exigences en imposant une VaR à 99% sur 10 jours comme base du calcul de capital réglementaire. La crise financière de 2008 a révélé les limites de cet outil — notamment son incapacité à capturer les risques de queue extrême et les corrélations de crise. Bâle III (2010, renforcé par la FRTB en 2016) a officiellement remplacé la VaR par l'Expected Shortfall à 97.5% comme mesure de risque de référence.

---

## 2. La Value at Risk (VaR)

### 2.1 Définition formelle

Soit $V$ la valeur d'un portefeuille et $\Delta V = V_{t+1} - V_t$ la variation de valeur sur un horizon $\Delta t$. La **perte** est $L = -\Delta V$. Soit $F_L$ la fonction de distribution cumulative de $L$.

**Définition** : La VaR au niveau de confiance $\alpha \in (0,1)$ est le quantile d'ordre $\alpha$ de la distribution des pertes :

$$\text{VaR}_\alpha = F_L^{-1}(\alpha) = \inf\{l \in \mathbb{R} : P(L \leq l) \geq \alpha\}$$

**Interprétation** : avec probabilité $\alpha$, la perte ne dépassera pas $\text{VaR}_\alpha$. Avec probabilité $1-\alpha$, la perte sera supérieure à $\text{VaR}_\alpha$.

**Exemple** : $\text{VaR}_{99\%} = 13\,162$ EUR sur 1 000 000 EUR signifie $P(L \leq 13\,162) = 99\%$, c'est-à-dire $P(L > 13\,162) = 1\%$.

### 2.2 Paramètres de la VaR

La VaR dépend de trois paramètres :

1. **Le portefeuille** : sa valeur $V$ et sa composition (actifs et poids $\mathbf{w}$)
2. **L'horizon** $\Delta t$ : typiquement 1 jour (trading), 10 jours (réglementaire), ou 1 mois
3. **Le niveau de confiance** $\alpha$ : typiquement 95% (gestion interne) ou 99% (réglementaire Bâle II)

### 2.3 Interprétation économique

La VaR répond à la question : "Quel est le capital minimum à mettre en réserve pour que la probabilité de ruine sur un horizon donné soit au plus $1-\alpha$ ?" C'est une mesure de risque de liquidation : si le portefeuille perd plus que sa VaR en un jour, cela peut déclencher des appels de marge ou des problèmes de liquidité.

---

## 3. Méthodes de calcul de la VaR

### 3.1 Méthode historique

**Principe** : utiliser la distribution empirique des rendements historiques comme proxy de la distribution future.

**Algorithme** :
1. Collecter les rendements journaliers $r_1, \ldots, r_T$ sur une fenêtre historique
2. Calculer les P&L : $\text{P\&L}_t = V \times r_t$, les pertes $L_t = -\text{P\&L}_t$
3. $\text{VaR}_\alpha^{hist} = Q_\alpha(L_1,\ldots,L_T)$ = quantile empirique d'ordre $\alpha$

**Hypothèse fondamentale** : la distribution future des rendements est identique à la distribution historique observée (stationnarité et représentativité de la fenêtre).

**Résultats obtenus** :
- VaR historique 95% = 9 590 EUR
- VaR historique 99% = 13 795 EUR

### 3.2 Méthode paramétrique (Delta-Normal)

**Principe** : supposer que les rendements du portefeuille suivent une loi normale et utiliser la formule analytique du quantile.

**Formule** : si $r_p \sim \mathcal{N}(\mu_p, \sigma_p^2)$, alors :
$$\text{VaR}_\alpha^{param} = V(z_\alpha \sigma_p - \mu_p)$$

où $z_\alpha = \Phi^{-1}(\alpha)$ est le quantile de la loi normale standard, $\mu_p = \mathbf{w}^\top\boldsymbol{\mu}$ et $\sigma_p = \sqrt{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}$.

**Valeurs des quantiles** :
- $z_{0.95} = \Phi^{-1}(0.95) = 1.6449$
- $z_{0.99} = \Phi^{-1}(0.99) = 2.3263$

**Résultats obtenus** :
- VaR paramétrique 95% = 9 277 EUR
- VaR paramétrique 99% = 13 059 EUR

### 3.3 Méthode Monte Carlo

**Principe** : simuler un grand nombre de scénarios de rendements futurs et calculer la VaR comme quantile empirique de la distribution simulée.

**Algorithme** :
1. Calibrer les paramètres $\boldsymbol{\mu}$, $\boldsymbol{\Sigma}$ (et $\nu$ pour Student-t)
2. Calculer $L = \text{Cholesky}(\boldsymbol{\Sigma})$
3. Pour $i = 1, \ldots, N$ : générer $\mathbf{z}_i \sim \mathcal{N}(0, I_n)$, poser $\mathbf{r}_i = \boldsymbol{\mu} + L\mathbf{z}_i$
4. Calculer $L_i = -V \cdot \mathbf{w}^\top\mathbf{r}_i$
5. $\text{VaR}_\alpha^{MC} = Q_\alpha(L_1,\ldots,L_N)$

**Résultats obtenus** :
- VaR Monte Carlo 95% = 9 372 EUR
- VaR Monte Carlo 99% = 13 162 EUR

---

## 4. L'Expected Shortfall (ES)

### 4.1 Définition formelle

$$\text{ES}_\alpha = E[L \mid L > \text{VaR}_\alpha] = \frac{E[L \cdot \mathbf{1}_{L > \text{VaR}_\alpha}]}{P(L > \text{VaR}_\alpha)}$$

Représentation intégrale :
$$\text{ES}_\alpha = \frac{1}{1-\alpha}\int_\alpha^1 \text{VaR}_u \, du$$

### 4.2 Formule analytique sous hypothèse gaussienne

Si $L \sim \mathcal{N}(\mu_L, \sigma_L^2)$ :
$$\text{ES}_\alpha = \mu_L + \sigma_L \cdot \frac{\phi(z_\alpha)}{1-\alpha}$$

### 4.3 Cohérence axiomatique

L'ES satisfait les quatre axiomes d'une mesure de risque cohérente (Artzner, Delbaen, Eber, Heath, 1999) : monotonie, invariance par translation, homogénéité positive, et **sous-additivité**. La VaR satisfait les trois premiers mais peut violer la sous-additivité.

### 4.4 Résultats obtenus

- ES Monte Carlo 95% = 11 712 EUR (ratio ES/VaR = 1.25)
- ES Monte Carlo 99% = 14 993 EUR (ratio ES/VaR = 1.14)

---

## 5. La distribution des rendements

### 5.1 Hypothèse gaussienne

La distribution gaussienne multivariée $\mathbf{r} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$ est l'hypothèse de base pour plusieurs raisons : elle est entièrement caractérisée par ses deux premiers moments, elle est stable par combinaison linéaire (le rendement du portefeuille est aussi gaussien), et elle conduit à des formules analytiques simples pour la VaR et l'ES.

**Limites** : la loi normale prédit beaucoup moins d'événements extrêmes que ce qu'on observe en pratique (fat tails empiriques). Elle ignore l'asymétrie négative des rendements d'actions (les baisses sont plus brusques que les hausses).

### 5.2 Distribution de Student-t

La distribution de Student-t multivariée avec $\nu$ degrés de liberté est une généralisation de la gaussienne avec des queues plus épaisses. Sa densité est :

$$f(\mathbf{x}) = \frac{\Gamma\left(\frac{\nu+n}{2}\right)}{\Gamma\left(\frac{\nu}{2}\right)(\nu\pi)^{n/2}|\boldsymbol{\Sigma}|^{1/2}} \left(1 + \frac{(\mathbf{x}-\boldsymbol{\mu})^\top\boldsymbol{\Sigma}^{-1}(\mathbf{x}-\boldsymbol{\mu})}{\nu}\right)^{-\frac{\nu+n}{2}}$$

Pour $\nu = 5$ (typique pour des actions), le quantile à 1% est 45% plus élevé que sous la gaussienne — impliquant une VaR significativement plus élevée.

---

## 6. Quantiles et distribution des P&L

### 6.1 La fonction de distribution cumulative

Pour un portefeuille de rendement $r_p \sim F$, la perte $L = -V \cdot r_p$ a une CDF :
$$F_L(l) = P(L \leq l) = P(r_p \geq -l/V) = 1 - F_{r_p}(-l/V)$$

La VaR est l'inverse de cette CDF :
$$\text{VaR}_\alpha = F_L^{-1}(\alpha) = -V \cdot F_{r_p}^{-1}(1-\alpha)$$

### 6.2 Relation entre niveaux de confiance et VaR

| Niveau $\alpha$ | Probabilité de dépassement | Fréquence approximative |
|-----------------|---------------------------|-------------------------|
| 90%             | 10%                       | 1 fois sur 10 jours (2×/mois) |
| 95%             | 5%                        | 1 fois sur 20 jours (1×/mois) |
| 99%             | 1%                        | ~2.5 fois par an |
| 99.9%           | 0.1%                      | ~0.25 fois par an |

### 6.3 Impact du niveau de confiance sur nos résultats

La VaR croît avec le niveau de confiance selon la forme de la queue de distribution :

| Niveau | VaR MC     | ES MC      |
|--------|------------|------------|
| 95%    | 9 372 EUR  | 11 712 EUR |
| 99%    | 13 162 EUR | 14 993 EUR |

L'augmentation de VaR de 95% à 99% (+41%) est légèrement supérieure à ce que prédit la loi normale (+41.4% : ratio des quantiles $z_{0.99}/z_{0.95} = 2.326/1.645 = 1.414$). La légère sur-estimation confirme la présence de queues légèrement plus épaisses que gaussien.

---

## 7. Lien avec le risk management bancaire (Bâle III)

### 7.1 Le capital réglementaire en risque de marché

Sous Bâle II, le capital minimum en risque de marché était :
$$K = \max\left(\text{VaR}_{99\%, 10j}^{t-1}, \frac{m_c}{60}\sum_{i=1}^{60}\text{VaR}_{99\%, 10j}^{t-i}\right)$$

où $m_c \geq 3$ est un facteur multiplicateur qui peut monter jusqu'à 4 en cas de mauvais backtesting.

### 7.2 La réforme FRTB (Bâle III)

La FRTB remplace la VaR par l'Expected Shortfall à 97.5% sur 10 jours, calibrée en période de stress :
- Mesure principale : ES à 97.5% (stress ES)
- Backtesting à 97.5% et 99% (deux seuils)
- Distinction entre "trading book" (positions à court terme) et "banking book"

L'ES à 97.5% est numériquement proche de la VaR à 99% sous gaussienne, mais beaucoup plus sensible aux queues épaisses et aux scénarios de crise. Elle est aussi sous-additive, favorisant la diversification dans la mesure du capital.

### 7.3 Implications pour notre projet

Notre projet calcule la VaR à 95% et 99% et l'ES à 95% et 99%. Si l'on voulait se conformer strictement à Bâle III, on devrait :
- Calculer l'ES à 97.5% (pas implémenté, mais trivial à ajouter)
- Calibrer sur une période incluant une période de stress explicite (ex : 2008-2009 ou 2020)
- Appliquer la règle $\sqrt{10}$ pour l'horizon de 10 jours
- Soumettre le modèle à un backtesting formel à 97.5% et 99%

---

## 8. Synthèse théorique

La Value at Risk et l'Expected Shortfall sont des outils complémentaires pour la quantification du risque de marché :

- La **VaR** fournit un seuil de perte dépassé avec une faible probabilité. Simple à interpréter, elle est un outil de communication efficace mais présente des limites théoriques (non sous-additive, ne capture pas la queue).

- L'**ES** mesure la perte moyenne au-delà de la VaR. Théoriquement supérieure (cohérente), elle est désormais la référence réglementaire de Bâle III. Elle est plus difficile à backtester (car moins robuste statistiquement).

- La **simulation Monte Carlo** permet de calculer les deux métriques sous des hypothèses distributiónelles flexibles (notamment Student-t pour les queues épaisses), en reproduisant fidèlement la structure de corrélation du portefeuille via la décomposition de Cholesky.

- Le **backtesting de Kupiec** fournit une validation empirique statistiquement fondée : notre modèle passe ce test avec 51/1008 exceptions à 95% et 11/1008 à 99%, prouvant l'absence de biais systématique.
