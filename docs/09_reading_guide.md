# Guide de lecture de la documentation

## Comment utiliser ce guide

Ce document est votre feuille de route pour naviguer dans les 13 autres fichiers de documentation. Selon votre objectif et le temps dont vous disposez, vous ne lirez pas les mêmes fichiers dans le même ordre.

---

## Parcours 1 : Lecture rapide (< 1 heure)

**Objectif** : comprendre l'essentiel du projet pour une présentation courte ou un premier entretien.

| Ordre | Fichier | Temps estimé | Ce qu'on doit retenir |
|-------|---------|--------------|------------------------|
| 1 | `00_big_picture.md` | 15 min | Le portefeuille, les résultats clés, le pipeline en grandes phases |
| 2 | `04_results_interpretation.md` | 15 min | Comment lire le tableau VaR/ES, les pièges d'interprétation, la formulation orale |
| 3 | `07_oral_defense.md` | 15 min | Les pitchs 30 sec / 2 min / 5 min, les 10 points à ne jamais oublier |
| 4 | `08_glossary.md` (sélection) | 15 min | VaR, ES, Cholesky, Monte Carlo, Backtesting — au minimum ces 5 définitions |

**À retenir absolument** :
- VaR MC 99% = 13 162 EUR = 1.32% du portefeuille
- ES MC 99% = 14 993 EUR
- Backtesting Kupiec : modèle VALIDE à 95% et 99%
- La VaR n'est PAS la perte maximale
- L'ES est une mesure de risque cohérente (sous-additive), pas la VaR

---

## Parcours 2 : Compréhension complète (4 à 6 heures)

**Objectif** : comprendre en profondeur toute la théorie, le code et les résultats, pour une soutenance de projet ou un entretien quant.

| Ordre | Fichier | Temps estimé | Objectif de lecture |
|-------|---------|--------------|---------------------|
| 1 | `00_big_picture.md` | 20 min | Vue d'ensemble, architecture, rôle des modules |
| 2 | `01_theory_from_scratch.md` | 45 min | Toute la théorie VaR/ES/Cholesky/Kupiec |
| 3 | `02_math_details.md` | 45 min | Preuves, dérivations, conditions de validité |
| 4 | `03_code_walkthrough.md` | 40 min | Pipeline complet, chaque module, flux de données |
| 5 | `04_results_interpretation.md` | 25 min | Lecture des résultats, pièges, formulations |
| 6 | `05_limits_and_extensions.md` | 20 min | Hypothèses, biais, extensions GARCH/copules |
| 7 | `06_interview_questions_answers.md` | 60 min | Parcourir les 50 questions, s'entraîner sur les avancées |
| 8 | `07_oral_defense.md` | 20 min | Finaliser les pitchs, adapter au public |
| 9 | `08_glossary.md` | 20 min | Réviser les définitions précises |
| 10 | Fichiers legacy (`theory.md`, `methodology.md`, etc.) | 30 min | Compléments si pertinent |

**Recommandation** : ne pas tout lire en une seule séance. Lisez les fichiers 1-3 le premier soir, 4-6 le second, 7-9 la veille de la présentation.

---

## Parcours 3 : Préparation entretien (2 à 3 heures)

**Objectif** : se préparer spécifiquement pour un entretien en risk management, finance quantitative ou asset management.

| Ordre | Fichier | Temps | Focus |
|-------|---------|-------|-------|
| 1 | `06_interview_questions_answers.md` | 60 min | Lire toutes les questions, préparer les réponses à voix haute |
| 2 | `07_oral_defense.md` | 20 min | Adapter le discours selon le type de recruteur (quant / risk / technique) |
| 3 | `01_theory_from_scratch.md` (sections 3-5) | 30 min | Revoir VaR, ES, Cholesky, Kupiec en détail |
| 4 | `05_limits_and_extensions.md` | 20 min | Les limites à mentionner proactivement en entretien |
| 5 | `08_glossary.md` | 15 min | Les 10 termes les plus importants |
| 6 | `04_results_interpretation.md` | 15 min | Formulations orales pour présenter les chiffres |

**Questions prioritaires** (à savoir répondre parfaitement) :
- Q1 : Qu'est-ce que la VaR ? (ne pas dire "perte maximale")
- Q2 : Qu'est-ce que l'ES ?
- Q11 : Pourquoi Cholesky ?
- Q21 : Limite de la règle $\sqrt{T}$ ?
- Q22 : Quand la VaR est-elle dangereuse ?
- Q41 : Pourquoi Bâle III a remplacé la VaR par l'ES ?

---

## Parcours 4 : Révision de la théorie mathématique (2 heures)

**Objectif** : approfondir les aspects mathématiques pour un cours de finance quantitative, un examen ou une discussion académique.

| Ordre | Fichier | Temps | Focus |
|-------|---------|-------|-------|
| 1 | `01_theory_from_scratch.md` | 50 min | Toutes les sections avec formules |
| 2 | `02_math_details.md` | 60 min | Preuves complètes (Cholesky, ES gaussienne, Kupiec, attribution Euler) |
| 3 | `08_glossary.md` | 10 min | Définitions techniques précises |

**Points mathématiques clés** :
- Preuve que $LL^\top = \Sigma$ et $L\mathbf{z} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$
- Dérivation de la formule ES gaussienne par intégration
- Formule LR du test de Kupiec et distribution asymptotique $\chi^2(1)$
- Attribution Euler : $\sum_i w_i \partial\text{VaR}/\partial w_i = \text{VaR}$ (homogénéité degré 1)
- Condition de validité de la règle $\sqrt{T}$ (i.i.d.)

---

## Ce qu'on doit retenir de chaque fichier

### `00_big_picture.md`
- Architecture du projet (9 modules + run_all.py + config.yaml)
- Le portefeuille (5 actifs, 1M EUR, poids)
- Les résultats numériques clés
- Le pipeline en 4 phases
- Le pitch 2 minutes

### `01_theory_from_scratch.md`
- Définition formelle VaR comme quantile de la perte
- Définition formelle ES comme espérance conditionnelle
- Les trois méthodes (historique / paramétrique / MC)
- Construction de la décomposition de Cholesky pour 2 actifs
- Règle $\sqrt{T}$ et ses hypothèses
- Algorithme du test de Kupiec

### `02_math_details.md`
- Preuve formelle que $\mathbf{r} = L\mathbf{z}$ a la bonne distribution
- Dérivation de $\text{ES}_\alpha = \mu_L + \sigma_L \phi(z_\alpha)/(1-\alpha)$
- Formule LR du test de Kupiec
- Attribution de Euler : $\sum \text{MC}_i = \text{VaR}$
- Variance de l'estimateur quantile Monte Carlo

### `03_code_walkthrough.md`
- Structure de `config.yaml` et rôle central
- Rôle de chaque module (`data_loader`, `portfolio`, `simulation`, etc.)
- Implémentation détaillée de la simulation (3 lignes clés)
- Flux de données du prix brut jusqu'à la VaR finale
- Pièges techniques (transposition Cholesky, signe des pertes, seed aléatoire)

### `04_results_interpretation.md`
- Pourquoi les trois méthodes convergent (bon signe)
- Ce que signifient ES/VaR en termes concrets
- Pièges d'interprétation (VaR ≠ perte maximale)
- Formulations orales recommandées
- Limites du backtesting Kupiec (ne teste pas le clustering)

### `05_limits_and_extensions.md`
- Les 5 hypothèses fortes (stationnarité, i.i.d., portefeuille statique, liquidité parfaite, paramètres fixes)
- Les biais identifiés (fenêtre, look-ahead, survivance)
- 7 extensions naturelles (GARCH, copules, stress tests, rééquilibrage dynamique)
- Le paradoxe de Goodhart appliqué à la VaR

### `06_interview_questions_answers.md`
- Les 10 questions basiques (savoir répondre en < 30 sec)
- Les 10 questions intermédiaires (savoir développer en 2 min)
- Les 10 questions avancées (montrer la profondeur de compréhension)
- Les 5 questions critiques (montrer l'esprit critique)
- Les 10 questions de code

### `07_oral_defense.md`
- Pitch 30 sec (par cœur)
- Pitch 2 min (à adapter selon l'audience)
- Pitch 5 min (plan détaillé)
- Vocabulaire adapté à chaque type d'audience
- Les 10 points à ne jamais oublier (à relire la veille)

### `08_glossary.md`
- Au minimum : VaR, ES, Cholesky, Monte Carlo, Backtesting, Kupiec, Leptokurtique, Stationnarité, Copule, GARCH
- Être capable de donner la définition technique précise de chacun

### `09_reading_guide.md` (ce fichier)
- Savoir quel parcours choisir selon l'objectif
- Avoir une idée du temps nécessaire

---

## Ordre de priorité si le temps est très limité (30 minutes)

Si vous ne pouvez lire qu'un seul fichier, lisez `07_oral_defense.md`.

Si vous avez 30 minutes en tout :
1. `07_oral_defense.md` — Section "10 points à ne jamais oublier" (5 min)
2. `00_big_picture.md` — Section "Résultats numériques" et "Pitch 2 minutes" (10 min)
3. `06_interview_questions_answers.md` — Questions Q1 à Q10 (15 min)

---

## Conseils généraux de révision

**La veille d'une soutenance** : relire uniquement `07_oral_defense.md` et les résultats chiffrés de `00_big_picture.md`. Ne pas essayer d'apprendre du nouveau matériel.

**Pour un entretien surprise** : avoir en tête les 3 chiffres clés (VaR MC 99% = 13 162 EUR = 1.32%, ES 99% = 14 993 EUR, backtesting VALIDE) et la formulation correcte de la VaR (pas "perte maximale").

**Pour un examen écrit** : maîtriser les formules de `02_math_details.md` — en particulier la dérivation de l'ES gaussienne et la formule du test de Kupiec.
