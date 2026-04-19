# Théorie depuis les bases : VaR, ES et Monte Carlo

## Introduction

Ce document construit la théorie pas à pas, depuis la notion élémentaire de perte jusqu'aux simulations Monte Carlo avec distributions multivariées. Pour chaque concept, nous suivons le schéma : **intuition → formule → interprétation → lien au code**.

Aucune connaissance préalable en finance quantitative n'est supposée, seulement des notions de probabilités et de statistiques de niveau licence.

---

## 1. La notion de perte financière

### 1.1 Intuition

Imaginons que vous possédez un portefeuille de 1 000 000 EUR aujourd'hui. Demain matin, la valeur de votre portefeuille sera différente — peut-être plus haute, peut-être plus basse. La **perte** (ou profit, notée P&L pour Profit and Loss) est simplement la différence de valeur entre aujourd'hui et demain.

Si votre portefeuille vaut 987 000 EUR demain, votre perte est de 13 000 EUR. Si il vaut 1 015 000 EUR, votre profit est de 15 000 EUR.

### 1.2 Définition formelle

Soit $V_t$ la valeur du portefeuille à la date $t$. On définit la **perte sur un jour** comme :

$$L_{t+1} = V_t - V_{t+1}$$

Par convention, une perte est **positive** quand on perd de l'argent. Un profit correspond à une perte négative.

En termes de rendement logarithmique journalier $r_{t+1} = \ln(V_{t+1}/V_t)$, on a approximativement :

$$L_{t+1} \approx -V_t \cdot r_{t+1}$$

Cette approximation est valide pour des rendements petits (< 10%), ce qui est le cas en temps normal.

### 1.3 Lien au code

Dans `src/portfolio.py`, le rendement du portefeuille est calculé comme la somme pondérée des rendements individuels :

```python
portfolio_returns = returns @ weights  # produit matriciel : vecteur rendements × poids
```

La perte simulée pour chaque scénario Monte Carlo dans `src/simulation.py` est :

```python
pnl = portfolio_value * simulated_returns  # P&L en euros
losses = -pnl                              # convention perte positive
```

---

## 2. La distribution des rendements

### 2.1 Intuition

Les rendements journaliers ne sont pas prévisibles dans leur signe (hausse ou baisse), mais leur **distribution statistique** est relativement stable dans le temps. On peut observer, sur des données historiques, que :

- La plupart des jours, le rendement est proche de zéro (journées ordinaires)
- Parfois, le rendement est fortement positif ou négatif (journées de choc)
- Les fortes variations à la baisse sont légèrement plus fréquentes que les fortes variations à la hausse (asymétrie)
- Les événements extrêmes sont plus fréquents que ce que prédirait une loi normale pure (queues épaisses)

### 2.2 Le rendement logarithmique

On utilise les rendements logarithmiques (log-returns) plutôt que les rendements arithmétiques pour plusieurs raisons :

**Définition** : $r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$

**Propriétés utiles** :
- Les log-returns sont additifs dans le temps : $r_{t,t+h} = \sum_{k=1}^{h} r_{t+k-1, t+k}$
- Ils ne peuvent pas tomber en dessous de -100% (impossibilité d'une valeur négative)
- Ils se comportent de façon plus symétrique que les rendements arithmétiques

**Exemple numérique** : SPY passe de 400 $ à 396 $. Rendement log = ln(396/400) = ln(0.99) ≈ -0.01005 = -1.005%. Rendement arithmétique = (396-400)/400 = -1.000%. La différence est faible mais s'accumule sur de longues périodes.

### 2.3 L'hypothèse distributionnelle

**Hypothèse gaussienne** : on suppose souvent que les log-returns suivent une loi normale $r_t \sim \mathcal{N}(\mu, \sigma^2)$, où $\mu$ est le rendement moyen journalier et $\sigma$ est la volatilité journalière.

**Exemple** : pour SPY, on pourrait observer $\mu \approx 0.04\%$ par jour et $\sigma \approx 1.0\%$ par jour.

**Problème** : en réalité, les rendements présentent des **queues épaisses** (leptokurtose) — les événements extrêmes sont plus fréquents que ce que prédit la loi normale. C'est pourquoi nous utilisons aussi la distribution **Student-t** dans notre modèle.

### 2.4 Lien au code

Dans `src/returns_model.py` :

```python
# Calcul des rendements log
log_returns = np.log(prices / prices.shift(1)).dropna()

# Calibration gaussienne
mean_returns = log_returns.mean()
cov_matrix = log_returns.cov()

# Calibration Student-t (si activée)
# Estimation des degrés de liberté par maximum de vraisemblance
```

---

## 3. La Value at Risk (VaR)

### 3.1 Intuition

La VaR répond à cette question simple : **quelle est la perte maximale que je peux subir avec une probabilité de X% sur un horizon de T jours ?**

Visualisons-le : imaginons que vous ayez observé les rendements journaliers de votre portefeuille sur 1000 jours. Vous classez ces 1000 jours du pire au meilleur. La **VaR à 99%** correspond à la frontière entre les 10 pires jours (1%) et les 990 meilleurs jours (99%). Autrement dit : sur 100 jours, vous perdrez plus que la VaR exactement 1 jour en moyenne.

```
Distribution des P&L journaliers :
                    
              ████                    
          ██████████                  
        ██████████████                
      ████████████████████            
  ████████████████████████████        
▓▓▓▓|████████████████████████████████
     ↑
  VaR 99%
  
▓▓▓▓ = les 1% pires jours (queue gauche)
```

### 3.2 Définition formelle

Soit $L$ la variable aléatoire représentant la perte du portefeuille sur un jour. La **VaR au niveau de confiance $\alpha$** est définie comme :

$$\text{VaR}_\alpha = \inf\{l \in \mathbb{R} : P(L > l) \leq 1 - \alpha\}$$

De façon équivalente, en notant $F_L$ la fonction de distribution cumulative (CDF) de $L$ :

$$\text{VaR}_\alpha = F_L^{-1}(\alpha) = Q_\alpha(L)$$

où $Q_\alpha$ désigne le quantile d'ordre $\alpha$.

**Interprétation** : avec probabilité $\alpha$ (par exemple 99%), la perte sera inférieure à $\text{VaR}_\alpha$. Avec probabilité $1-\alpha$ (1%), la perte dépassera la VaR.

### 3.3 Exemple numérique concret

Avec notre portefeuille de 1 000 000 EUR :

- VaR à 95% = 9 590 EUR (méthode historique) : avec 95% de probabilité, on ne perd pas plus de 9 590 EUR demain.
- VaR à 99% = 13 162 EUR (Monte Carlo) : avec 99% de probabilité, on ne perd pas plus de 13 162 EUR demain.

En pourcentage : 13 162 / 1 000 000 = **1,32%** de la valeur du portefeuille.

**Question piège** : "Est-ce qu'une VaR de 13 162 EUR à 99% veut dire qu'on ne peut jamais perdre plus ?" **Non.** Cela signifie qu'il y a 1% de chances de perdre *plus* que 13 162 EUR. Dans ces scénarios extrêmes, on peut perdre beaucoup plus — c'est exactement ce que mesure l'Expected Shortfall.

---

## 4. Les trois méthodes de calcul de la VaR

### 4.1 Méthode historique

**Principe** : utiliser directement les rendements historiques passés comme scénarios futurs. On suppose que le futur ressemble au passé.

**Algorithme** :
1. Collecter les rendements journaliers historiques sur une fenêtre (par exemple 4 ans de données = ~1000 observations)
2. Calculer la perte journalière correspondante : $L_t = -V \cdot r_t$
3. Trier les pertes par ordre croissant
4. La VaR à $\alpha$% est le quantile $(1-\alpha)$ de cette distribution empirique

**Exemple** : sur 1000 jours, la VaR à 99% est la **10ème plus grande perte** (les 10 pires jours représentent 1%).

**Avantages** :
- Aucune hypothèse distributionnelle : capte automatiquement les queues épaisses, la non-stationnarité locale, les chocs
- Simple à comprendre et à expliquer
- Ne requiert pas d'estimation de paramètres

**Inconvénients** :
- Sensible à la fenêtre historique choisie
- Limitée par les événements passés : ne peut pas simuler des crises jamais vues
- Discontinuités dans l'estimation (sensible à l'ajout/retrait d'une observation extrême)

**Lien au code** (`src/risk_metrics.py`) :

```python
def var_historical(losses, confidence_level):
    return np.percentile(losses, confidence_level * 100)
```

### 4.2 Méthode paramétrique (Delta-Normal)

**Principe** : supposer que les rendements suivent une loi normale et utiliser la formule analytique.

**Sous hypothèse gaussienne** : le rendement du portefeuille suit $r_p \sim \mathcal{N}(\mu_p, \sigma_p^2)$, donc :

$$\text{VaR}_\alpha = V \cdot (-\mu_p + z_\alpha \cdot \sigma_p)$$

où $z_\alpha$ est le quantile de la loi normale standard au niveau $(1-\alpha)$ :
- Pour $\alpha = 95\%$ : $z_{0.95} = 1.645$
- Pour $\alpha = 99\%$ : $z_{0.99} = 2.326$

**Décomposition** :
- $\mu_p = \mathbf{w}^\top \boldsymbol{\mu}$ : rendement espéré du portefeuille (produit scalaire poids × rendements moyens)
- $\sigma_p = \sqrt{\mathbf{w}^\top \boldsymbol{\Sigma} \mathbf{w}}$ : volatilité du portefeuille (forme quadratique sur la matrice de covariance)

**Exemple numérique** :
Supposons $\mu_p \approx 0.02\%$ par jour (rendement quasiment nul sur 1 jour) et $\sigma_p = 0.56\%$ (volatilité journalière du portefeuille).

$$\text{VaR}_{99\%} = 1\,000\,000 \times (2.326 \times 0.0056 - 0.0002) = 1\,000\,000 \times 0.013 \approx 13\,000 \text{ EUR}$$

On retrouve notre résultat de 13 059 EUR.

**Avantages** :
- Rapide à calculer (une seule formule)
- Facile à comprendre et à auditer
- Stable (peu sensible aux données individuelles)

**Inconvénients** :
- Hypothèse gaussienne irréaliste : sous-estime les risques de queue
- Ne capture pas les queues épaisses, l'asymétrie, ni les régimes de crise
- Implicitement linéaire : inadaptée aux portefeuilles avec options

**Lien au code** (`src/risk_metrics.py`) :

```python
def var_parametric(portfolio_vol, portfolio_mean, confidence_level, portfolio_value):
    z = norm.ppf(confidence_level)
    var = portfolio_value * (z * portfolio_vol - portfolio_mean)
    return var
```

### 4.3 Méthode Monte Carlo

**Principe** : simuler un grand nombre (50 000) de scénarios de rendements futurs selon un modèle probabiliste, calculer la perte dans chaque scénario, puis lire le quantile empirique de la distribution simulée.

**Algorithme en 5 étapes** :
1. Calibrer les paramètres de la distribution (moyenne, covariance, éventuellement degrés de liberté)
2. Effectuer la décomposition de Cholesky de la matrice de covariance
3. Générer $N$ vecteurs de nombres aléatoires $\mathbf{z}_i \sim \mathcal{N}(0, I)$ ou $t_\nu(0, I)$
4. Transformer : $\mathbf{r}_i = \boldsymbol{\mu} + L \mathbf{z}_i$ où $L$ est la matrice de Cholesky
5. Calculer les pertes $L_i = -V \cdot \mathbf{w}^\top \mathbf{r}_i$ et prendre le quantile

**Avantages** :
- Peut utiliser des distributions non-gaussiennes (Student-t, distributions asymétriques)
- Peut modéliser des dynamiques complexes (GARCH, sauts)
- Calcule naturellement l'ES (pas seulement la VaR)
- Scalable : ajouter des actifs ne change pas l'algorithme fondamental

**Inconvénients** :
- Coûteux en calcul (50 000 simulations)
- Dépend du modèle choisi : si le modèle est mauvais, les simulations sont mauvaises
- Variance d'estimation : les résultats varient légèrement d'une exécution à l'autre (random seed)

**Lien au code** (`src/simulation.py`) :

```python
# Étape 2 : décomposition de Cholesky
L = np.linalg.cholesky(cov_matrix)

# Étape 3 : génération de nombres aléatoires
z = np.random.standard_normal((n_simulations, n_assets))

# Étape 4 : transformation
simulated_returns = mean_returns + z @ L.T

# Étape 5 : pertes
pnl = portfolio_value * (simulated_returns @ weights)
```

---

## 5. L'Expected Shortfall (ES)

### 5.1 Intuition

La VaR répond à : "quelle est la perte maximale avec 99% de probabilité ?" Mais elle ne dit rien sur ce qui se passe dans ces 1% de mauvais cas. Deux portefeuilles peuvent avoir la même VaR mais des profils de risque très différents dans la queue.

L'**Expected Shortfall** (aussi appelé CVaR ou Conditional VaR) répond à : **"si je suis dans les 1% mauvais jours, quelle est ma perte moyenne ?"**

Visuellement, c'est la **moyenne de la queue gauche** au-delà de la VaR.

### 5.2 Définition formelle

L'Expected Shortfall au niveau $\alpha$ est défini comme :

$$\text{ES}_\alpha = E[L \mid L > \text{VaR}_\alpha]$$

C'est-à-dire l'espérance de la perte sachant que la perte dépasse la VaR.

Formulation intégrale équivalente :

$$\text{ES}_\alpha = \frac{1}{1-\alpha} \int_\alpha^1 \text{VaR}_u \, du$$

Cette expression montre que l'ES est une **moyenne pondérée des VaR** pour tous les niveaux $u > \alpha$.

### 5.3 Propriété importante : cohérence

L'ES est une **mesure de risque cohérente** au sens d'Artzner et al. (1999), ce que la VaR n'est pas en général. En particulier, l'ES satisfait la **sous-additivité** : $\text{ES}(A+B) \leq \text{ES}(A) + \text{ES}(B)$, ce qui signifie que la diversification réduit toujours le risque mesuré. La VaR peut violer cette propriété, ce qui est problématique dans un contexte de gestion de portefeuille.

C'est pourquoi **Bâle III (FRTB)** a officiellement remplacé la VaR par l'ES comme mesure de risque réglementaire pour les banques depuis 2019.

### 5.4 Formule analytique sous hypothèse gaussienne

Si $L \sim \mathcal{N}(\mu_L, \sigma_L^2)$, alors :

$$\text{ES}_\alpha = \mu_L + \sigma_L \cdot \frac{\phi(z_\alpha)}{1-\alpha}$$

où $\phi$ est la densité de la loi normale standard et $z_\alpha = \Phi^{-1}(\alpha)$ est le quantile gaussien.

**Exemple numérique** : pour $\alpha = 99\%$, $z_{0.99} = 2.326$, $\phi(2.326) = 0.0267$.

$$\text{ES}_{99\%} = \mu_L + \sigma_L \cdot \frac{0.0267}{0.01} = \mu_L + 2.665 \cdot \sigma_L$$

Comparez avec la VaR : $\text{VaR}_{99\%} = \mu_L + 2.326 \cdot \sigma_L$

Donc sous hypothèse gaussienne, l'ES est toujours **supérieure** à la VaR, et le ratio ES/VaR est constant ($\approx 2.665/2.326 \approx 1.15$).

### 5.5 Nos résultats numériques

Pour notre portefeuille Monte Carlo :

| Niveau | VaR MC     | ES MC      | Ratio ES/VaR |
|--------|------------|------------|--------------|
| 95%    | 9 372 EUR  | 11 712 EUR | 1.25         |
| 99%    | 13 162 EUR | 14 993 EUR | 1.14         |

Le ratio ES/VaR est légèrement supérieur à 1.14 (valeur théorique gaussienne à 99%), ce qui indique que nos simulations capturent une légère leptokurtose.

**Interprétation** : dans les 1% pires jours, on perd en moyenne **14 993 EUR**, soit **1 831 EUR de plus** que ce que la VaR laissait supposer.

### 5.6 Lien au code

Dans `src/risk_metrics.py` :

```python
def expected_shortfall(losses, confidence_level):
    var = np.percentile(losses, confidence_level * 100)
    tail_losses = losses[losses > var]
    return tail_losses.mean()
```

---

## 6. La décomposition de Cholesky

### 6.1 Le problème à résoudre

Pour simuler des rendements multi-actifs corrélés, on ne peut pas simplement générer des variables indépendantes. Si SPY monte, EFA a tendance à monter aussi (corrélation positive). Cette structure de dépendance doit être reproduite dans les simulations.

### 6.2 Intuition géométrique

La décomposition de Cholesky résout le problème suivant : étant donnée une matrice de covariance $\Sigma$ (qui décrit comment les actifs varient ensemble), comment générer des vecteurs aléatoires qui ont exactement cette structure de covariance ?

La réponse : trouver une matrice triangulaire inférieure $L$ telle que $\Sigma = L L^\top$, puis transformer des variables indépendantes $\mathbf{z}$ via $\mathbf{r} = L\mathbf{z}$.

**Analogie** : $L$ est comme la "racine carrée" de la matrice $\Sigma$. De même que $\sigma = \sqrt{\sigma^2}$ pour scalaires, $L = \text{Chol}(\Sigma)$ pour matrices.

### 6.3 Construction pas à pas pour 2 actifs

Supposons deux actifs avec des volatilités $\sigma_1, \sigma_2$ et une corrélation $\rho$. La matrice de covariance est :

$$\Sigma = \begin{pmatrix} \sigma_1^2 & \rho\sigma_1\sigma_2 \\ \rho\sigma_1\sigma_2 & \sigma_2^2 \end{pmatrix}$$

La décomposition de Cholesky donne :

$$L = \begin{pmatrix} \sigma_1 & 0 \\ \rho\sigma_2 & \sigma_2\sqrt{1-\rho^2} \end{pmatrix}$$

**Vérification** : $LL^\top = \begin{pmatrix} \sigma_1^2 & \rho\sigma_1\sigma_2 \\ \rho\sigma_1\sigma_2 & \rho^2\sigma_2^2 + \sigma_2^2(1-\rho^2) \end{pmatrix} = \begin{pmatrix} \sigma_1^2 & \rho\sigma_1\sigma_2 \\ \rho\sigma_1\sigma_2 & \sigma_2^2 \end{pmatrix} = \Sigma$ ✓

Si $\mathbf{z} = (z_1, z_2)^\top$ avec $z_1, z_2 \sim \mathcal{N}(0,1)$ indépendants, alors $\mathbf{r} = L\mathbf{z}$ donne :

$$r_1 = \sigma_1 z_1, \quad r_2 = \rho\sigma_2 z_1 + \sigma_2\sqrt{1-\rho^2} z_2$$

- $\text{Var}(r_1) = \sigma_1^2$ ✓
- $\text{Var}(r_2) = \rho^2\sigma_2^2 + \sigma_2^2(1-\rho^2) = \sigma_2^2$ ✓
- $\text{Cov}(r_1, r_2) = \sigma_1\sigma_2 \cdot \rho \cdot E[z_1^2] = \rho\sigma_1\sigma_2$ ✓

### 6.4 Généralisation à 5 actifs

Pour notre portefeuille à 5 actifs, la même logique s'applique mais avec une matrice $5 \times 5$. NumPy calcule automatiquement cette décomposition via `np.linalg.cholesky(cov_matrix)`.

### 6.5 Lien au code

```python
# Dans src/simulation.py
cov_matrix = returns_model.cov_matrix  # matrice 5×5
L = np.linalg.cholesky(cov_matrix)    # triangulaire inférieure 5×5

# Génération de 50000 vecteurs gaussiens indépendants
z = np.random.standard_normal((50000, 5))  # forme : (50000, 5)

# Transformation : chaque ligne de z est transformée par L
correlated_returns = z @ L.T  # forme : (50000, 5)
# Chaque ligne est maintenant un vecteur de rendements corrélés
```

---

## 7. La distribution Student-t multivariée

### 7.1 Pourquoi la gaussienne est insuffisante

La loi normale prédit que des mouvements de plus de 3 écarts-types sont extrêmement rares (probabilité < 0.3%). En pratique, les marchés financiers voient des événements de 4, 5 ou 6 écarts-types bien plus souvent. On parle de **queues épaisses** ou de distribution **leptokurtique**.

**Exemple** : le 15 janvier 2015, la BNS a supprimé le plancher EUR/CHF. En quelques minutes, le CHF s'est apprécié de 30%, un mouvement de plus de 20 écarts-types. Sous hypothèse gaussienne, la probabilité d'un tel événement est astronomiquement faible (10^{-80}). En pratique, c'est arrivé.

### 7.2 La distribution Student-t

La loi de Student-t avec $\nu$ degrés de liberté a des queues plus épaisses que la normale. Plus $\nu$ est petit, plus les queues sont épaisses. Quand $\nu \to \infty$, on retrouve la loi normale.

Pour $\nu > 2$, la variance existe et vaut $\frac{\nu}{\nu-2}$ (supérieure à 1, la variance de la normale standard).

**Valeurs typiques estimées sur données financières** : $\nu \in [4, 8]$ pour les actions, indiquant des queues significativement plus épaisses que la normale.

### 7.3 Distribution Student-t multivariée et Cholesky

La généralisation multivariée utilise la même décomposition de Cholesky. Pour simuler $\mathbf{r} \sim t_\nu(\boldsymbol{\mu}, \boldsymbol{\Sigma})$ :

1. Générer $\mathbf{z} \sim \mathcal{N}(0, I_d)$ (gaussien standard multivarié)
2. Générer $\chi^2 \sim \chi^2_\nu$ (chi-carré indépendant)
3. Poser $\mathbf{r} = \boldsymbol{\mu} + L \cdot \frac{\mathbf{z}}{\sqrt{\chi^2/\nu}}$

Cette construction garantit que les queues sont épaisses et que la structure de corrélation est respectée.

### 7.4 Comparaison pratique

Sous hypothèse Student-t, les quantiles extrêmes sont plus élevés que sous hypothèse gaussienne :

| Probabilité | Quantile Gaussien | Quantile Student-t ($\nu=5$) | Différence |
|-------------|-------------------|------------------------------|------------|
| 5%          | -1.645            | -2.015                       | +22%       |
| 1%          | -2.326            | -3.365                       | +45%       |
| 0.1%        | -3.090            | -5.893                       | +91%       |

Pour les queues extrêmes, l'hypothèse Student-t donne des VaR significativement plus élevées.

---

## 8. L'ajustement pour horizon multi-jours

### 8.1 La règle de la racine carrée du temps

On calcule souvent la VaR sur un horizon de 1 jour, mais les régulateurs demandent une VaR sur 10 jours (Bâle II) ou on peut vouloir une VaR sur 5 jours (semaine de trading).

Sous l'hypothèse que les rendements journaliers sont **indépendants et identiquement distribués (i.i.d.)**, le rendement sur $T$ jours est la somme de $T$ rendements journaliers. Si chaque rendement journalier a une variance $\sigma^2$, le rendement sur $T$ jours a une variance $T\sigma^2$, donc un écart-type $\sigma\sqrt{T}$.

$$\text{VaR}_\alpha(T\text{ jours}) = \text{VaR}_\alpha(1\text{ jour}) \times \sqrt{T}$$

**Exemple** : VaR 99% à 1 jour = 13 162 EUR. VaR 99% à 10 jours :
$$13\,162 \times \sqrt{10} = 13\,162 \times 3.162 = 41\,618 \text{ EUR}$$

### 8.2 Hypothèse i.i.d. et ses limites

La règle $\sqrt{T}$ n'est valide que si les rendements sont i.i.d. En réalité :
- Il existe une **autocorrélation de court terme** dans les rendements (légèrement négative à 1-5 jours)
- La **volatilité est autocorrélée** (phénomène de clusters de volatilité) : les périodes calmes restent calmes, les périodes agitées restent agitées
- Ces deux effets se compensent partiellement, ce qui fait que $\sqrt{T}$ est une approximation raisonnable en pratique

**Alternative rigoureuse** : utiliser un modèle GARCH pour modéliser la dynamique de la volatilité, puis simuler des trajectoires multi-jours. C'est une extension naturelle de ce projet (voir `05_limits_and_extensions.md`).

---

## 9. Le backtesting : valider le modèle

### 9.1 Intuition

Un modèle de VaR doit être **vérifié empiriquement**. Si notre VaR à 99% est correcte, on devrait observer exactement 1% de dépassements sur des données historiques. Si on observe beaucoup plus, le modèle est trop optimiste. Si on observe beaucoup moins, il est trop conservateur.

Le backtesting consiste à compter le nombre de fois où la perte réelle a dépassé la VaR prédite.

### 9.2 Le test de Kupiec

Wilhelm Kupiec (1995) a proposé un test statistique pour vérifier si le taux de dépassements observé est compatible avec le taux théorique.

**Définition** : sur $T$ jours, on observe $N$ dépassements. Sous $H_0$ (modèle correct), chaque jour est un dépassement avec probabilité $p = 1-\alpha$ indépendamment des autres. Donc $N \sim \text{Binomiale}(T, p)$.

**Statistique de test** (log-vraisemblance ratio) :

$$LR_{uc} = -2\ln\left[\frac{p^N(1-p)^{T-N}}{\hat{p}^N(1-\hat{p})^{T-N}}\right] \xrightarrow{H_0} \chi^2(1)$$

où $\hat{p} = N/T$ est le taux observé.

**Nos résultats** :
- À 95% : $N = 51$ sur $T = 1008$ jours, $\hat{p} = 5.06\%$ vs $p = 5\%$ → LR faible → **modèle VALIDE**
- À 99% : $N = 11$ sur $T = 1008$ jours, $\hat{p} = 1.09\%$ vs $p = 1\%$ → LR faible → **modèle VALIDE**

**Interprétation** : l'écart entre le taux observé et le taux théorique est statistiquement insignifiant. On ne rejette pas $H_0$.

---

## 10. L'attribution marginale du risque

### 10.1 Intuition

Notre portefeuille a une VaR de 13 162 EUR. Quel actif contribue le plus à ce risque ? Cette information est cruciale pour décider comment rééquilibrer le portefeuille.

### 10.2 La contribution marginale

La **contribution marginale** de l'actif $i$ est définie comme :

$$\text{MC}_i = w_i \cdot \frac{\partial \text{VaR}}{\partial w_i}$$

Elle mesure de combien la VaR augmenterait si l'on augmentait marginalement le poids de l'actif $i$.

**Propriété** : les contributions marginales se somment à la VaR totale :
$$\text{VaR}_{total} = \sum_{i=1}^{n} \text{MC}_i$$

Cela permet de calculer la **part en %** de chaque actif dans le risque total.

### 10.3 Calcul numérique

En pratique, on calcule la dérivée numérique :

$$\text{MC}_i \approx \frac{\text{VaR}(w_i + \delta) - \text{VaR}(w_i - \delta)}{2\delta} \cdot w_i$$

avec $\delta = 0.01$ (choc de 1% sur le poids).

### 10.4 Lien au code

Dans `src/sensitivity.py` :

```python
def marginal_risk_contribution(weights, returns, portfolio_value, confidence, delta=0.01):
    contributions = {}
    base_var = compute_var(weights, returns, portfolio_value, confidence)
    
    for i, asset in enumerate(assets):
        w_up = weights.copy()
        w_up[i] += delta
        w_down = weights.copy()
        w_down[i] -= delta
        
        var_up = compute_var(w_up, returns, portfolio_value, confidence)
        var_down = compute_var(w_down, returns, portfolio_value, confidence)
        
        dvar_dwi = (var_up - var_down) / (2 * delta)
        contributions[asset] = weights[i] * dvar_dwi
    
    return contributions
```

---

## Récapitulatif des concepts clés

| Concept          | Intuition                                      | Formule clé                                         |
|------------------|------------------------------------------------|-----------------------------------------------------|
| Rendement log    | Variation relative de valeur                   | $r_t = \ln(P_t/P_{t-1})$                           |
| VaR              | Perte maximale à $\alpha$% de confiance        | $\text{VaR}_\alpha = Q_\alpha(L)$                  |
| ES               | Perte moyenne dans les scénarios extrêmes      | $E[L \mid L > \text{VaR}_\alpha]$                  |
| Cholesky         | Racine carrée matricielle de la covariance     | $\Sigma = LL^\top$                                 |
| Règle $\sqrt{T}$ | Extrapolation de la VaR sur horizon multi-jours | $\text{VaR}(T) = \text{VaR}(1) \times \sqrt{T}$  |
| Kupiec           | Test statistique de validité du modèle         | $LR_{uc} \sim \chi^2(1)$                           |
| Attribution MC   | Part de chaque actif dans le risque total      | $\text{MC}_i = w_i \partial\text{VaR}/\partial w_i$ |
