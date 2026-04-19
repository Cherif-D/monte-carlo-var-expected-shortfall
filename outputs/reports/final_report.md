# Rapport de Risque — Moteur Monte Carlo de VaR et Expected Shortfall

**Date de génération :** 19 April 2026
**Portefeuille :** Portefeuille Multi-Actifs M1
**Valeur initiale :** 1,000,000 EUR
**Nombre de simulations :** 50,000
**Horizon VaR :** 1 jour(s)
**Distribution utilisée :** Normal

---


## 1. Composition du portefeuille

### Allocation

| Actif | Poids | Exposition (EUR) | Rendement annuel | Volatilité annuelle |
|-------|------:|----------------:|----------------:|--------------------:|
| SPY | 30.0% |      300,000 | -6.04% | 18.06% |
| EFA | 20.0% |      200,000 | -3.40% | 16.63% |
| AGG | 25.0% |      250,000 | -1.36% | 5.86% |
| GLD | 15.0% |      150,000 | -2.12% | 14.25% |
| EURUSD | 10.0% |      100,000 | -5.58% | 6.88% |


## 2. Paramètres calibrés

### Statistiques descriptives des rendements

| Actif | mu_journalier | sigma_journalier | mu_annuel | sigma_annuel |
| --- | --- | --- | --- | --- |
| SPY | -0.00024 | 0.011378 | -0.06042 | 0.180617 |
| EFA | -0.000135 | 0.010477 | -0.033998 | 0.166321 |
| AGG | -5.4e-05 | 0.003689 | -0.013577 | 0.058558 |
| GLD | -8.4e-05 | 0.008974 | -0.021232 | 0.142463 |
| EURUSD | -0.000222 | 0.004337 | -0.055837 | 0.068846 |


### Matrice de corrélation

| Actif | SPY | EFA | AGG | GLD | EURUSD |
|-------|-------|-------|-------|-------|-------|
| **SPY** | 1.000 | 0.802 | -0.210 | 0.071 | 0.142 |
| **EFA** | 0.802 | 1.000 | -0.140 | 0.056 | 0.191 |
| **AGG** | -0.210 | -0.140 | 1.000 | 0.180 | -0.054 |
| **GLD** | 0.071 | 0.056 | 0.180 | 1.000 | 0.143 |
| **EURUSD** | 0.142 | 0.191 | -0.054 | 0.143 | 1.000 |


## 3. Résultats VaR et Expected Shortfall

> Les valeurs sont exprimées en EUR (perte positive = perte de valeur du portefeuille).

| Méthode | Niveau confiance | Horizon (jours) | VaR (EUR) | ES (EUR) | VaR (%) | ES (%) | Ratio ES/VaR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| historique | 95.0% | 1 | 9,590 | 11,966 | 0.959 | 1.1966 | 1.2478 |
| parametrique | 95.0% | 1 | 9,277 | 11,596 | 0.9277 | 1.1596 | 1.25 |
| monte_carlo | 95.0% | 1 | 9,372 | 11,712 | 0.9372 | 1.1712 | 1.2496 |
| historique | 99.0% | 1 | 13,795 | 15,036 | 1.3795 | 1.5036 | 1.09 |
| parametrique | 99.0% | 1 | 13,059 | 14,940 | 1.3059 | 1.494 | 1.144 |
| monte_carlo | 99.0% | 1 | 13,162 | 14,993 | 1.3162 | 1.4993 | 1.1391 |


### Interprétation

La **VaR historique** s'appuie uniquement sur les données passées sans hypothèse distributionnelle. La **VaR paramétrique gaussienne** suppose des rendements normalement distribués et fournit une formule analytique fermée. La **VaR Monte Carlo** utilise la distribution empirique des scénarios simulés et constitue l'estimateur le plus flexible des trois.

L'**Expected Shortfall** (ES, également appelé CVaR) mesure la perte espérée *au-delà* de la VaR. Elle est toujours supérieure ou égale à la VaR et fournit une information sur la sévérité des pertes extrêmes, pas seulement leur seuil.

## 4. Analyses de sensibilité

### 4.1 Sensibilité à la volatilité

Le tableau suivant montre comment la VaR évolue lorsqu'on multiplie les volatilités historiques par un facteur allant de 0.5× à 2×.

| Facteur volatilité | Niveau confiance | VaR MC (EUR) | ES MC (EUR) | VaR MC (%) |
| --- | --- | --- | --- | --- |
| 0.5 | 95% | 4760.0 | 5930.0 | 0.476 |
| 0.5 | 99% | 6655.0 | 7570.0 | 0.665 |
| 0.75 | 95% | 7066.0 | 8821.0 | 0.707 |
| 0.75 | 99% | 9909.0 | 11282.0 | 0.991 |
| 1.0 | 95% | 9372.0 | 11712.0 | 0.937 |
| 1.0 | 99% | 13162.0 | 14993.0 | 1.316 |
| 1.25 | 95% | 11679.0 | 14603.0 | 1.168 |
| 1.25 | 99% | 16416.0 | 18705.0 | 1.642 |
| 1.5 | 95% | 13985.0 | 17494.0 | 1.398 |
| 1.5 | 99% | 19670.0 | 22416.0 | 1.967 |
| 2.0 | 95% | 18598.0 | 23277.0 | 1.86 |
| 2.0 | 99% | 26178.0 | 29840.0 | 2.618 |


### 4.2 Sensibilité aux corrélations

L'augmentation des corrélations en période de stress réduit la diversification et augmente mécaniquement la VaR du portefeuille.

| Facteur corrélation | Label corrélation | Niveau confiance | VaR MC (EUR) | ES MC (EUR) | VaR MC (%) |
| --- | --- | --- | --- | --- | --- |
| 0.0 | Indépendants (0) | 95% | 7328.0 | 9149.0 | 0.733 |
| 0.0 | Indépendants (0) | 99% | 10378.0 | 11656.0 | 1.038 |
| 0.5 | 0.5x historique | 95% | 8413.0 | 10507.0 | 0.841 |
| 0.5 | 0.5x historique | 99% | 11903.0 | 13387.0 | 1.19 |
| 1.0 | 1.0x historique | 95% | 9372.0 | 11712.0 | 0.937 |
| 1.0 | 1.0x historique | 99% | 13162.0 | 14993.0 | 1.316 |
| 1.5 | 1.5x historique | 95% | 9774.0 | 12258.0 | 0.977 |
| 1.5 | 1.5x historique | 99% | 13839.0 | 15781.0 | 1.384 |


### 4.3 Sensibilité à l'horizon

Sous l'hypothèse i.i.d., la VaR à l'horizon *h* est approximée par VaR_h = VaR_1j × √h (règle racine carrée du temps).

| Horizon (jours) | Niveau confiance | VaR MC (EUR) | ES MC (EUR) | VaR MC (%) | ES / VaR |
| --- | --- | --- | --- | --- | --- |
| 1 | 95% | 9217.0 | 11557.0 | 0.922 | 1.254 |
| 1 | 99% | 13069.0 | 14908.0 | 1.307 | 1.141 |
| 5 | 95% | 21164.0 | 26299.0 | 2.116 | 1.243 |
| 5 | 99% | 29532.0 | 34013.0 | 2.953 | 1.152 |
| 10 | 95% | 30151.0 | 37473.0 | 3.015 | 1.243 |
| 10 | 99% | 41916.0 | 48137.0 | 4.192 | 1.148 |
| 21 | 95% | 44763.0 | 55114.0 | 4.476 | 1.231 |
| 21 | 99% | 61051.0 | 70454.0 | 6.105 | 1.154 |


## 5. Backtesting de la VaR (Kupiec, 1995)

Le test de Kupiec évalue si la fréquence observée d'exceptions est statistiquement compatible avec la probabilité théorique (1 - alpha).

- **n_observations** : 1008
- **niveau_confiance** : 0.99
- **freq_theo_exception** : 0.010000000000000009
- **n_exceptions** : 11
- **freq_obs_exception** : 0.0109
- **LR_stat** : 0.0824
- **LR_pval** : 0.7741
- **verdict** : Modèle VALIDE (Kupiec, 5%)


## 6. Limites et extensions

### Limites du modèle actuel

1. **Hypothèse gaussienne** : les rendements réels présentent des queues plus épaisses
   que la loi normale (kurtosis > 3). La VaR paramétrique gaussienne sous-estime
   systématiquement le risque extrême. L'extension Student-t corrige partiellement ce biais.

2. **Stationnarité** : le modèle suppose que les paramètres (mu, sigma, corrélations)
   sont constants dans le temps. En pratique, la volatilité est hétéroscédastique
   (effet GARCH) et les corrélations varient selon les régimes de marché.

3. **Portefeuille statique** : les poids ne sont pas rééquilibrés. Cette hypothèse
   est acceptable pour des horizons courts (< 10 jours) mais devient irréaliste
   pour des horizons plus longs.

4. **Absence de liquidité et coûts de transaction** : le modèle ne tient pas compte
   des coûts de débouclement d'une position en situation de stress.

5. **Données synthétiques** : les données d'exemple sont générées par GBM et ne
   reflètent pas toutes les caractéristiques des données réelles (sauts, fat tails).

### Extensions naturelles

- Modèle à volatilité stochastique (GARCH, EGARCH) pour mieux capturer le clustering de volatilité.
- Distribution de Student-t multivariée ou copules pour les queues épaisses.
- Monte Carlo conditionnel (scenarios de stress basés sur des événements historiques).
- Rééquilibrage dynamique du portefeuille.
- Calcul de la VaR incrémentale / marginale et de la contribution au risque.
- Extension aux produits dérivés (options, swaps) via valorisation Monte Carlo.


## 7. Conclusion

Ce projet a permis de mettre en œuvre un moteur complet de calcul de la VaR et de
l'Expected Shortfall pour un portefeuille multi-actifs de 1,000,000 EUR.

La VaR Monte Carlo à 99% sur 1 jour est estimée à **13,162.34 EUR** (1.32% de la valeur du portefeuille).

Les trois méthodes (historique, paramétrique, Monte Carlo) fournissent des estimations
cohérentes. Les divergences observées reflètent les différentes hypothèses sous-jacentes
et illustrent l'importance de ne pas se fier à une seule méthode.

L'analyse de sensibilité confirme que la VaR est fortement dépendante du niveau de
volatilité et des corrélations entre actifs. En particulier, la corrélation croissante
en périodes de stress peut entraîner une augmentation significative du risque par
rapport aux conditions normales.

Ce travail constitue une base solide pour des développements ultérieurs vers des
modèles plus sophistiqués (GARCH, Student-t, copules, stress-testing réglementaire).

---

*Rapport généré automatiquement par run_all.py — Projet M1 Finance Quantitative.*
