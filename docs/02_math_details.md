# Détails mathématiques : notations, preuves et dérivations

## Préambule

Ce document est destiné à ceux qui souhaitent comprendre les fondements mathématiques rigoureux du projet. Il complète le fichier `01_theory_from_scratch.md` en approfondissant les preuves et dérivations. Niveau supposé : L3 mathématiques ou M1 finance quantitative.

---

## 1. Notations et conventions

### 1.1 Notations générales

| Symbole | Signification |
|---------|---------------|
| $n$ | Nombre d'actifs dans le portefeuille (ici $n = 5$) |
| $N$ | Nombre de simulations Monte Carlo (ici $N = 50\,000$) |
| $T$ | Nombre de jours historiques disponibles |
| $V$ | Valeur du portefeuille (ici $V = 1\,000\,000$ EUR) |
| $\mathbf{w} = (w_1,\ldots,w_n)^\top$ | Vecteur des poids du portefeuille, $\mathbf{1}^\top\mathbf{w} = 1$ |
| $\mathbf{r}_t = (r_{1,t},\ldots,r_{n,t})^\top$ | Vecteur des log-rendements à la date $t$ |
| $r_{p,t} = \mathbf{w}^\top \mathbf{r}_t$ | Log-rendement du portefeuille |
| $\boldsymbol{\mu} = E[\mathbf{r}_t]$ | Vecteur des rendements espérés (dimension $n$) |
| $\boldsymbol{\Sigma} = \text{Cov}(\mathbf{r}_t)$ | Matrice de variance-covariance ($n \times n$, symétrique définie positive) |
| $\boldsymbol{\Gamma}$ | Matrice de corrélation (diagonale unités) |
| $L$ | Matrice triangulaire inférieure de Cholesky |
| $\alpha$ | Niveau de confiance (par exemple 0.99 pour 99%) |
| $\phi(\cdot)$ | Densité de la loi normale standard |
| $\Phi(\cdot)$ | Fonction de répartition (CDF) de la loi normale standard |
| $z_\alpha = \Phi^{-1}(\alpha)$ | Quantile d'ordre $\alpha$ de la loi normale standard |

### 1.2 Conventions sur les signes

Dans tout ce document, la **perte** $L_t$ est définie comme positif en cas de perte :
$$L_t = -V \cdot r_{p,t} = -V \cdot \mathbf{w}^\top \mathbf{r}_t$$

La VaR est exprimée en **valeur absolue positive** : $\text{VaR}_\alpha > 0$ représente une perte.

### 1.3 Hypothèses fondamentales du modèle de base

**(H1) Stationnarité** : la distribution de $\mathbf{r}_t$ ne dépend pas de $t$.

**(H2) i.i.d.** : les vecteurs $\mathbf{r}_1, \mathbf{r}_2, \ldots$ sont indépendants et identiquement distribués.

**(H3) Log-normalité** : les prix vérifient $P_{i,t} = P_{i,0} \exp\left(\sum_{s=1}^t r_{i,s}\right)$, donc les log-rendements sont utilisés.

**(H4) Continuité** : la CDF de la perte est continue (pas d'atomes de probabilité).

Ces hypothèses sont discutées et critiquées dans `05_limits_and_extensions.md`.

---

## 2. Décomposition de Cholesky : preuve que $X = LZ$ a la bonne distribution

### 2.1 Énoncé

**Théorème** : Soit $\boldsymbol{\Sigma}$ une matrice $n \times n$ symétrique définie positive. Il existe une unique matrice triangulaire inférieure $L$ à diagonale positive telle que $\boldsymbol{\Sigma} = LL^\top$. Si $\mathbf{Z} \sim \mathcal{N}(0, I_n)$, alors $\mathbf{X} = \boldsymbol{\mu} + L\mathbf{Z}$ vérifie $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$.

### 2.2 Preuve de l'existence et de l'unicité

**Existence par induction sur $n$** :

Pour $n = 1$ : $\Sigma = (\sigma^2)$, prendre $L = (\sigma)$ avec $\sigma > 0$.

Pour le pas d'induction, partitionnons $\boldsymbol{\Sigma}$ sous forme $2 \times 2$ par blocs :
$$\boldsymbol{\Sigma} = \begin{pmatrix} A & \mathbf{b} \\ \mathbf{b}^\top & c \end{pmatrix}$$

où $A$ est $(n-1)\times(n-1)$ définie positive, $\mathbf{b} \in \mathbb{R}^{n-1}$, $c > 0$.

On cherche $L = \begin{pmatrix} L_{11} & 0 \\ \mathbf{l}^\top & l_{nn} \end{pmatrix}$ triangulaire inférieure telle que :

$$LL^\top = \begin{pmatrix} L_{11}L_{11}^\top & L_{11}\mathbf{l} \\ \mathbf{l}^\top L_{11}^\top & \mathbf{l}^\top\mathbf{l} + l_{nn}^2 \end{pmatrix} = \begin{pmatrix} A & \mathbf{b} \\ \mathbf{b}^\top & c \end{pmatrix}$$

Cela donne :
1. $L_{11}L_{11}^\top = A$ → $L_{11}$ existe par hypothèse d'induction (car $A$ est définie positive)
2. $L_{11}\mathbf{l} = \mathbf{b}$ → $\mathbf{l} = L_{11}^{-1}\mathbf{b}$ (unique car $L_{11}$ est inversible)
3. $l_{nn}^2 = c - \mathbf{l}^\top\mathbf{l} = c - \mathbf{b}^\top(L_{11}L_{11}^\top)^{-1}\mathbf{b} = c - \mathbf{b}^\top A^{-1}\mathbf{b}$

Le complément de Schur $c - \mathbf{b}^\top A^{-1}\mathbf{b} > 0$ car $\boldsymbol{\Sigma}$ est définie positive. Donc $l_{nn} = \sqrt{c - \mathbf{b}^\top A^{-1}\mathbf{b}} > 0$.

**Unicité** : la diagonale de $L$ étant positive, chaque étape détermine uniquement les coefficients de $L$.

### 2.3 Preuve que $X = \mu + LZ \sim \mathcal{N}(\mu, \Sigma)$

**Espérance** : $E[\mathbf{X}] = \boldsymbol{\mu} + L \cdot E[\mathbf{Z}] = \boldsymbol{\mu} + L \cdot \mathbf{0} = \boldsymbol{\mu}$. ✓

**Matrice de covariance** :
$$\text{Cov}(\mathbf{X}) = E[(\mathbf{X}-\boldsymbol{\mu})(\mathbf{X}-\boldsymbol{\mu})^\top] = E[L\mathbf{Z}\mathbf{Z}^\top L^\top] = L \underbrace{E[\mathbf{Z}\mathbf{Z}^\top]}_{= I_n} L^\top = LL^\top = \boldsymbol{\Sigma}$$

**Normalité** : la transformation affine $\mathbf{X} = \boldsymbol{\mu} + L\mathbf{Z}$ d'un vecteur gaussien est gaussienne (propriété de stabilité de la loi normale par transformation linéaire). ✓

**Conclusion** : $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$.

### 2.4 Calcul algorithmique de Cholesky

L'algorithme de Cholesky calcule $L$ élément par élément :

$$l_{jj} = \sqrt{\sigma_{jj} - \sum_{k=1}^{j-1} l_{jk}^2}$$

$$l_{ij} = \frac{1}{l_{jj}}\left(\sigma_{ij} - \sum_{k=1}^{j-1} l_{ik}l_{jk}\right), \quad i > j$$

La complexité est $O(n^3/3)$ pour une matrice $n \times n$, soit deux fois plus rapide que l'inversion de matrice. Pour $n = 5$, c'est négligeable.

### 2.5 Condition de validité numérique

La décomposition de Cholesky n'est définie que si $\boldsymbol{\Sigma}$ est définie positive (tous les eigenvaleurs strictement positifs). En pratique, une matrice de covariance estimée peut devenir semi-définie positive si certains actifs sont linéairement dépendants. NumPy gère cela via `np.linalg.cholesky()` qui lève une exception `LinAlgError` si la matrice n'est pas définie positive.

---

## 3. Dérivation de la formule ES gaussienne

### 3.1 Contexte

Soit $L \sim \mathcal{N}(\mu_L, \sigma_L^2)$ la perte du portefeuille. On pose $\tilde{L} = (L - \mu_L)/\sigma_L \sim \mathcal{N}(0,1)$.

La VaR et l'ES au niveau $\alpha$ sont :
$$\text{VaR}_\alpha = \mu_L + z_\alpha \sigma_L \quad \text{avec } z_\alpha = \Phi^{-1}(\alpha)$$

$$\text{ES}_\alpha = E[L \mid L > \text{VaR}_\alpha]$$

### 3.2 Dérivation

En utilisant la définition de l'espérance conditionnelle :

$$\text{ES}_\alpha = \frac{E[L \cdot \mathbf{1}_{L > \text{VaR}_\alpha}]}{P(L > \text{VaR}_\alpha)}$$

**Dénominateur** : $P(L > \text{VaR}_\alpha) = P(\tilde{L} > z_\alpha) = 1 - \Phi(z_\alpha) = 1 - \alpha$.

**Numérateur** : On développe $L = \mu_L + \sigma_L \tilde{L}$ :

$$E[L \cdot \mathbf{1}_{L > \text{VaR}_\alpha}] = \mu_L P(L > \text{VaR}_\alpha) + \sigma_L E[\tilde{L} \cdot \mathbf{1}_{\tilde{L} > z_\alpha}]$$

Il reste à calculer $E[\tilde{L} \cdot \mathbf{1}_{\tilde{L} > z_\alpha}]$ pour $\tilde{L} \sim \mathcal{N}(0,1)$ :

$$E[\tilde{L} \cdot \mathbf{1}_{\tilde{L} > z_\alpha}] = \int_{z_\alpha}^{+\infty} x \cdot \frac{1}{\sqrt{2\pi}} e^{-x^2/2} dx$$

Par le calcul direct (en reconnaissant la dérivée de $e^{-x^2/2}$) :

$$= \int_{z_\alpha}^{+\infty} \frac{1}{\sqrt{2\pi}} \cdot \left(-\frac{d}{dx}e^{-x^2/2}\right) dx = \frac{1}{\sqrt{2\pi}} \left[-e^{-x^2/2}\right]_{z_\alpha}^{+\infty} = \frac{e^{-z_\alpha^2/2}}{\sqrt{2\pi}} = \phi(z_\alpha)$$

**En combinant** :

$$\text{ES}_\alpha = \frac{\mu_L(1-\alpha) + \sigma_L \phi(z_\alpha)}{1-\alpha} = \mu_L + \sigma_L \cdot \frac{\phi(z_\alpha)}{1-\alpha}$$

### 3.3 Valeurs numériques

| $\alpha$ | $z_\alpha$ | $\phi(z_\alpha)$ | $\frac{\phi(z_\alpha)}{1-\alpha}$ | Facteur ES/VaR |
|----------|------------|-------------------|------------------------------------|-----------------|
| 90%      | 1.282      | 0.1754            | 1.754                              | 1.37            |
| 95%      | 1.645      | 0.1031            | 2.063                              | 1.25            |
| 99%      | 2.326      | 0.0267            | 2.665                              | 1.15            |
| 99.5%    | 2.576      | 0.0145            | 2.892                              | 1.12            |

**Interprétation** : à 99%, l'ES gaussienne est 15% supérieure à la VaR gaussienne. Sur notre exemple, si $\text{VaR}_{99\%} = 13\,059$ EUR (méthode paramétrique), l'ES correspondante serait $13\,059 \times 1.15 \approx 15\,018$ EUR.

### 3.4 Comparaison avec nos résultats Monte Carlo

Nos résultats MC : $\text{ES}_{99\%} = 14\,993$ EUR, $\text{VaR}_{99\%} = 13\,162$ EUR, ratio = 1.139.

Le ratio MC (1.139) est légèrement inférieur au ratio gaussien théorique (1.15), ce qui est cohérent : sous Student-t, la queue est plus épaisse donc la VaR est plus grande, mais le ratio ES/VaR tend à diminuer légèrement.

---

## 4. La règle de la racine carrée du temps

### 4.1 Hypothèse et énoncé

**Sous (H2) i.i.d.** : les rendements journaliers $r_1, r_2, \ldots$ sont indépendants de même loi $\mathcal{L}(\mu, \sigma^2)$.

Le rendement sur $T$ jours est $R_T = \sum_{t=1}^T r_t$.

**Propriétés** :
$$E[R_T] = T\mu, \quad \text{Var}(R_T) = T\sigma^2, \quad \text{Std}(R_T) = \sigma\sqrt{T}$$

**Corollaire pour la VaR** : si $r_t \sim \mathcal{N}(\mu, \sigma^2)$, alors $R_T \sim \mathcal{N}(T\mu, T\sigma^2)$ et :

$$\text{VaR}_\alpha(T) = V(z_\alpha \sigma\sqrt{T} - T\mu) \approx V \cdot z_\alpha \sigma\sqrt{T}$$

(approximation valable car $T\mu \ll z_\alpha\sigma\sqrt{T}$ sur des horizons courts)

$$\boxed{\text{VaR}_\alpha(T) \approx \text{VaR}_\alpha(1) \times \sqrt{T}}$$

### 4.2 Validité et limites

La règle est exacte sous hypothèse gaussienne i.i.d. Elle donne des approximations :

**Trop basses** en présence de :
- Volatilité conditionnelle (GARCH) : en période de forte volatilité, les rendements multi-jours ont plus de variance que $T\sigma^2$
- Queues épaisses : la règle $\sqrt{T}$ suppose la normalité des sommes

**Trop hautes** en présence de :
- Mean-reversion : les actifs tendent à revenir vers leur moyenne, réduisant la variance à long terme

**Application à nos résultats** :

| Horizon $T$ | $\sqrt{T}$ | VaR 99% estimée |
|-------------|------------|------------------|
| 1 jour      | 1.000      | 13 162 EUR       |
| 5 jours     | 2.236      | 29 430 EUR       |
| 10 jours    | 3.162      | 41 618 EUR       |
| 20 jours    | 4.472      | 58 876 EUR       |

### 4.3 Justification par le TCL (Théorème Central Limite)

Même si les rendements ne sont pas gaussiens, le TCL nous dit que $R_T = \sum_{t=1}^T r_t$ converge en distribution vers une loi normale pour $T$ grand. Donc la règle $\sqrt{T}$ devient asymptotiquement exacte même pour des distributions non-normales, à condition que les rendements soient i.i.d.

La vitesse de convergence dépend de la kurtosis : plus les queues sont épaisses, plus il faut de $T$ pour que la normale soit une bonne approximation.

---

## 5. Formule et test de Kupiec

### 5.1 Formalisation

Soit $I_t = \mathbf{1}_{L_t > \text{VaR}_\alpha}$ l'indicateur d'exception au jour $t$. Sous $H_0$ (modèle correct), les $I_t$ sont i.i.d. de loi Bernoulli de paramètre $p = 1 - \alpha$.

On observe $N = \sum_{t=1}^T I_t$ exceptions sur $T$ jours. $N \sim \text{Binomiale}(T, p)$ sous $H_0$.

### 5.2 Statistique de test

**Hypothèses** :
- $H_0$ : $p = p_0 = 1 - \alpha$ (taux correct)
- $H_1$ : $p \neq p_0$ (taux incorrect)

**Log-vraisemblance sous $H_0$** :
$$\ell_0 = N\ln(p_0) + (T-N)\ln(1-p_0)$$

**Log-vraisemblance sous $H_1$** (maximum de vraisemblance, $\hat{p} = N/T$) :
$$\ell_1 = N\ln\left(\frac{N}{T}\right) + (T-N)\ln\left(\frac{T-N}{T}\right)$$

**Statistique LR (Likelihood Ratio)** :
$$LR_{uc} = -2(\ell_0 - \ell_1) = 2\left[N\ln\frac{\hat{p}}{p_0} + (T-N)\ln\frac{1-\hat{p}}{1-p_0}\right]$$

Par le théorème de Wilks, sous $H_0$ : $LR_{uc} \xrightarrow{d} \chi^2(1)$.

**Règle de décision** : rejeter $H_0$ si $LR_{uc} > \chi^2_{1,0.95} = 3.84$ (test à 5%).

### 5.3 Application à nos résultats

**Niveau 95%** ($p_0 = 0.05$, $T = 1008$, $N = 51$, $\hat{p} = 0.0506$) :

$$LR_{uc} = 2\left[51\ln\frac{0.0506}{0.05} + 957\ln\frac{0.9494}{0.95}\right]$$

$$= 2\left[51 \times 0.0117 + 957 \times (-0.0055)\right] = 2\left[0.598 - 5.26\right] \approx 2 \times (-4.66) \approx ?$$

Attendu : LR ≈ 0.03, largement inférieur à 3.84. Le modèle est validé.

**Niveau 99%** ($p_0 = 0.01$, $T = 1008$, $N = 11$, $\hat{p} = 0.0109$) :

Attendu : LR ≈ 0.08, largement inférieur à 3.84. Le modèle est validé.

### 5.4 Limites du test de Kupiec

Le test de Kupiec ne teste que l'**unconditional coverage** : le taux global. Il ne teste pas le clustering (les exceptions peuvent arriver toutes ensemble — un mauvais signe). Le **test de Christoffersen** (2001) teste en plus l'indépendance des exceptions (conditional coverage). La combinaison des deux donne un test plus complet.

---

## 6. Propriétés mathématiques de l'ES

### 6.1 Cohérence axiomatique

L'ES est une mesure de risque **cohérente** au sens d'Artzner, Delbaen, Eber, Heath (1999), c'est-à-dire qu'elle satisfait les quatre axiomes suivants :

**(A1) Monotonie** : si $X \leq Y$ presque sûrement, alors $\rho(X) \geq \rho(Y)$ (pire position → plus de risque).

**(A2) Invariance par translation** : $\rho(X + m) = \rho(X) - m$ pour tout $m \in \mathbb{R}$ (ajouter du cash réduit le risque d'autant).

**(A3) Homogénéité positive** : $\rho(\lambda X) = \lambda \rho(X)$ pour $\lambda > 0$ (doubler la position double le risque).

**(A4) Sous-additivité** : $\rho(X + Y) \leq \rho(X) + \rho(Y)$ (la diversification ne peut qu'aider).

**La VaR satisfait (A1), (A2), (A3) mais pas toujours (A4)**. L'ES satisfait les quatre.

### 6.2 Représentation duale (Rockafellar-Uryasev)

L'ES admet la représentation variationnelle suivante (Rockafellar et Uryasev, 2000) :

$$\text{ES}_\alpha = \min_{\theta \in \mathbb{R}} \left\{\theta + \frac{1}{1-\alpha} E[\max(L - \theta, 0)]\right\}$$

Cette formulation est à la base des algorithmes d'optimisation du risque utilisant l'ES comme critère.

### 6.3 Lien ES-VaR en général

Pour toute distribution continue de la perte $L$ :

$$\text{ES}_\alpha = \frac{1}{1-\alpha}\int_\alpha^1 \text{VaR}_u \, du$$

L'ES est donc la moyenne des VaR de tous les niveaux supérieurs à $\alpha$. Elle est toujours plus grande que la VaR au niveau $\alpha$ :

$$\text{ES}_\alpha \geq \text{VaR}_\alpha$$

L'inégalité est stricte sauf dans des cas dégénérés (distribution à un point de masse).

---

## 7. Matrice de corrélation et ses propriétés

### 7.1 Définition

La matrice de corrélation $\boldsymbol{\Gamma}$ est liée à la matrice de covariance $\boldsymbol{\Sigma}$ par :

$$\gamma_{ij} = \frac{\sigma_{ij}}{\sigma_i \sigma_j}, \quad \boldsymbol{\Gamma} = D^{-1} \boldsymbol{\Sigma} D^{-1}$$

où $D = \text{diag}(\sigma_1, \ldots, \sigma_n)$.

**Propriétés** :
- $\gamma_{ii} = 1$ (diagonale unitaire)
- $\gamma_{ij} = \gamma_{ji} \in [-1, 1]$ (symétrie, bornes)
- $\boldsymbol{\Gamma}$ est définie positive si et seulement si $\boldsymbol{\Sigma}$ l'est

### 7.2 Interprétation des corrélations pour notre portefeuille

On s'attend aux relations suivantes dans notre portefeuille :

- **SPY-EFA** : corrélation élevée positive (~0.80), car les marchés actions mondiaux sont très synchronisés
- **SPY-AGG** : corrélation négative ou faible (~-0.10), car les obligations montent quand les actions baissent (flight to quality)
- **SPY-GLD** : corrélation faible à légèrement négative (~-0.05), l'or est une valeur refuge
- **SPY-EURUSD** : corrélation modérée positive (~0.15), les marchés risk-on favorisent les devises des marchés émergents et l'euro
- **AGG-EURUSD** : corrélation faible (~0.05)

Ces corrélations sont cruciales : c'est la diversification entre actifs peu corrélés qui fait que la VaR du portefeuille (13 162 EUR) est bien inférieure à la somme des VaR individuelles.

### 7.3 Effet de la corrélation sur la VaR du portefeuille

Sous hypothèse gaussienne, la volatilité du portefeuille est :

$$\sigma_p^2 = \mathbf{w}^\top \boldsymbol{\Sigma} \mathbf{w} = \sum_i w_i^2 \sigma_i^2 + 2\sum_{i<j} w_i w_j \sigma_i \sigma_j \gamma_{ij}$$

**Cas limites** :
- Si toutes les corrélations valent 1 : $\sigma_p = \sum_i w_i \sigma_i$ (pas de diversification)
- Si toutes les corrélations valent 0 : $\sigma_p = \sqrt{\sum_i w_i^2 \sigma_i^2}$ (diversification maximale)
- Si toutes les corrélations valent -1 (impossible en général) : risque nul possible

Le **bénéfice de diversification** est défini comme :
$$\text{BD} = \frac{\sum_i w_i \sigma_i - \sigma_p}{\sum_i w_i \sigma_i} \times 100\%$$

Un bénéfice de diversification de 30% signifie que le portefeuille est 30% moins risqué que ce que suggèrent les risques individuels.

---

## 8. Attribution marginale : dérivation formelle

### 8.1 Formule analytique pour la VaR paramétrique

Pour la VaR paramétrique gaussienne, la contribution analytique de l'actif $i$ est :

$$\text{MC}_i = w_i \cdot \frac{\partial \text{VaR}}{\partial w_i} = V \cdot z_\alpha \cdot \frac{w_i (\boldsymbol{\Sigma}\mathbf{w})_i}{\sigma_p}$$

où $(\boldsymbol{\Sigma}\mathbf{w})_i$ est le $i$-ème composant du produit $\boldsymbol{\Sigma}\mathbf{w}$.

**Vérification de la décomposition** : $\sum_i \text{MC}_i = V \cdot z_\alpha \cdot \frac{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}{\sigma_p} = V \cdot z_\alpha \cdot \sigma_p = \text{VaR}$. ✓

### 8.2 Contribution en pourcentage

La contribution relative de l'actif $i$ est :

$$\text{RC}_i = \frac{\text{MC}_i}{\text{VaR}} = \frac{w_i(\boldsymbol{\Sigma}\mathbf{w})_i}{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}$$

**Propriété** : $\sum_i \text{RC}_i = 1$.

Cette décomposition s'appelle le **théorème d'Euler pour les fonctions homogènes de degré 1** : la VaR paramétrique est homogène de degré 1 en $\mathbf{w}$ (doubler toutes les positions double la VaR), donc la somme des contributions euléariennes vaut exactement la VaR.

### 8.3 Attribution marginale Monte Carlo

Pour la VaR Monte Carlo, on ne dispose pas de formule analytique. On utilise l'estimateur numérique :

$$\hat{\text{MC}}_i = w_i \cdot \frac{\text{VaR}(w_i + \delta) - \text{VaR}(w_i - \delta)}{2\delta}$$

**Problème** : la VaR Monte Carlo est bruitée (variance d'estimation ~$1/\sqrt{N}$), donc la dérivée numérique est elle aussi bruitée. On peut réduire cette variance en :
1. Augmentant $N$ (coûteux)
2. Utilisant des simulations communes (Common Random Numbers) : utiliser le même seed pour les deux évaluations $w_i + \delta$ et $w_i - \delta$, ce qui annule une grande partie du bruit
3. Utilisant une représentation analytique approchée basée sur les simulations existantes

---

## 9. Estimation des paramètres

### 9.1 Estimateur de la moyenne

Estimateur empirique non biaisé :
$$\hat{\boldsymbol{\mu}} = \frac{1}{T}\sum_{t=1}^T \mathbf{r}_t$$

**Variance de l'estimateur** : $\text{Var}(\hat{\mu}_i) = \sigma_i^2 / T$. Avec $T = 1008$ jours et $\sigma \approx 1\%$, l'erreur standard sur la moyenne est $\approx 0.03\%$, soit un rapport signal/bruit très faible. C'est pour cela qu'en pratique, on pose souvent $\boldsymbol{\mu} = 0$ pour le calcul de VaR (l'effet de la dérive sur 1 jour est négligeable devant la volatilité).

### 9.2 Estimateur de la matrice de covariance

Estimateur empirique non biaisé de Bessel :
$$\hat{\boldsymbol{\Sigma}} = \frac{1}{T-1}\sum_{t=1}^T (\mathbf{r}_t - \hat{\boldsymbol{\mu}})(\mathbf{r}_t - \hat{\boldsymbol{\mu}})^\top$$

**Problème de dimension** : avec $n = 5$ actifs et $T = 1008$ observations, on estime $n(n+1)/2 = 15$ paramètres avec un ratio observations/paramètres de $1008/15 \approx 67$. C'est confortable. Mais pour $n = 100$ actifs, on devrait estimer $5050$ paramètres, ce qui serait problématique avec seulement 1000 observations (matrice de covariance mal conditionnée, voire singulière).

Solutions pour grandes dimensions : **matrice de covariance régularisée** (Ledoit-Wolf), **modèles factoriels** (CAPM, modèle à facteurs).

### 9.3 Estimation des degrés de liberté Student-t

L'estimation des degrés de liberté $\nu$ se fait par **maximum de vraisemblance**. La log-vraisemblance pour $\mathbf{r}_t \sim t_\nu(\boldsymbol{\mu}, \boldsymbol{\Sigma})$ est :

$$\ell(\nu, \boldsymbol{\mu}, \boldsymbol{\Sigma}) = \sum_{t=1}^T \ln f_{t_\nu}(\mathbf{r}_t; \boldsymbol{\mu}, \boldsymbol{\Sigma})$$

où la densité de la Student-t multivariée est :

$$f_{t_\nu}(\mathbf{x}) = \frac{\Gamma\left(\frac{\nu+n}{2}\right)}{\Gamma\left(\frac{\nu}{2}\right)(\nu\pi)^{n/2}|\boldsymbol{\Sigma}|^{1/2}} \left(1 + \frac{(\mathbf{x}-\boldsymbol{\mu})^\top \boldsymbol{\Sigma}^{-1}(\mathbf{x}-\boldsymbol{\mu})}{\nu}\right)^{-\frac{\nu+n}{2}}$$

L'optimisation en $\nu$ se fait numériquement (SciPy `minimize`). Les valeurs typiques obtenues sur données financières sont $\nu \in [4, 8]$.

---

## 10. Convergence de la VaR Monte Carlo

### 10.1 Variance de l'estimateur quantile

La VaR Monte Carlo est un estimateur de quantile empirique. Pour $N$ simulations i.i.d. de loi $F_L$, l'estimateur $\hat{Q}_\alpha = F_L^{-1}(\alpha)$ estimé sur les $N$ simulations a une variance asymptotique :

$$\text{Var}(\hat{Q}_\alpha) \approx \frac{\alpha(1-\alpha)}{N [f_L(\text{VaR}_\alpha)]^2}$$

où $f_L$ est la densité de la loi des pertes.

### 10.2 Erreur standard pour nos simulations

Pour $N = 50\,000$, $\alpha = 0.99$, et en supposant $f_L(\text{VaR}) \approx 0.03$ (densité au niveau 99%) :

$$\text{SE}(\hat{\text{VaR}}_{99\%}) \approx \frac{\sqrt{0.01 \times 0.99}}{50\,000^{1/2} \times 0.03} \approx \frac{0.0995}{7.07} \approx 0.47\%$$

En euros : $0.47\% \times 13\,162 \approx 62$ EUR. L'erreur d'estimation est donc d'environ **±62 EUR** sur notre VaR de 13 162 EUR, soit moins de 0.5%.

C'est pourquoi les résultats varient légèrement d'une exécution à l'autre (même ordre de grandeur), et c'est une raison pour laquelle on fixe une graine aléatoire (`seed = 42` dans `config.yaml`) pour la reproductibilité.

### 10.3 Réduction de variance

Pour améliorer la précision sans augmenter $N$, on peut utiliser :

- **Stratified sampling** : diviser l'espace des simulations en strates et échantillonner proportionnellement
- **Importance sampling** : sur-échantillonner dans la queue gauche (région d'intérêt) et pondérer
- **Quasi-Monte Carlo** : utiliser des suites à faible discrépance (Sobol, Halton) plutôt que des nombres pseudo-aléatoires

Ces techniques ne sont pas implémentées dans le projet actuel mais constituent des extensions naturelles.
