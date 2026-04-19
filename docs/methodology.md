# Méthodologie du projet

## 1. Données utilisées

### 1.1 Sources et acquisition

Les données sont acquises via l'API Yahoo Finance (`yfinance`), qui fournit des prix ajustés de clôture quotidiens pour des ETF et instruments financiers. Le téléchargement est effectué une seule fois et mis en cache localement (`data/prices.pkl`) pour éviter les appels répétés.

**Actifs retenus** :

| Ticker  | Instrument                    | Classe d'actif    |
|---------|-------------------------------|-------------------|
| SPY     | SPDR S&P 500 ETF Trust        | Actions US        |
| EFA     | iShares MSCI EAFE ETF         | Actions internationales |
| AGG     | iShares Core US Aggregate Bond ETF | Obligations US |
| GLD     | SPDR Gold Trust               | Or / Matières premières |
| EURUSD=X | Taux de change EUR/USD       | Devises           |

**Période d'estimation** : définie dans `config.yaml` (typiquement 2020-2024, environ 1000 jours de trading).

### 1.2 Traitement des données

**Prix ajustés** : les prix SPY, EFA, AGG et GLD sont des prix ajustés pour les dividendes et les splits (paramètre `auto_adjust=True` dans yfinance). Cela assure que les log-returns mesurent le **rendement total** de l'investisseur, pas seulement la variation de cours.

**Alignement des dates** : les actifs ont des jours fériés différents. La procédure est :
1. Suppression des jours où tous les actifs sont fermés
2. Forward-fill (propagation de la dernière valeur) pour les jours fériés d'un sous-ensemble d'actifs
3. Suppression des lignes restant avec NaN

**Calcul des log-returns** : $r_{i,t} = \ln(P_{i,t}/P_{i,t-1})$.

---

## 2. Construction du portefeuille

### 2.1 Définition

- **Valeur** : $V = 1\,000\,000$ EUR
- **Poids** : $\mathbf{w} = (30\%, 20\%, 25\%, 15\%, 10\%)^\top$
- **Contrainte** : $\sum_i w_i = 1$ (portefeuille fully invested)

### 2.2 Statistiques calibrées

À partir des rendements historiques $\{\mathbf{r}_t\}_{t=1}^T$ :

$$\hat{\boldsymbol{\mu}} = \frac{1}{T}\sum_{t=1}^T \mathbf{r}_t \quad \in \mathbb{R}^5$$

$$\hat{\boldsymbol{\Sigma}} = \frac{1}{T-1}\sum_{t=1}^T (\mathbf{r}_t - \hat{\boldsymbol{\mu}})(\mathbf{r}_t - \hat{\boldsymbol{\mu}})^\top \quad \in \mathbb{R}^{5\times 5}$$

$$\hat{\mu}_p = \mathbf{w}^\top\hat{\boldsymbol{\mu}}, \quad \hat{\sigma}_p = \sqrt{\mathbf{w}^\top\hat{\boldsymbol{\Sigma}}\mathbf{w}}$$

$$\hat{\boldsymbol{\Gamma}} = D^{-1}\hat{\boldsymbol{\Sigma}}D^{-1} \quad \text{(matrice de corrélation)}$$

où $D = \text{diag}(\hat{\sigma}_1, \ldots, \hat{\sigma}_5)$.

---

## 3. Calibration du modèle de simulation

### 3.1 Distribution gaussienne multivariée

Paramètres : $\boldsymbol{\mu} = \hat{\boldsymbol{\mu}}$, $\boldsymbol{\Sigma} = \hat{\boldsymbol{\Sigma}}$.

Décomposition de Cholesky : $\hat{\boldsymbol{\Sigma}} = LL^\top$.

### 3.2 Distribution Student-t multivariée

En plus des paramètres gaussiens, on estime $\nu$ par maximum de vraisemblance sur les rendements du portefeuille standardisés :

$$\hat\nu = \arg\max_{\nu > 2} \sum_{t=1}^T \ln f_{t_\nu}\left(\frac{r_{p,t} - \hat\mu_p}{\hat\sigma_p}\right)$$

### 3.3 Simulation des scénarios

$N = 50\,000$ scénarios, générés par :
- $\mathbf{Z} \in \mathbb{R}^{N \times 5}$ matrice de vecteurs gaussiens standard indépendants
- Cas Student-t : division de chaque ligne par $\sqrt{\chi^2_\nu/\nu}$ (facteur de mise à l'échelle)
- Transformation : $\mathbf{r}_i = \hat{\boldsymbol{\mu}} + L\mathbf{z}_i$
- P&L : $\text{P\&L}_i = V \times \mathbf{w}^\top\mathbf{r}_i$

---

## 4. Calcul des métriques de risque

### 4.1 VaR historique

$$\text{VaR}_\alpha^{hist} = Q_\alpha(-V \cdot \mathbf{w}^\top\mathbf{r}_{1:T})$$

quantile empirique d'ordre $\alpha$ des pertes historiques.

### 4.2 VaR paramétrique

$$\text{VaR}_\alpha^{param} = V(z_\alpha\hat\sigma_p - \hat\mu_p)$$

### 4.3 VaR et ES Monte Carlo

$$\text{VaR}_\alpha^{MC} = Q_\alpha(L_1,\ldots,L_N)$$

$$\text{ES}_\alpha^{MC} = \frac{1}{|\{i : L_i > \text{VaR}_\alpha^{MC}\}|}\sum_{i : L_i > \text{VaR}_\alpha^{MC}} L_i$$

### 4.4 Extension multi-horizons (règle $\sqrt{T}$)

$$\text{VaR}_\alpha(T) \approx \text{VaR}_\alpha(1) \times \sqrt{T}$$

Calculé pour $T \in \{1, 5, 10, 20\}$ jours.

---

## 5. Stress et analyses de sensibilité

### 5.1 Sensibilité à la volatilité

Choc multiplicatif $k$ sur les volatilités individuelles ($k \in \{0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0\}$) :

$$\boldsymbol{\Sigma}(k) = k^2 \cdot \hat{\boldsymbol{\Sigma}}$$

$$\text{VaR}_\alpha(k) = V \cdot z_\alpha \cdot \sqrt{\mathbf{w}^\top\boldsymbol{\Sigma}(k)\mathbf{w}}$$

### 5.2 Sensibilité à la corrélation

Corrélation uniforme $\rho \in [0, 0.9]$ entre tous les actifs :

$$\boldsymbol{\Gamma}(\rho) = \rho\mathbf{1}\mathbf{1}^\top + (1-\rho)I_n$$

$$\boldsymbol{\Sigma}(\rho) = D\boldsymbol{\Gamma}(\rho)D$$

### 5.3 Attribution marginale du risque

$$\text{MC}_i = w_i \cdot \frac{\text{VaR}(w_i + \delta) - \text{VaR}(w_i - \delta)}{2\delta}$$

avec $\delta = 0.01$ et renormalisation des poids après choc.

---

## 6. Backtesting

### 6.1 Protocole

1. Calculer la VaR historique day-by-day sur la fenêtre de backtesting (les mêmes 1008 jours)
2. Compter $N$ = nombre de jours où la perte réelle dépasse la VaR prédite
3. Calculer le taux d'exception $\hat{p} = N/T$
4. Appliquer le test de Kupiec avec $H_0 : p = 1-\alpha$

### 6.2 Résultats

| Niveau | $T$ | $N$ | $\hat{p}$ | $p_0$ | $LR_{uc}$ | $p$-valeur | Décision |
|--------|-----|-----|-----------|-------|-----------|------------|----------|
| 95%    | 1008| 51  | 5.06%     | 5.00% | ~0.03     | ~0.87      | Non rejeté ($H_0$) |
| 99%    | 1008| 11  | 1.09%     | 1.00% | ~0.08     | ~0.78      | Non rejeté ($H_0$) |

---

## 7. Pipeline complet

```
Étape 1  : Chargement config.yaml
Étape 2  : Téléchargement/cache données Yahoo Finance
Étape 3  : Calcul rendements log, matrice covariance, corrélation
Étape 4  : Décomposition de Cholesky
Étape 5  : VaR historique (95%, 99%)
Étape 6  : VaR paramétrique gaussienne (95%, 99%)
Étape 7  : Simulation Monte Carlo (50 000 scénarios)
Étape 8  : VaR et ES Monte Carlo (95%, 99%)
Étape 9  : ES historique et paramétrique
Étape 10 : VaR multi-horizons (1, 5, 10, 20 jours)
Étape 11 : Backtesting Kupiec
Étape 12 : Sensibilité à la volatilité
Étape 13 : Sensibilité à la corrélation / horizon / confiance
Étape 14 : Attribution marginale du risque
Étape 15 : Génération des graphiques
Étape 16 : Rapport final (CSV + console)
```
