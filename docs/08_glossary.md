# Glossaire alphabétique

Ce glossaire recense les termes clés du projet, par ordre alphabétique. Pour chaque terme : une définition simple en une phrase, suivie d'une définition technique précise.

---

## A

### Asymétrie (Skewness)

**Définition simple** : mesure de l'inclinaison d'une distribution — positive si la queue droite est plus longue, négative si la queue gauche est plus longue.

**Définition technique** : le skewness est le troisième moment centré normalisé : $S = E\left[\left(\frac{X-\mu}{\sigma}\right)^3\right]$. Une distribution normale a un skewness de 0. Les rendements financiers présentent souvent un skewness négatif (queues gauches plus épaisses que les queues droites), reflétant l'asymétrie des krachs vs des hausses. Un skewness négatif implique que les VaR gauches (pertes) sont plus importantes que ne le prédirait une distribution symétrique.

---

### Attribution marginale du risque

**Définition simple** : décomposition du risque total du portefeuille par contribution de chaque actif.

**Définition technique** : la contribution marginale de l'actif $i$ est $\text{MC}_i = w_i \cdot \partial\text{VaR}/\partial w_i$. Par le théorème d'Euler (VaR homogène de degré 1), $\sum_i \text{MC}_i = \text{VaR}_{total}$. La contribution relative est $\text{RC}_i = \text{MC}_i/\text{VaR}$. Pour la VaR paramétrique gaussienne : $\text{MC}_i = V \cdot z_\alpha \cdot w_i(\boldsymbol{\Sigma}\mathbf{w})_i / \sigma_p$.

---

## B

### Backtesting

**Définition simple** : validation empirique d'un modèle de risque en comparant ses prédictions aux données réelles.

**Définition technique** : le backtesting d'une VaR consiste à compter le nombre d'exceptions $N$ sur $T$ périodes (jours où la perte réelle dépasse la VaR prédite). Sous un modèle correct à niveau $\alpha$, $N \sim \text{Binomiale}(T, 1-\alpha)$. Le test de Kupiec formalise cette vérification par un test du rapport de vraisemblance : $LR_{uc} = -2\ln[p^N(1-p)^{T-N}/\hat{p}^N(1-\hat{p})^{T-N}] \sim \chi^2(1)$ sous $H_0$. Voir aussi : test de Christoffersen (conditional coverage), test de Basel (zones verte/jaune/rouge).

---

### Bâle III / FRTB

**Définition simple** : cadre réglementaire international qui impose aux banques de détenir du capital proportionnel à leurs risques.

**Définition technique** : Bâle III est l'accord de réglementation bancaire du Comité de Bâle sur le contrôle bancaire. La FRTB (Fundamental Review of the Trading Book, 2016) en est la composante dédiée au risque de marché. Elle remplace la VaR à 99% sur 10 jours (Bâle II) par l'ES à 97.5% sur 10 jours (FRTB), exige une calibration en période de stress, et impose des backtestings à 97.5% et 99%.

---

### Bénéfice de diversification

**Définition simple** : réduction du risque obtenue en combinant des actifs imparfaitement corrélés.

**Définition technique** : $\text{BD} = \sum_i w_i\sigma_i - \sigma_p$, où $\sigma_p = \sqrt{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}$. Pour des corrélations strictement inférieures à 1, $\sigma_p < \sum_i w_i\sigma_i$, donc BD > 0. Le ratio de diversification est $\text{DR} = \sum_i w_i\sigma_i / \sigma_p > 1$. La diversification est le seul "repas gratuit" en finance (Markowitz).

---

## C

### Cholesky (décomposition de)

**Définition simple** : factorisation d'une matrice symétrique définie positive en un produit $LL^\top$, utilisée pour générer des vecteurs aléatoires corrélés.

**Définition technique** : toute matrice $n \times n$ symétrique définie positive $\boldsymbol{\Sigma}$ admet une unique décomposition $\boldsymbol{\Sigma} = LL^\top$ où $L$ est triangulaire inférieure à diagonale positive. Si $\mathbf{z} \sim \mathcal{N}(0, I_n)$, alors $\mathbf{x} = L\mathbf{z} + \boldsymbol{\mu} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$. C'est l'outil fondamental de la simulation Monte Carlo multivariée. L'algorithme a une complexité $O(n^3/3)$, NumPy l'implémente via `np.linalg.cholesky()`.

---

### Copule

**Définition simple** : fonction qui décrit la structure de dépendance entre variables aléatoires, séparément de leurs distributions marginales.

**Définition technique** : par le théorème de Sklar, toute distribution jointe $F(x_1,\ldots,x_n)$ s'écrit $C(F_1(x_1),\ldots,F_n(x_n))$ où $C : [0,1]^n \to [0,1]$ est une copule. Les copules de Student-t, gaussienne, Clayton, Gumbel et Frank sont couramment utilisées en finance. La copule gaussienne (corrélation de Pearson) est équivalente au modèle de Cholesky. La copule de Clayton a une dépendance de queue inférieure asymptotique, mieux adaptée aux co-chutes des marchés financiers.

---

### Covariance

**Définition simple** : mesure de la tendance de deux variables à varier ensemble dans le même sens ou des sens opposés.

**Définition technique** : $\text{Cov}(X, Y) = E[(X-E[X])(Y-E[Y])] = E[XY] - E[X]E[Y]$. La covariance est normalisée par les écarts-types pour obtenir la corrélation : $\rho_{XY} = \text{Cov}(X,Y)/(\sigma_X\sigma_Y) \in [-1,1]$. Dans notre projet, la matrice de covariance $5 \times 5$ est estimée par $\hat{\boldsymbol{\Sigma}} = \frac{1}{T-1}\sum_t(\mathbf{r}_t - \hat{\boldsymbol{\mu}})(\mathbf{r}_t - \hat{\boldsymbol{\mu}})^\top$.

---

### CVaR (Conditional Value at Risk)

**Définition simple** : synonyme d'Expected Shortfall — la perte moyenne dans les scénarios qui dépassent la VaR.

**Définition technique** : $\text{CVaR}_\alpha = E[L \mid L \geq \text{VaR}_\alpha] = \frac{1}{1-\alpha}\int_\alpha^1 \text{VaR}_u \, du$. Les termes CVaR, ES et Expected Tail Loss (ETL) désignent la même quantité pour les distributions continues. Artzner et al. (1999) préfèrent le terme ES pour distinguer ce concept de la "VaR conditionnelle" au sens large. Depuis Bâle III, le terme ES est privilégié dans les textes réglementaires.

---

## D

### Distribution de probabilité

**Définition simple** : description mathématique de la probabilité de chaque valeur possible d'une variable aléatoire.

**Définition technique** : une distribution peut être caractérisée par sa fonction de répartition (CDF) $F(x) = P(X \leq x)$, sa densité (PDF) $f(x) = F'(x)$, ou sa fonction de masse (PMF) pour les distributions discrètes. En finance, les rendements sont modélisés par des distributions continues : normale $\mathcal{N}(\mu, \sigma^2)$, Student-t $t_\nu(\mu, \Sigma)$, ou des distributions non-paramétriques (VaR historique).

---

### Distribution de Student-t

**Définition simple** : généralisation de la loi normale avec des queues plus épaisses, paramétrée par le nombre de degrés de liberté $\nu$.

**Définition technique** : une variable $X \sim t_\nu(\mu, \sigma^2)$ a une densité $f(x) = \frac{\Gamma((\nu+1)/2)}{\sqrt{\nu\pi}\sigma\Gamma(\nu/2)}\left(1+\frac{(x-\mu)^2}{\nu\sigma^2}\right)^{-(\nu+1)/2}$. Pour $\nu > 2$, la variance est $\frac{\nu}{\nu-2}\sigma^2$. Pour $\nu > 4$, le kurtosis est $3 + 6/(\nu-4)$ (excès de kurtosis $= 6/(\nu-4)$). Quand $\nu \to \infty$, on retrouve $\mathcal{N}(\mu,\sigma^2)$. Des valeurs typiques en finance : $\nu = 4$ (très leptokurtique) à $\nu = 8$ (modérément leptokurtique).

---

## E

### ES (Expected Shortfall)

**Définition simple** : perte moyenne dans les scénarios qui dépassent la VaR, aussi appelée CVaR.

**Définition technique** : $\text{ES}_\alpha = E[L \mid L > \text{VaR}_\alpha] = \frac{E[L \cdot \mathbf{1}_{L > \text{VaR}_\alpha}]}{1-\alpha}$. Sous hypothèse gaussienne : $\text{ES}_\alpha = \mu_L + \sigma_L \cdot \phi(z_\alpha)/(1-\alpha)$ où $\phi$ est la densité standard normale. L'ES est une mesure de risque cohérente (sous-additive), contrairement à la VaR. Dans notre projet, ES MC 99% = 14 993 EUR.

---

## G

### GARCH (Generalized Autoregressive Conditional Heteroskedasticity)

**Définition simple** : modèle qui capture la volatilité variable dans le temps et la persistance des chocs de marché.

**Définition technique** : le modèle GARCH(1,1) de Bollerslev (1986) spécifie : $r_t = \mu + \epsilon_t$, $\epsilon_t = \sigma_t z_t$, $z_t \sim \mathcal{N}(0,1)$ i.i.d., $\sigma_t^2 = \omega + \alpha\epsilon_{t-1}^2 + \beta\sigma_{t-1}^2$ avec $\omega > 0$, $\alpha, \beta \geq 0$, $\alpha + \beta < 1$. La condition $\alpha + \beta < 1$ assure la stationnarité de la variance. Le paramètre $\beta$ mesure la persistance de la volatilité : $\beta \approx 0.9$ (très persistant, typique des actions). L'extension DCC-GARCH (Engle, 2002) modélise les corrélations dynamiques.

---

## H

### Hypothèse i.i.d.

**Définition simple** : supposer que les observations successives sont indépendantes et de même distribution.

**Définition technique** : des variables $X_1, X_2, \ldots$ sont i.i.d. si elles sont mutuellement indépendantes ($X_i \perp X_j$ pour $i \neq j$) et ont la même loi marginale. Pour les rendements financiers, l'hypothèse i.i.d. est approximative : elle est violée par le clustering de volatilité (autocorrélation de $|r_t|$) et par les corrélations intertemporelles. Elle justifie la règle $\sqrt{T}$ et la validité du MLE standard.

---

## K

### Kurtosis

**Définition simple** : mesure de la "lourdeur" des queues d'une distribution par rapport à la loi normale.

**Définition technique** : le kurtosis est le quatrième moment centré normalisé : $\kappa = E\left[\left(\frac{X-\mu}{\sigma}\right)^4\right]$. La loi normale a $\kappa = 3$. L'excès de kurtosis est $\kappa - 3$. Une distribution avec excès de kurtosis positif est leptokurtique (queues épaisses, pic central élevé). Les rendements journaliers d'actions ont typiquement $\kappa \in [5, 12]$, soit un excès de kurtosis de 2 à 9.

---

### Kupiec (test de)

**Définition simple** : test statistique qui vérifie si le taux d'exceptions observé dans un backtesting est compatible avec le taux théorique du modèle.

**Définition technique** : Kupiec (1995) propose $LR_{uc} = -2\ln\left[\frac{p_0^N(1-p_0)^{T-N}}{\hat{p}^N(1-\hat{p})^{T-N}}\right]$ où $p_0 = 1-\alpha$ est le taux théorique, $\hat{p} = N/T$ le taux observé, $N$ les exceptions sur $T$ périodes. Sous $H_0$ (modèle correct), $LR_{uc} \xrightarrow{d} \chi^2(1)$. On rejette $H_0$ si $LR_{uc} > 3.84$ (test à 5%). Dans notre projet : $LR_{uc} \approx 0.03$ à 95% et $\approx 0.08$ à 99% — bien inférieurs à 3.84, donc $H_0$ non rejetée.

---

## L

### Leptokurtique

**Définition simple** : qualifie une distribution avec des queues plus épaisses et un pic central plus prononcé que la loi normale.

**Définition technique** : une distribution est leptokurtique si son excès de kurtosis (kurtosis - 3) est positif. Cela signifie plus de probabilité dans les queues et dans le centre, et moins dans les "épaules". La distribution de Student-t est leptokurtique. Les rendements financiers sont empiriquement leptokurtiques — phénomène connu depuis Mandelbrot (1963) et Fama (1965). C'est la principale motivation pour utiliser la Student-t plutôt que la normale dans notre simulation.

---

### Log-vraisemblance (maximum de)

**Définition simple** : méthode d'estimation qui choisit les paramètres qui rendent les données observées les plus probables.

**Définition technique** : pour des observations i.i.d. $x_1, \ldots, x_T$ de densité $f(x; \theta)$, la log-vraisemblance est $\ell(\theta) = \sum_t \ln f(x_t; \theta)$. L'estimateur MLE $\hat\theta = \arg\max_\theta \ell(\theta)$ est asymptotiquement normal, efficace et consistant. Dans ce projet, les degrés de liberté Student-t sont fixés par configuration; leur estimation par MLE est une extension possible.

---

## M

### Matrice de corrélation

**Définition simple** : matrice qui résume les corrélations entre paires d'actifs, avec des 1 sur la diagonale et des valeurs dans [-1, 1] hors-diagonale.

**Définition technique** : $\boldsymbol{\Gamma} = D^{-1}\boldsymbol{\Sigma}D^{-1}$ où $D = \text{diag}(\sigma_1,\ldots,\sigma_n)$. Les propriétés : $\gamma_{ii} = 1$, $\gamma_{ij} = \gamma_{ji}$, $\gamma_{ij} \in [-1,1]$, $\boldsymbol{\Gamma}$ est définie semi-positive. Une corrélation de 1 indique une dépendance linéaire parfaite ; 0, l'absence de dépendance linéaire (mais non nécessairement l'indépendance) ; -1, une dépendance parfaitement inverse.

---

### Monte Carlo (simulation de)

**Définition simple** : méthode qui génère un grand nombre de scénarios aléatoires pour approcher des grandeurs statistiques difficiles à calculer analytiquement.

**Définition technique** : en finance, la simulation Monte Carlo génère $N$ trajectoires de rendements selon un modèle probabiliste, calcule la quantité d'intérêt (P&L, VaR, ES) sur chaque trajectoire, puis prend la moyenne ou un quantile de la distribution empirique. La précision croît en $O(1/\sqrt{N})$ (loi des grands nombres). Pour $N = 50\,000$ et $\alpha = 99\%$, l'erreur standard sur la VaR est de l'ordre de ±0.3%. L'avantage est la flexibilité : on peut simuler des dynamiques non-linéaires et des distributions non-gaussiennes.

---

### Mouvement Brownien Géométrique (MBG)

**Définition simple** : modèle de base pour les prix d'actions, supposant que le prix suit une tendance aléatoire multiplicative.

**Définition technique** : $dS_t = \mu S_t dt + \sigma S_t dW_t$, soit $S_t = S_0 \exp\left((\mu - \sigma^2/2)t + \sigma W_t\right)$ où $W_t$ est un mouvement brownien standard. Les log-returns journaliers sont $r_t \sim \mathcal{N}((\mu-\sigma^2/2)\Delta t, \sigma^2\Delta t)$. Le MBG est le modèle sous-jacent à Black-Scholes. Notre projet utilise implicitement une approximation discrète du MBG (log-returns gaussiens i.i.d.) tout en l'améliorant via la Student-t.

---

## P

### P&L (Profit and Loss)

**Définition simple** : la variation de valeur d'un portefeuille sur une période.

**Définition technique** : $\text{P\&L}_t = V_t - V_{t-1}$ (différence de valeur en euros). Positif = profit, négatif = perte. La convention "perte positive" (Loss) est souvent utilisée dans les modèles de risque : $L_t = -\text{P\&L}_t = V_{t-1} - V_t$. Notre simulation calcule $\text{P\&L}_i = V \times r_{p,i}$ pour chaque scénario $i$, soit la perte $L_i = -V \times r_{p,i}$.

---

### Portefeuille

**Définition simple** : ensemble de positions financières avec leurs poids respectifs.

**Définition technique** : un portefeuille est défini par un vecteur de poids $\mathbf{w} = (w_1,\ldots,w_n)^\top$ satisfaisant $\sum_i w_i = 1$ (poids normalisés), où $w_i = V_i/V$ est la fraction de la valeur totale $V$ allouée à l'actif $i$. Le rendement du portefeuille est $r_p = \mathbf{w}^\top\mathbf{r}$, sa volatilité $\sigma_p = \sqrt{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}$. Notre portefeuille : $\mathbf{w} = (0.30, 0.20, 0.25, 0.15, 0.10)^\top$, $V = 1\,000\,000$ EUR.

---

## Q

### Quantile

**Définition simple** : valeur au-dessous de laquelle se trouve une proportion donnée de la distribution.

**Définition technique** : le quantile d'ordre $p \in (0,1)$ d'une variable aléatoire $X$ est $Q_p = F^{-1}(p) = \inf\{x : F(x) \geq p\}$. Le quantile d'ordre 0.99 est la valeur dépassée par seulement 1% de la distribution. La VaR au niveau de confiance $\alpha$ est le quantile d'ordre $\alpha$ de la distribution des pertes. Pour une distribution normale standard, $Q_{0.99} = 2.326$ et $Q_{0.95} = 1.645$.

---

### Queue de distribution

**Définition simple** : partie extrême d'une distribution, là où les événements rares ont une probabilité faible mais non nulle.

**Définition technique** : la queue gauche (ou queue de perte) d'une distribution de P&L correspond aux pertes extrêmes. Pour une distribution $F$, la queue gauche au niveau $\alpha$ est l'ensemble $\{x : F(x) \leq 1-\alpha\}$. La VaR est la frontière de cette queue. L'ES mesure le contenu de cette queue. Les distributions à queues épaisses (heavy tails) ont une probabilité de queue plus élevée qu'une gaussienne de même variance — caractéristique des rendements financiers.

---

## R

### Rendement logarithmique

**Définition simple** : variation relative du prix exprimée en logarithme naturel.

**Définition technique** : $r_t = \ln(P_t/P_{t-1}) = \ln P_t - \ln P_{t-1}$. Pour un actif de prix $P_t$, le log-return est additif dans le temps : $r_{0,T} = \sum_{t=1}^T r_{t-1,t}$, contrairement au rendement arithmétique. Sous hypothèse de MBG, les log-returns sont normaux i.i.d. Leur avantage empirique : ils ne peuvent pas dépasser -100% (impossibilité d'un prix négatif) et leur distribution est plus proche de la symétrie que les rendements arithmétiques.

---

### Risque de marché

**Définition simple** : risque de perte lié aux mouvements défavorables des prix de marché (actions, taux, devises, matières premières).

**Définition technique** : selon Bâle III, le risque de marché est le risque de perte sur des positions en trading (le "trading book") dû aux variations des facteurs de risque : (1) risque de taux d'intérêt, (2) risque actions, (3) risque de change, (4) risque de matières premières, (5) risque de crédit du marché secondaire. Il est à distinguer du risque de crédit (défaut de contrepartie) et du risque opérationnel. Notre projet couvre les points (2), (3) et (4) via SPY/EFA, EURUSD et GLD.

---

## S

### Simulation

**Définition simple** : génération informatique d'un grand nombre de scénarios selon un modèle probabiliste pour approximer des grandeurs statistiques.

**Définition technique** : une simulation de Monte Carlo génère $N$ réalisations d'une variable aléatoire (ou d'un vecteur) selon une distribution spécifiée, puis estime une fonctionnelle de cette distribution par la moyenne empirique (loi des grands nombres). Pour la VaR à 99% : on génère $N$ pertes $L_1,\ldots,L_N$ et on estime $\text{VaR}_{99\%} \approx \hat{F}_L^{-1}(0.99) = L_{(0.99N)}$ (la $(0.99N)$-ème statistique d'ordre). L'erreur d'estimation est $O(1/\sqrt{N})$.

---

### Stationnarité

**Définition simple** : propriété d'un processus stochastique dont la distribution ne change pas dans le temps.

**Définition technique** : un processus $\{r_t\}$ est strictement stationnaire si la distribution conjointe de $(r_{t_1},\ldots,r_{t_k})$ est la même que celle de $(r_{t_1+h},\ldots,r_{t_k+h})$ pour tout $h$ et $(t_1,\ldots,t_k)$. Il est faiblement stationnaire (ou stationnaire de second ordre) si $E[r_t]$ et $\text{Cov}(r_t, r_{t+h})$ ne dépendent pas de $t$. Notre modèle suppose la stationnarité des rendements — hypothèse violée par les changements de régime et la volatilité stochastique.

---

## V

### VaR (Value at Risk)

**Définition simple** : perte maximale d'un portefeuille sur un horizon donné avec un niveau de confiance spécifié.

**Définition technique** : $\text{VaR}_\alpha = F_L^{-1}(\alpha) = Q_\alpha(L)$, le quantile d'ordre $\alpha$ de la distribution des pertes. Formellement : $P(L \leq \text{VaR}_\alpha) = \alpha$, soit $P(L > \text{VaR}_\alpha) = 1-\alpha$. Il existe trois grandes méthodes de calcul : historique (quantile empirique), paramétrique ($\mu_L + z_\alpha\sigma_L$ sous gaussienne), et Monte Carlo (quantile empirique de $N$ simulations). Dans notre projet : $\text{VaR}_{99\%}^{MC} = 13\,162$ EUR sur 1 million EUR.

---

### Volatilité

**Définition simple** : mesure de la dispersion des rendements d'un actif autour de sa moyenne, souvent exprimée en écart-type annualisé.

**Définition technique** : la volatilité journalière est $\sigma = \sqrt{\text{Var}(r_t)}$ estimée par $\hat\sigma = \sqrt{\frac{1}{T-1}\sum_t(r_t - \bar{r})^2}$. Pour l'annualiser : $\sigma_{ann} = \sigma_{jour} \times \sqrt{252}$ (252 jours de trading par an). La volatilité du portefeuille est $\sigma_p = \sqrt{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}$. Pour notre portefeuille : $\sigma_p \approx 0.56\%$ par jour, soit $\approx 8.9\%$ annualisé.

---

## W

### Window (fenêtre d'estimation)

**Définition simple** : période historique utilisée pour calibrer les paramètres du modèle de risque.

**Définition technique** : le choix de la fenêtre affecte directement la VaR calculée. Une fenêtre courte (~250 jours) est plus réactive aux changements de régime mais plus volatile. Une fenêtre longue (~1000 jours) est plus stable mais peut ne pas refléter les conditions actuelles. Bâle III exige une fenêtre d'au moins 1 an incluant une période de stress récente. Notre projet utilise ~1000 jours (2020-2024), une fenêtre qui inclut des épisodes de forte volatilité (COVID-19) et de hausse des taux (2022).
