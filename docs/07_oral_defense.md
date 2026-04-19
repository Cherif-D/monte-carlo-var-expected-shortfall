# Préparer la présentation orale

## Introduction

La présentation orale d'un projet de finance quantitative est un exercice très différent de la rédaction d'un rapport ou du codage. Il s'agit de convaincre un auditoire que vous comprenez profondément ce que vous avez fait — pas seulement que le code fonctionne. Ce document vous prépare à différents formats et audiences.

---

## 1. Le pitch en 30 secondes

Situations : couloir, ascenseur, début d'entretien, première prise de contact.

**Formulation** :
> "J'ai développé un moteur de calcul de risque en Python qui estime la Value at Risk et l'Expected Shortfall d'un portefeuille de cinq classes d'actifs. J'utilise trois méthodes — historique, paramétrique et Monte Carlo — et je valide les résultats par un backtesting statistique. Sur un million d'euros, on obtient une VaR à 99% d'environ 13 000 euros par jour."

**Ce que ce pitch doit accomplir** :
- Montrer que vous savez ce qu'est une VaR (mesure de risque, pas "du calcul")
- Montrer une approche comparative (trois méthodes)
- Ancrer dans un chiffre concret (13 000 EUR)
- Être compréhensible par quelqu'un de financier mais non-spécialiste du risque

**À ne pas faire** :
- Commencer par "J'ai codé un script Python qui..." — trop technique, pas assez financier
- Dire "Je calcule la perte maximale" — faux et révèle une incompréhension

---

## 2. Le pitch en 2 minutes

Situations : présentation éclair, début de soutenance, conférence étudiante.

**Structure recommandée** :

**(1) Le contexte (20 sec)**
> "La gestion du risque de marché est au cœur de la réglementation bancaire depuis les années 1990. La question centrale est simple : combien peut-on perdre demain ? Notre projet répond à cette question pour un portefeuille diversifié de cinq actifs — actions américaines, actions internationales, obligations, or et euro-dollar."

**(2) Les méthodes (40 sec)**
> "Nous calculons la VaR et l'Expected Shortfall par trois approches complémentaires. La méthode historique exploite directement les 1008 jours de données de marché. La méthode paramétrique utilise une formule analytique sous hypothèse gaussienne. La méthode Monte Carlo génère 50 000 scénarios en utilisant une décomposition de Cholesky pour reproduire fidèlement les corrélations entre actifs, et une distribution de Student-t pour capturer les queues épaisses des marchés financiers."

**(3) Les résultats (30 sec)**
> "Sur un portefeuille de 1 million d'euros, notre VaR Monte Carlo à 99% est de 13 162 euros sur un jour — soit 1,32% de la valeur du portefeuille. L'Expected Shortfall à 99%, qui mesure la perte moyenne dans les 1% pires scénarios, est de 14 993 euros. Les trois méthodes convergent, ce qui valide la robustesse de nos estimations."

**(4) La validation (20 sec)**
> "Le modèle est validé par un backtesting de Kupiec sur 1008 jours. On observe 51 exceptions à 95% et 11 à 99% — des taux de 5,06% et 1,09%, statistiquement indistinguables des 5% et 1% théoriques. Le modèle est donc validé."

**(5) Les apports et la conscience des limites (10 sec)**
> "Le projet inclut également des analyses de sensibilité et une attribution marginale du risque par actif. Les principales limites — stationnarité et corrélations de crise — sont discutées et constituent des pistes d'extension naturelles."

---

## 3. Le pitch en 5 minutes

Situations : soutenance de projet, entretien technique approfondi.

### Plan de présentation

**Introduction (40 sec)**
Commencer par le contexte réglementaire (Bâle III, exigences de capital) pour montrer que ce projet répond à un besoin réel, pas seulement un exercice académique. Annoncer clairement la structure de la présentation.

**Le portefeuille (30 sec)**
Présenter le tableau des actifs et poids. Justifier les choix : pourquoi ces cinq actifs ? La diversification entre actions (SPY, EFA), obligations (AGG), matières premières (GLD) et devises (EURUSD) représente une allocation multi-actifs typique. Insister sur la valeur de 1 million EUR comme référence.

**Théorie (60 sec)**
Expliquer la VaR en une phrase intuitive ("perte maximale à X% de probabilité"), puis la formule générale. Faire de même pour l'ES ("perte moyenne dans les X% pires cas"). Ne pas entrer dans les détails mathématiques — dire "si vous voulez les détails, je peux développer".

**Les trois méthodes (60 sec)**
Présenter rapidement les trois approches avec leurs hypothèses respectives. Une slide avec un tableau comparatif (méthode / hypothèse principale / avantage / inconvénient) est idéale ici.

**Résultats clés (60 sec)**
Présenter le tableau récapitulatif des VaR et ES. Commenter la convergence des méthodes. Souligner que la VaR MC (avec Student-t) est légèrement supérieure à la VaR paramétrique — signe que les queues épaisses sont bien capturées. Mentionner le résultat de backtesting.

**Analyses complémentaires (30 sec)**
Mentionner rapidement la sensibilité à la volatilité (si la volatilité double, la VaR double) et l'attribution marginale.

**Limites et extensions (20 sec)**
Être honnête et bref : "Le modèle suppose la stationnarité et les corrélations constantes — ce qui est faux en période de crise. L'extension naturelle est un modèle GARCH."

**Conclusion (20 sec)**
Résumer en une phrase : "Ce projet démontre que la VaR Monte Carlo avec distribution de Student-t est une approche robuste pour la gestion du risque de marché, validée empiriquement sur données réelles."

---

## 4. Comment expliquer à différents types d'audience

### 4.1 À un professeur de finance quantitative

Ce qu'il attend : rigueur mathématique, connaissance des hypothèses et de leurs implications.

**Langage approprié** :
- "Nous utilisons la décomposition de Cholesky de la matrice de variance-covariance pour générer des simulations corrélées."
- "La distribution Student-t multivariée est obtenue par la transformation $\mathbf{r} = L(\mathbf{z}/\sqrt{\chi^2_\nu/\nu})$."
- "Le test de Kupiec teste le likelihood ratio de la coverage inconditionnelle."
- "L'ES satisfait les quatre axiomes de cohérence d'Artzner et al. (1999), contrairement à la VaR."

**Ce qu'il faut avoir préparé** : les preuves mathématiques (voir `02_math_details.md`), les hypothèses exactes du modèle, les alternatives théoriques (copules, GARCH), les références bibliographiques.

**Question type** : "Pourquoi la VaR n'est-elle pas cohérente ?"

**Réponse** : "La VaR peut violer la sous-additivité : il existe des distributions pour lesquelles $\text{VaR}(X+Y) > \text{VaR}(X) + \text{VaR}(Y)$. Cela contredit le principe économique selon lequel la diversification réduit le risque. L'ES satisfait toujours la sous-additivité, ce qui en fait une mesure de risque cohérente au sens d'Artzner et al."

---

### 4.2 À un recruteur quant (trading, structuration, risk quant)

Ce qu'il attend : maîtrise technique, lien avec la pratique de marché, conscience des limites.

**Langage approprié** :
- "Le portefeuille a une VaR 10 jours de 41 600 euros sous l'hypothèse i.i.d. — mais en période de stress, un modèle GARCH donnerait un résultat bien différent."
- "Le moteur permet de comparer une simulation gaussienne et une Student-t paramétrée dans la configuration pour illustrer l'impact des queues épaisses."
- "Le backtesting Kupiec passe à 95% et 99%, mais je suis conscient que le test de Christoffersen (conditional coverage) serait plus rigoureux."

**Ce qu'il veut entendre** : que vous savez où votre modèle est solide et où il est fragile. Les recruteurs quant apprécient la lucidité sur les limites — méfiez-vous de paraître trop "vendeur" de votre propre travail.

**Question piège** : "Est-ce que vous feriez confiance à votre VaR pour piloter les limites de trading d'une banque ?"

**Bonne réponse** : "Non, pas sans améliorations. Le modèle est un excellent exercice pédagogique et un prototype convaincant, mais une VaR de production exigerait un modèle GARCH pour la volatilité conditionnelle, des tests de stress, un backtesting out-of-sample plus rigoureux, et une validation par une équipe de risk management indépendante. Ce que j'ai construit illustre les principes — l'implémentation en production nécessiterait beaucoup plus."

---

### 4.3 À un recruteur risk management (banque, assurance, asset management)

Ce qu'il attend : compréhension du métier, lien avec la réglementation, capacité à communiquer le risque.

**Langage approprié** :
- "Ce projet correspond à l'exercice réglementaire imposé par Bâle III pour le capital en risque de marché."
- "Notre backtesting Kupiec valide le modèle — un résultat essentiel pour répondre aux exigences de validation interne des modèles (model validation)."
- "L'ES est la mesure désormais préconisée par Bâle III (FRTB) car elle capture mieux les risques de queue."

**Ce qu'il veut entendre** : que vous comprenez pourquoi ces outils existent dans un contexte institutionnel, pas seulement comment les calculer. Montrez que vous avez lu les textes réglementaires ou que vous en connaissez les grandes lignes.

**Question type** : "Comment présenteriez-vous ce résultat à un comité de risque ?"

**Bonne réponse** : "Je commencerais par le chiffre clé — 'notre risque journalier à 99% est de 13 162 euros, soit 1.32% du portefeuille' — puis je montrerais le graphique de distribution P&L pour donner une vision intuitive. Je mentionnerais ensuite que le modèle est validé par backtesting sur 1008 jours, et je terminerais par les résultats de sensibilité — comment la VaR évolue si la volatilité monte de 20%. Je n'entrerais dans les détails de Cholesky ou de Student-t que si on me le demande explicitement."

---

### 4.4 À quelqu'un de moins technique (manager, client, ami)

Ce qu'il attend : comprendre l'essentiel sans les détails techniques.

**Langage approprié** :
- "Imaginez que vous faites un trajet en voiture chaque jour. La plupart du temps, ça prend 30 minutes. La VaR, c'est dire : '99% du temps, le trajet durera moins de 45 minutes.' Ce qui reste ouvert, c'est ce qui arrive dans le 1% restant — l'Expected Shortfall mesure ça."
- "Si j'investis un million d'euros dans ce portefeuille, il y a 99 chances sur 100 que je ne perde pas plus de 13 000 euros demain."
- "Pour valider que notre calcul est correct, on a vérifié que sur 1000 jours passés, le nombre de mauvaises surprises était exactement conforme à nos prédictions."

**À éviter** : les formules, les acronymes non expliqués, les références bibliographiques.

---

## 5. Les vocabulaires clés à maîtriser

Avant une présentation, assurez-vous de pouvoir expliquer aisément (sans hésiter) chacun de ces termes :

### Termes de base
| Terme | Définition à maîtriser |
|-------|------------------------|
| VaR | Quantile de la distribution des pertes |
| Expected Shortfall | Espérance conditionnelle de la perte au-delà de la VaR |
| Niveau de confiance | Probabilité que la perte soit inférieure à la VaR |
| Log-return | Logarithme du ratio de prix consécutifs |
| Matrice de covariance | Résumé des variances et covariances entre actifs |

### Termes techniques
| Terme | Ce qu'il faut pouvoir expliquer |
|-------|--------------------------------|
| Cholesky | Factorisation matricielle pour simuler des vecteurs corrélés |
| Monte Carlo | Simulation d'un grand nombre de scénarios aléatoires |
| Distribution Student-t | Généralisation de la normale avec queues plus épaisses |
| Backtesting | Vérification empirique de la validité du modèle |
| Test de Kupiec | Test statistique du taux d'exceptions |

### Termes réglementaires
| Terme | Contexte |
|-------|---------|
| Bâle III / FRTB | Réglementation bancaire internationale, risque de marché |
| ES à 97.5% | Mesure imposée par FRTB, remplace la VaR à 99% |
| Capital réglementaire | Capital minimum que les banques doivent détenir |
| Mesure de risque cohérente | Artzner et al., sous-additivité, ES vs VaR |

---

## 6. Les questions les plus fréquentes et comment les anticiper

### "Pourquoi vous avez choisi ces 5 actifs ?"

Répondre : diversification multi-classes (actions domestiques, actions internationales, taux, or, devises) représentative d'une allocation institutionnelle modérée. La diversification inter-classe est justifiée par les faibles corrélations historiques entre obligations et actions, entre or et actions.

### "Votre VaR est-elle correcte ?"

Répondre : elle est cohérente — les trois méthodes convergent, et le backtesting de Kupiec confirme la validité statistique. Elle est néanmoins soumise aux limites habituelles de tout modèle VaR : stationnarité, corrélations supposées constantes, absence de GARCH. Ces limites sont connues et discutées.

### "Combien de temps prend l'exécution ?"

Être prêt avec un ordre de grandeur. 50 000 simulations en Python avec NumPy prennent typiquement 1 à 5 secondes selon la machine. Le téléchargement des données est la partie la plus longue si le cache n'est pas disponible.

### "Avez-vous testé avec un autre portefeuille ?"

C'est une bonne question de suivi. Vous pouvez répondre que le système est entièrement paramétré par `config.yaml` — changer d'actifs ou de poids ne nécessite aucune modification du code. C'est une preuve de conception solide.

---

## 7. Gestion du stress et de l'improvisation

### Si vous oubliez une formule

Ne paniquez pas. Dites : "Je ne me rappelle pas de la forme exacte de la formule, mais l'idée est... [expliquer l'intuition]". Un examinateur préfère une intuition correcte à une formule mal restituée.

### Si on vous pose une question hors de votre préparation

"C'est une bonne question. Je n'ai pas étudié ce point spécifique dans ce projet, mais ma compréhension générale est que... [donner votre meilleure réponse honnête]. Je serai ravi d'approfondir cela après."

### Si on critique votre approche

Ne vous défendez pas immédiatement. Dites d'abord : "C'est une critique valide" (si elle l'est), puis expliquez pourquoi vous avez quand même fait ce choix (compromis, cadre du projet, temps disponible). Montrez que vous avez conscience des limites.

---

## 8. Les 10 points à ne jamais oublier

1. **La VaR n'est pas la perte maximale.** C'est la perte dépassée avec une probabilité de $(1-\alpha)$.

2. **L'ES est supérieure à la VaR.** $\text{ES}_\alpha \geq \text{VaR}_\alpha$ toujours.

3. **Bâle III utilise l'ES, pas la VaR.** Depuis FRTB (2016), l'ES à 97.5% est la référence réglementaire.

4. **La diversification disparaît en période de crise.** Les corrélations tendent vers 1.

5. **La Student-t a des queues plus épaisses que la normale.** Elle donne des VaR plus élevées, plus conservatrices.

6. **La règle $\sqrt{T}$ est une approximation.** Valide sous i.i.d., insuffisante en présence de GARCH.

7. **Le backtesting de Kupiec valide notre modèle.** 51/1008 à 95% et 11/1008 à 99% sont statistiquement corrects.

8. **La décomposition de Cholesky génère des corrélations correctes.** $\mathbf{r} = L\mathbf{z}$ donne $\text{Cov}(\mathbf{r}) = \boldsymbol{\Sigma}$.

9. **L'ES est sous-additive, la VaR ne l'est pas toujours.** L'ES est une mesure de risque cohérente.

10. **Les résultats numériques** : VaR MC 99% = 13 162 EUR = 1,32%, ES MC 99% = 14 993 EUR, convergence des trois méthodes.
