# Préparation aux entretiens : 50 questions-réponses

## Mode d'emploi

Ce document contient 50 questions-réponses organisées du plus simple au plus avancé. Pour chaque question, le format est :

- **Réponse courte** : la réponse d'une phrase qu'on donne si le recruteur attend juste une confirmation
- **Réponse détaillée** : la réponse complète pour un recruteur technique ou un jury de soutenance
- **Piège à éviter** : l'erreur classique à ne pas commettre (quand c'est pertinent)

---

## Partie 1 — Questions fondamentales (niveau débutant)

---

### Q1 : Qu'est-ce que la Value at Risk (VaR) ?

**Réponse courte** : La VaR est la perte maximale d'un portefeuille sur un horizon donné, avec un certain niveau de confiance.

**Réponse détaillée** : La VaR au niveau de confiance $\alpha$ sur un horizon $T$ est le quantile d'ordre $\alpha$ de la distribution des pertes du portefeuille. Par exemple, une VaR à 99% sur 1 jour de 13 162 EUR signifie que, avec une probabilité de 99%, le portefeuille ne perdra pas plus de 13 162 EUR le lendemain. En termes probabilistes : $P(L > \text{VaR}_{99\%}) = 1\%$.

**Piège à éviter** : Ne jamais dire "la VaR est la perte maximale". La VaR est la perte maximale *avec une probabilité donnée* — il y a toujours 1% (ou 5%) de chances de perdre plus. Ce piège est récurrent et très visible pour un examinateur.

---

### Q2 : Qu'est-ce que l'Expected Shortfall (ES) ?

**Réponse courte** : L'ES est la perte moyenne dans les scénarios qui dépassent la VaR.

**Réponse détaillée** : L'ES (aussi appelé CVaR ou Conditional VaR) est définie comme $\text{ES}_\alpha = E[L \mid L > \text{VaR}_\alpha]$. C'est l'espérance de la perte sachant qu'on est dans les pires $(1-\alpha)$% de scénarios. Dans notre projet, l'ES à 99% est de 14 993 EUR : dans les 1% pires jours, on perd en moyenne 14 993 EUR. L'ES est toujours supérieure ou égale à la VaR au même niveau.

---

### Q3 : Quelle est la différence entre VaR et ES ?

**Réponse courte** : La VaR fixe un seuil que la perte dépasse avec une probabilité donnée ; l'ES mesure la perte *moyenne* au-delà de ce seuil.

**Réponse détaillée** : La VaR répond à "quelle est ma perte maximale à X% de probabilité ?". Elle ne dit rien sur la profondeur de la queue : deux portefeuilles avec la même VaR peuvent avoir des ES très différentes si l'un d'eux a une queue gauche beaucoup plus épaisse. L'ES complète la VaR en quantifiant le risque extrême au-delà du seuil. De plus, contrairement à la VaR, l'ES est une mesure de risque cohérente (sous-additive), ce qui lui donne une justification théorique plus solide.

---

### Q4 : Pourquoi utiliser trois méthodes différentes pour calculer la VaR ?

**Réponse courte** : Chaque méthode repose sur des hypothèses différentes ; leur comparaison permet de vérifier la robustesse des résultats.

**Réponse détaillée** : La méthode historique utilise directement le passé sans hypothèse distributionnelle mais est limitée aux événements déjà vus. La méthode paramétrique est analytique et rapide mais suppose la gaussianité. La méthode Monte Carlo est la plus flexible (peut utiliser Student-t, modèles non-linéaires) mais requiert un modèle de simulation. Dans notre projet, les trois donnent des résultats proches (9 277 à 9 590 EUR à 95%), ce qui renforce la confiance dans les estimations.

---

### Q5 : Qu'est-ce qu'un rendement logarithmique et pourquoi l'utiliser ?

**Réponse courte** : C'est $\ln(P_t/P_{t-1})$ — la variation relative du prix. On l'utilise car il est additif dans le temps et symétrique.

**Réponse détaillée** : Le log-return $r_t = \ln(P_t/P_{t-1})$ a plusieurs propriétés avantageuses : (1) il est additif sur plusieurs périodes, $r_{t,t+h} = \sum r_{t+k}$ ; (2) il ne peut pas descendre sous -100% (impossibilité d'un prix négatif) ; (3) il est plus proche d'une distribution normale que le rendement arithmétique. L'approximation $\ln(1+x) \approx x$ pour $|x|$ petit montre que les deux rendements sont quasi-identiques sur une journée.

---

### Q6 : Qu'est-ce que la matrice de variance-covariance ?

**Réponse courte** : C'est la matrice $\Sigma_{ij} = \text{Cov}(r_i, r_j)$ qui résume comment les actifs varient ensemble.

**Réponse détaillée** : Pour $n$ actifs, la matrice de covariance est $n \times n$, symétrique et (si les actifs sont non-dégénérés) définie positive. La diagonale contient les variances $\sigma_i^2$ de chaque actif, et les termes hors-diagonale les covariances. Elle est l'ingrédient fondamental pour calculer la volatilité du portefeuille : $\sigma_p^2 = \mathbf{w}^\top \boldsymbol{\Sigma} \mathbf{w}$. Pour notre portefeuille à 5 actifs, c'est une matrice $5 \times 5$ avec $5 \times 6/2 = 15$ paramètres distincts.

---

### Q7 : Qu'est-ce que le niveau de confiance dans une VaR ?

**Réponse courte** : C'est la probabilité que la perte soit inférieure à la VaR.

**Réponse détaillée** : Un niveau de confiance de 99% signifie que, sur 100 jours de trading typiques, on s'attend à voir au plus 1 jour où la perte dépasse la VaR. C'est le complément du "niveau d'exception" ou "tail probability" (1%). Le choix du niveau dépend du contexte : les banques utilisent 99% pour le capital réglementaire (Bâle II), Bâle III/FRTB utilise 97.5% pour l'ES.

---

### Q8 : Qu'est-ce que le backtesting d'une VaR ?

**Réponse courte** : C'est la vérification a posteriori que le taux d'exceptions observé est cohérent avec le niveau de confiance du modèle.

**Réponse détaillée** : On compare, sur une série historique, le nombre de jours où la perte réelle a dépassé la VaR prédite. Sous un modèle correct à 99%, on s'attend à 1% d'exceptions. Si on observe 5% d'exceptions, le modèle sous-estime systématiquement le risque. Le test de Kupiec formalise cela statistiquement via un test du rapport de vraisemblance.

---

### Q9 : Qu'est-ce que le test de Kupiec ?

**Réponse courte** : C'est un test statistique qui vérifie si le taux d'exceptions observé est compatible avec le taux théorique du modèle.

**Réponse détaillée** : Kupiec (1995) propose une statistique de test basée sur le rapport de vraisemblance entre l'hypothèse $H_0$ (taux correct) et l'alternative (taux différent). La statistique $LR_{uc}$ suit asymptotiquement un $\chi^2(1)$. Dans notre projet : 51 exceptions sur 1008 jours à 95% (taux = 5.06% vs 5% théorique) et 11 exceptions sur 1008 jours à 99% (taux = 1.09% vs 1% théorique). Les deux $p$-values sont bien supérieures à 5%, on ne rejette pas $H_0$ : le modèle est valide.

**Piège à éviter** : Le test de Kupiec ne teste que le taux global (unconditional coverage). Il ne teste pas si les exceptions sont clustérisées (conditional coverage). Un modèle peut passer le test de Kupiec mais avoir toutes ses exceptions concentrées sur une semaine de crise — ce qui est un problème sérieux non détecté.

---

### Q10 : Qu'est-ce que la règle de la racine carrée du temps ?

**Réponse courte** : C'est l'approximation $\text{VaR}(T\text{ jours}) = \text{VaR}(1\text{ jour}) \times \sqrt{T}$, valide sous hypothèse i.i.d.

**Réponse détaillée** : Si les rendements journaliers sont indépendants et identiquement distribués, la variance du rendement sur $T$ jours est $T$ fois la variance journalière (additivité). L'écart-type (donc la VaR sous gaussienne) croît en $\sqrt{T}$. C'est une extension commode mais approximative. La règle surestime si les rendements sont mean-reverting, la sous-estime si la volatilité est persistante (GARCH).

---

## Partie 2 — Questions intermédiaires

---

### Q11 : Pourquoi utilise-t-on la décomposition de Cholesky dans la simulation ?

**Réponse courte** : Pour générer des vecteurs de rendements corrélés à partir de variables indépendantes.

**Réponse détaillée** : On ne peut pas simuler directement des variables corrélées. La décomposition de Cholesky transforme des variables indépendantes $\mathbf{z} \sim \mathcal{N}(0, I)$ en variables corrélées $\mathbf{r} = L\mathbf{z}$ où $L$ est la matrice triangulaire inférieure telle que $LL^\top = \boldsymbol{\Sigma}$. Il est prouvé que $\mathbf{r} \sim \mathcal{N}(\mathbf{0}, \boldsymbol{\Sigma})$. C'est une façon numériquement stable et efficace de reproduire la structure de corrélation du portefeuille.

**Piège à éviter** : Confondre $L^\top\mathbf{z}$ avec $L\mathbf{z}$. Dans NumPy, `np.linalg.cholesky()` retourne la triangulaire inférieure $L$. La transformation correcte est $L\mathbf{z}$ (ou en notation matricielle avec les simulations en lignes : `Z @ L.T`).

---

### Q12 : Quelle est la différence entre la distribution gaussienne et la distribution Student-t ?

**Réponse courte** : La Student-t a des queues plus épaisses, ce qui modélise mieux les événements extrêmes des marchés financiers.

**Réponse détaillée** : La distribution de Student-t avec $\nu$ degrés de liberté a un kurtosis de $3 + 6/(\nu-4)$ pour $\nu > 4$ (contre 3 pour la normale). Plus $\nu$ est petit, plus les queues sont épaisses. Pour $\nu = 5$ (typique pour des actions), le quantile à 1% est ~3.365 contre 2.326 pour la normale — soit 45% plus élevé. Cela se traduit par une VaR plus élevée, ce qui est plus prudent. Quand $\nu \to \infty$, la Student-t converge vers la normale.

---

### Q13 : Qu'est-ce que la leptokurtose et pourquoi est-elle importante en finance ?

**Réponse courte** : C'est la propriété d'avoir des queues plus épaisses et un pic plus élevé que la loi normale.

**Réponse détaillée** : Les distributions leptokurtiques (kurtosis > 3) ont plus de probabilité dans les queues et dans le centre, et moins dans les "épaules" que la normale. Pour les rendements financiers, cela signifie que les événements extrêmes sont plus fréquents que ce que prédit la normale. Empiriquement, le kurtosis des rendements journaliers d'actions est souvent entre 5 et 10. Ignorer la leptokurtose conduit à une sous-estimation systématique des risques extrêmes — erreur classique des modèles pré-2008.

---

### Q14 : Qu'est-ce que la sous-additivité et pourquoi est-ce important ?

**Réponse courte** : La sous-additivité signifie que le risque d'un portefeuille combiné est toujours inférieur ou égal à la somme des risques séparés — elle formalise le principe de diversification.

**Réponse détaillée** : Une mesure de risque $\rho$ est sous-additive si $\rho(X + Y) \leq \rho(X) + \rho(Y)$. L'ES satisfait toujours cette propriété. La VaR peut la violer : il existe des distributions telles que $\text{VaR}(X+Y) > \text{VaR}(X) + \text{VaR}(Y)$. Cela implique qu'avec la VaR comme mesure de risque, diviser un portefeuille pourrait artificiellement paraître plus risqué que le combiner — ce qui est absurde économiquement. La sous-additivité est un des quatre axiomes d'une mesure de risque cohérente (Artzner et al., 1999).

---

### Q15 : Comment interpréter la contribution marginale d'un actif au risque ?

**Réponse courte** : C'est de combien la VaR totale augmenterait si on augmentait légèrement le poids de cet actif.

**Réponse détaillée** : La contribution marginale de l'actif $i$ est $\text{MC}_i = w_i \cdot \partial\text{VaR}/\partial w_i$. La somme des contributions marginales vaut exactement la VaR totale (propriété de l'Euler pour les fonctions homogènes). Un actif avec une contribution de 30% signifie que 30% du risque total lui est attribuable. Si un actif représente 20% du portefeuille mais contribue à 35% du risque, il est le principal "consommateur de risque" et est un candidat à une réduction de position.

---

### Q16 : Pourquoi la VaR Monte Carlo est-elle légèrement différente à chaque exécution ?

**Réponse courte** : Parce que la simulation génère des nombres aléatoires — la VaR est un estimateur bruité qui varie selon la graine aléatoire.

**Réponse détaillée** : La VaR Monte Carlo est le quantile empirique de $N$ simulations aléatoires. Pour $N$ fini, il y a une variance d'estimation. L'erreur standard est approximativement $\text{SE} \approx \sqrt{\alpha(1-\alpha)} / (N^{1/2} f(\text{VaR}))$ où $f$ est la densité au point de VaR. Avec $N = 50\,000$, cette erreur est de l'ordre de ±60 EUR pour notre VaR à 99%. Pour éliminer ce bruit dans les comparaisons, on fixe une graine aléatoire (`seed = 42` dans `config.yaml`).

---

### Q17 : Quelle est la signification économique du bénéfice de diversification ?

**Réponse courte** : C'est la réduction de risque obtenue en combinant des actifs imparfaitement corrélés dans un portefeuille.

**Réponse détaillée** : Sous hypothèse gaussienne, la volatilité du portefeuille est $\sigma_p = \sqrt{\mathbf{w}^\top\boldsymbol{\Sigma}\mathbf{w}}$. Si toutes les corrélations étaient de 1 (pas de diversification), on aurait $\sigma_p = \sum_i w_i\sigma_i$ (somme pondérée des volatilités individuelles). Le bénéfice de diversification est la différence : $BD = \sum_i w_i\sigma_i - \sigma_p > 0$ pour des corrélations strictement inférieures à 1. Dans notre portefeuille multi-actifs (actions, obligations, or, devises), ce bénéfice est significatif car les classes d'actifs ont des corrélations faibles voire négatives.

---

### Q18 : Pourquoi la VaR historique est-elle sensible au choix de la fenêtre temporelle ?

**Réponse courte** : Parce qu'elle est basée directement sur les données passées — l'ajout ou la suppression d'une journée extrême peut significativement changer le quantile.

**Réponse détaillée** : La VaR historique à 99% sur 1000 jours est le 10ème pire rendement. Si une crise comme mars 2020 entre dans ou sort de la fenêtre, le 10ème pire rendement peut changer d'ordre de grandeur. Ce phénomène, appelé "ghost effect" ou effet de "date cliff", est un problème connu : la VaR peut sauter brutalement 4 ans après une crise quand les données de crise sortent de la fenêtre de calcul. Les régulateurs en sont conscients et exigent souvent une période d'observation d'au moins 1 an incluant une période de stress.

---

### Q19 : En quoi la décomposition de Cholesky exige-t-elle que la matrice de covariance soit définie positive ?

**Réponse courte** : Parce que l'algorithme de Cholesky requiert de prendre des racines carrées de valeurs qui doivent être strictement positives.

**Réponse détaillée** : À chaque étape de l'algorithme de Cholesky, on calcule $l_{jj} = \sqrt{\sigma_{jj} - \sum_{k<j}l_{jk}^2}$. L'expression sous la racine est le complément de Schur de la matrice — il est strictement positif si et seulement si la matrice est définie positive. Si la matrice n'est que semi-définie positive (valeur propre nulle), certains $l_{jj}$ seraient nuls, rendant la matrice $L$ singulière et la décomposition non unique. En pratique, cela peut arriver si des actifs sont parfaitement linéairement dépendants ou si on a plus d'actifs que d'observations.

---

### Q20 : Qu'est-ce que le problème de "la VaR ne dit rien sur la queue" ?

**Réponse courte** : La VaR donne une frontière mais ignore ce qui se passe au-delà — deux portefeuilles très différents peuvent avoir la même VaR.

**Réponse détaillée** : Imaginons deux portefeuilles. Le portefeuille A a une distribution de perte avec une queue légèrement au-delà de la VaR (pertes limitées à 1.2× la VaR). Le portefeuille B a une queue très épaisse (pertes pouvant atteindre 10× la VaR). Les deux ont exactement la même VaR à 99%, donc la même charge en capital sous Bâle II. Mais B est bien plus dangereux. C'est la principale critique faite à la VaR, qui a conduit Bâle III à adopter l'ES (qui mesure justement le contenu de la queue).

---

## Partie 3 — Questions avancées

---

### Q21 : Quelle est la limite de la règle racine carrée du temps en présence de GARCH ?

**Réponse courte** : En présence de clustering de volatilité (GARCH), la variance sur $T$ jours n'est pas $T$ fois la variance journalière — la règle $\sqrt{T}$ sous-estime le risque en période de forte volatilité et le surestime en période de calme.

**Réponse détaillée** : Dans un modèle GARCH(1,1), la volatilité conditionnelle à $t+1$ dépend des chocs passés : $\sigma_{t+1}^2 = \omega + \alpha\epsilon_t^2 + \beta\sigma_t^2$. La variance du rendement à 10 jours depuis $t$ n'est pas $10\sigma_t^2$ mais une somme complexe $\sum_{k=1}^{10} E[\sigma_{t+k}^2 | \mathcal{F}_t]$ qui dépend de l'état courant. Si $\sigma_t$ est élevée (comme en mars 2020), la variance à 10 jours est beaucoup plus grande que $10\sigma_t^2$ car la volatilité persiste. La règle $\sqrt{T}$ est donc inappropriée dans ces conditions — elle peut sous-estimer la VaR à 10 jours d'un facteur 2 ou plus en pleine crise.

---

### Q22 : Comment la VaR peut-elle être dangereuse comme outil de gestion du risque ?

**Réponse courte** : Elle peut créer une fausse sensation de sécurité et des incitations perverses à concentrer les risques dans la queue extrême.

**Réponse détaillée** : (1) **Risque de modèle** : si les hypothèses sous-jacentes (gaussianité, stationnarité) sont fausses, la VaR est incorrecte. (2) **Incitations perverses** : une banque qui optimise pour minimiser sa VaR peut vendre de la protection contre des événements à 99.5% de probabilité (assurance contre les queues extrêmes) sans que cela impacte sa VaR à 99%. Elle accumule alors un risque énorme dans les 0.5% d'événements extrêmes — exactement ce qui s'est passé avec les CDS avant 2008. (3) **Fausse précision** : présenter une VaR à 13 162 EUR avec deux décimales suggère une précision illusoire, alors que l'intervalle de confiance réel est de l'ordre de ±500 EUR.

---

### Q23 : Quelle est la différence entre VaR unconditionnelle et VaR conditionnelle ?

**Réponse courte** : La VaR unconditionnelle est calculée sur la distribution marginale des rendements ; la VaR conditionnelle est calculée en tenant compte de l'état actuel du marché.

**Réponse détaillée** : Notre VaR Monte Carlo est *unconditionnelle* : elle utilise la distribution stationnaire des rendements estimée sur toute la période historique. Une VaR *conditionnelle* (par exemple basée sur un modèle GARCH) utilise la distribution des rendements *sachant* la volatilité courante $\sigma_t^2$. Si le VIX est actuellement à 30 (volatilité élevée), la VaR conditionnelle sera plus élevée que la VaR unconditionnelle. En période de calme (VIX à 12), elle sera plus basse. La VaR conditionnelle est plus utile pour le pilotage quotidien du risque, mais plus complexe à estimer et à valider.

---

### Q24 : Pourquoi les corrélations augmentent-elles en période de crise ?

**Réponse courte** : Parce que les marchés répondent aux mêmes chocs systémiques simultanément (flight to quality, appels de marges, ventes forcées).

**Réponse détaillée** : En période de stress, plusieurs mécanismes poussent les corrélations vers 1 : (1) **Chocs systémiques** : une crise bancaire ou une récession touche tous les marchés en même temps. (2) **Appels de marges** : quand des fonds à levier subissent des pertes, ils doivent vendre leurs positions les plus liquides (souvent les actions US) pour couvrir leurs marges, propageant la baisse à des actifs initialement non concernés. (3) **Réduction du levier** : les banques réduisent leur bilan en vendant toutes leurs positions. Ce phénomène de "corrélation de crise" est la principale limite pratique de la diversification.

---

### Q25 : En quoi consiste la mesure de risque cohérente selon Artzner et al. (1999) ?

**Réponse courte** : Une mesure de risque cohérente satisfait quatre axiomes : monotonie, invariance par translation, homogénéité positive et sous-additivité.

**Réponse détaillée** : Les quatre axiomes garantissent que la mesure de risque se comporte de façon "raisonnable" : (A1) un portefeuille qui domine toujours un autre est moins risqué ; (A2) ajouter du cash réduit le risque d'autant ; (A3) doubler les positions double le risque ; (A4) la diversification est toujours bénéfique. La VaR satisfait (A1)-(A3) mais pas toujours (A4), ce qui est problématique dans un contexte de portefeuille. L'ES satisfait les quatre, ce qui justifie son adoption par Bâle III.

---

### Q26 : Comment fonctionnent les copules en finance quantitative ?

**Réponse courte** : Les copules séparent la modélisation des distributions marginales des actifs individuels de la modélisation de leur structure de dépendance.

**Réponse détaillée** : Par le théorème de Sklar, toute distribution conjointe $F(x_1, \ldots, x_n)$ peut être décomposée en $F(x_1,\ldots,x_n) = C(F_1(x_1), \ldots, F_n(x_n))$ où $C$ est une copule (distribution uniforme sur $[0,1]^n$) et les $F_i$ sont les marginales. Une copule de Student-t modélise une dépendance de queue symétrique (corrélations élevées dans les deux queues). Une copule de Clayton modélise une dépendance de queue inférieure (corrélations plus élevées dans les pertes extrêmes) — plus réaliste pour les marchés financiers en crise. Les copules permettent de conserver des marginales non-gaussiennes tout en choisissant indépendamment la structure de dépendance.

---

### Q27 : Comment fonctionne le maximum de vraisemblance pour estimer les degrés de liberté d'une Student-t ?

**Réponse courte** : On cherche le $\nu$ qui maximise la probabilité d'observer les données sous la distribution Student-t $t_\nu$.

**Réponse détaillée** : Étant données les données historiques $r_1, \ldots, r_T$, la log-vraisemblance sous Student-t avec $\nu$ degrés de liberté est $\ell(\nu) = \sum_t \ln f_\nu(r_t)$ où $f_\nu$ est la densité de la Student-t. On peut maximiser numériquement cette fonction en $\nu$ (par exemple via `scipy.optimize.minimize_scalar`). Le MLE $\hat{\nu}$ est l'estimateur optimal sous des conditions de régularité. Dans cette version du projet, les degrés de liberté sont fixés dans `config.yaml` avec `simulation.student_df`; l'estimation MLE est une extension naturelle.

---

### Q28 : Quelle est la différence entre la VaR 1 jour de Bâle II et la VaR/ES de Bâle III ?

**Réponse courte** : Bâle II utilise la VaR à 99% sur 10 jours ; Bâle III (FRTB) remplace la VaR par l'ES à 97.5% sur 10 jours.

**Réponse détaillée** : Bâle II (2004) impose une VaR à 99% sur un horizon de 10 jours (via la règle $\sqrt{10}$) pour calculer la charge de capital en risque de marché. La crise de 2008 a révélé que cette mesure était insuffisante pour capter les risques de queue. La FRTB (Fundamental Review of the Trading Book), publiée en 2016 et entrant en vigueur progressivement depuis 2022, impose une ES à 97.5% sur 10 jours. L'ES à 97.5% est similaire numériquement à la VaR à 99% dans une distribution normale, mais est beaucoup plus sensible aux queues épaisses. Elle est aussi cohérente (sous-additive), ce qui favorise la diversification.

---

### Q29 : Comment calculer analytiquement la contribution de chaque actif au risque sous hypothèse gaussienne ?

**Réponse courte** : La contribution de l'actif $i$ est $\text{MC}_i = V \cdot z_\alpha \cdot w_i(\boldsymbol{\Sigma}\mathbf{w})_i / \sigma_p$.

**Réponse détaillée** : Sous hypothèse gaussienne, $\text{VaR} = V \cdot (z_\alpha\sigma_p - \mu_p)$. On calcule la dérivée partielle :
$$\frac{\partial\text{VaR}}{\partial w_i} = V \cdot z_\alpha \cdot \frac{(\boldsymbol{\Sigma}\mathbf{w})_i}{\sigma_p}$$
La contribution marginale est $\text{MC}_i = w_i \cdot \partial\text{VaR}/\partial w_i$. Par le théorème d'Euler (VaR homogène de degré 1 en $\mathbf{w}$), $\sum_i \text{MC}_i = \text{VaR}$. La contribution relative $\text{RC}_i = \text{MC}_i/\text{VaR} = w_i(\boldsymbol{\Sigma}\mathbf{w})_i / \sigma_p^2$ indique la part de risque attribuable à chaque actif.

---

### Q30 : Qu'est-ce que le "smile de volatilité" et en quoi remet-il en question l'hypothèse gaussienne ?

**Réponse courte** : Le smile de volatilité montre que la volatilité implicite des options varie avec le prix d'exercice — ce qui contredit la distribution log-normale supposée par Black-Scholes.

**Réponse détaillée** : Dans le modèle de Black-Scholes, la volatilité implicite devrait être constante quel que soit le strike. En pratique, les options profondes dans la monnaie (deep out-of-the-money) ont des volatilités implicites plus élevées que les options at-the-money. Cela forme une courbe en "smile" (ou "skew" pour les indices d'actions, avec une volatilité plus élevée pour les puts OTM que pour les calls OTM). Ce phénomène est la signature empirique des queues épaisses et de l'asymétrie — exactement ce que la distribution de Student-t capture mieux que la gaussienne.

---

## Partie 4 — Questions sur le code et l'implémentation

---

### Q31 : Comment le code génère-t-il les 50 000 scénarios corrélés ?

**Réponse courte** : Il génère 50 000 vecteurs gaussiens indépendants de dimension 5, puis les transforme par la matrice de Cholesky de la covariance.

**Réponse détaillée** : Le code utilise `rng.standard_normal((50000, 5))` pour créer une matrice de nombres gaussiens indépendants, puis applique `Z @ L.T` où `L = np.linalg.cholesky(cov)`. Cette transformation induit exactement la structure de covariance souhaitée. En cas de distribution Student-t, chaque ligne est également divisée par $\sqrt{\chi^2_\nu/\nu}$ pour épaissir les queues.

---

### Q32 : Pourquoi utilise-t-on une graine aléatoire fixe dans le code ?

**Réponse courte** : Pour assurer la reproductibilité : toujours obtenir les mêmes résultats avec les mêmes données d'entrée.

**Réponse détaillée** : NumPy utilise un générateur de nombres pseudo-aléatoires. En fixant la graine, on détermine entièrement la séquence de nombres "aléatoires" générés. Cela permet à n'importe qui de reproduire exactement les mêmes résultats en réexécutant le code — crucial pour les tests, le débogage et la comparabilité des résultats entre collègues. En production, on pourrait vouloir ne pas fixer la graine pour avoir une exploration véritablement stochastique.

---

### Q33 : Comment le code gère-t-il les valeurs manquantes dans les données de prix ?

**Réponse courte** : Par forward-fill (propagation de la dernière valeur connue) pour les jours fériés, et suppression des lignes entièrement manquantes.

**Réponse détaillée** : Les actifs ont des jours fériés différents (marché US vs marchés européens vs or/forex). Yahoo Finance retourne des NaN pour ces jours. Le `fillna(method='ffill')` propage le dernier prix connu (ce qui donne un log-return de 0 ce jour-là, hypothèse raisonnable pour la liquidité théorique). Les premières observations (NaN avant la première cotation) sont supprimées par `dropna()`.

---

### Q34 : Que se passe-t-il si la matrice de covariance n'est pas définie positive ?

**Réponse courte** : `np.linalg.cholesky()` lève une exception `LinAlgError` et la simulation échoue.

**Réponse détaillée** : Une matrice de covariance mal conditionnée peut apparaître si les actifs ont des séries de longueurs différentes ou si certains actifs sont linéairement dépendants. Solutions : (1) régularisation de Ledoit-Wolf : `sklearn.covariance.LedoitWolf().fit(returns)` ; (2) correction de la plus petite valeur propre : remplacer les valeurs propres négatives ou nulles par une petite valeur positive ; (3) réduction de dimensionnalité (PCA). Pour notre projet à 5 actifs avec 1000+ observations, ce problème ne devrait pas survenir.

---

### Q35 : Comment le code calcule-t-il l'ES Monte Carlo ?

**Réponse courte** : Il filtre les pertes supérieures à la VaR et prend leur moyenne.

**Réponse détaillée** : En Python : `tail_losses = losses[losses > var_threshold]` sélectionne les ~500 pires pertes (1% de 50 000). Puis `tail_losses.mean()` donne l'ES. C'est l'estimateur empirique direct. Sa variance est plus faible que celle de la VaR (car l'ES utilise plus d'observations), ce qui rend l'ES MC plus stable que la VaR MC pour des $N$ modérés.

---

### Q36 : Pourquoi utilise-t-on `np.log(prices / prices.shift(1))` plutôt que `prices.pct_change()` ?

**Réponse courte** : Pour calculer des rendements logarithmiques (additifs dans le temps) plutôt que des rendements arithmétiques (pas additifs).

**Réponse détaillée** : `prices.pct_change()` calcule $(P_t - P_{t-1})/P_{t-1}$, le rendement arithmétique. `np.log(prices / prices.shift(1))` calcule $\ln(P_t/P_{t-1})$, le rendement log. Les deux sont quasi-identiques pour des variations < 5%, mais les log-returns sont additifs : $r_{0\to T} = \sum r_{t\to t+1}$, ce qui simplifie les calculs multi-périodes et les agrégations temporelles. La plupart des modèles financiers théoriques sont construits avec des log-returns.

---

## Partie 5 — Questions critiques et de jugement

---

### Q37 : Dans quels cas la VaR Monte Carlo peut-elle être moins fiable que la VaR historique ?

**Réponse courte** : Quand le modèle de simulation est mal spécifié (mauvaise distribution, mauvaise matrice de covariance).

**Réponse détaillée** : La VaR Monte Carlo est "model-dependent" : elle ne peut simuler que ce que le modèle peut représenter. Si la vraie distribution est très asymétrique et que le modèle ne capture pas cette asymétrie, la VaR MC sera biaisée. La VaR historique, elle, utilise directement les données passées sans hypothèse de distribution. Dans des périodes stables avec beaucoup de données, la VaR historique peut être préférée. La VaR MC est supérieure quand on veut explorer des scénarios au-delà du passé observé.

---

### Q38 : Si vous deviez améliorer ce projet en priorité, que feriez-vous ?

**Réponse courte** : Implémenter un modèle GARCH pour la volatilité conditionnelle et ajouter des scénarios de stress historiques.

**Réponse détaillée** : La limitation la plus sérieuse est l'hypothèse de stationnarité. Un GARCH(1,1) permettrait d'obtenir une VaR qui varie dans le temps selon le régime de volatilité — bien plus réaliste pour la gestion quotidienne. En second priorité, des scénarios de stress (rejeu de 2008, 2020) seraient très utiles pour la communication aux stakeholders et comme complément à l'approche statistique. Enfin, un backtesting out-of-sample (estimer sur 2020-2022, tester sur 2023-2024) serait plus rigoureux que le backtesting in-sample actuel.

---

### Q39 : Comment répondriez-vous à un régulateur qui vous demande pourquoi votre VaR est plus basse que celle d'un concurrent ?

**Réponse courte** : La différence peut s'expliquer par la composition du portefeuille, la fenêtre historique, les hypothèses de distribution ou le nombre de simulations.

**Réponse détaillée** : Une VaR plus basse n'est pas nécessairement meilleure ou pire — elle peut refléter une composition différente (portefeuille plus diversifié), une période d'estimation incluant moins de stress, ou des hypothèses plus optimistes (gaussianité vs Student-t). Pour répondre à un régulateur, on comparerait les hypothèses (distribution, fenêtre, niveau de confiance), validerait par backtesting, et montrerait que le modèle est conservateur en cas de stress (les résultats de sensibilité à la volatilité sont utiles ici). L'essentiel est de démontrer que le modèle est documenté, calibré sur des données récentes et validé empiriquement.

---

### Q40 : Quelle est la différence entre la VaR utilisée pour le capital réglementaire et la VaR utilisée pour la gestion interne ?

**Réponse courte** : La VaR réglementaire est calibrée pour le pire cas et soumise à des règles strictes ; la VaR de gestion interne est ajustée aux besoins opérationnels de l'institution.

**Réponse détaillée** : Bâle III impose des paramètres spécifiques (ES à 97.5%, horizon 10 jours, fenêtre d'observation incluant une période de stress). Cette VaR réglementaire détermine le capital minimum que la banque doit détenir — c'est une mesure de protection des créanciers et du système financier. La VaR interne peut être à 95% sur 1 jour (plus sensible aux variations quotidiennes, utile pour les limites de trading), sur 10 jours (pour la gestion du risque de liquidation), ou à 99.9% (pour les décisions de couverture de queue). Les deux coexistent dans une banque sophistiquée avec des objectifs différents.

---

### Q41 : Pourquoi Bâle III a-t-il remplacé la VaR par l'ES ?

**Réponse courte** : Parce que la crise de 2008 a montré que la VaR ne capturait pas les risques de queue, et parce que l'ES est théoriquement supérieure (cohérence, sensibilité aux queues).

**Réponse détaillée** : Avant 2008, les VaR des grandes banques indiquaient des risques modérés. Pourtant, les pertes réalisées ont été cataclysmiques. L'examen post-crise a révélé trois problèmes : (1) les modèles sous-estimaient les corrélations de crise ; (2) la VaR ne mesurait pas l'ampleur des pertes au-delà du seuil ; (3) les banques optimisaient pour réduire leur VaR en concentrant les risques dans la queue extrême. L'ES à 97.5% adresse directement le point (2). Les niveaux de 97.5% ont été choisis pour que l'ES sous gaussienne soit comparable à la VaR à 99% (les deux correspondent environ au même quantile sous une distribution normale), assurant une continuité approximative avec Bâle II.

---

### Q42 : Que signifie qu'un modèle de risque "échoue" au backtesting et quelles sont les conséquences ?

**Réponse courte** : Un modèle qui échoue présente trop d'exceptions (ou trop peu) — les pertes réelles dévient systématiquement des prédictions.

**Réponse détaillée** : Bâle II définit des "zones" pour le backtesting annuel (250 jours) d'une VaR à 99% : zone verte (0-4 exceptions), zone jaune (5-9 exceptions), zone rouge (10+ exceptions). Dans la zone rouge, la banque doit multiplier sa charge de capital par un facteur pouvant atteindre 4 — ce qui est extrêmement pénalisant. Un modèle qui échoue systématiquement doit être revu, recalibré, ou remplacé. Les conséquences incluent aussi une surveillance accrue des régulateurs et une atteinte à la réputation de l'institution.

---

### Q43 : Comment expliquer la VaR à quelqu'un qui ne connaît pas la finance ?

**Réponse courte** : "Si vous jouez à pile ou face 100 fois, combien perdez-vous dans le pire cas les 99 fois où vous gagnez ? C'est ça la VaR — le montant que vous ne perdrez pas la plupart du temps."

**Réponse détaillée** : Une analogie météo fonctionne bien : "La météo annonce 95% de chances qu'il ne pleuve pas plus de 10 mm demain. La VaR à 95% est similaire : il y a 95% de chances que votre portefeuille ne perde pas plus de X euros demain. Comme la météo, c'est une probabilité, pas une certitude — il reste 5% de chances que la pluie dépasse 10 mm, et 5% de chances que vos pertes dépassent X euros." La VaR n'est pas la perte maximale possible, exactement comme 10 mm de pluie n'est pas le maximum météo imaginable.

---

### Q44 : En quoi les ETF facilitent-ils la modélisation par rapport aux actions individuelles ?

**Réponse courte** : Les ETF sont déjà diversifiés, liquides, et leurs séries temporelles sont longues et stables — ils évitent les problèmes de survie et de liquidité des actions individuelles.

**Réponse détaillée** : Un ETF comme SPY réplique le S&P 500 — il est extrêmement liquide, a des données remontant à 1993, ne peut pas faire faillite (il peut être liquidé mais pas défaillant), et son niveau de prix reflète le rendement total ajusté des dividendes. Des actions individuelles peuvent être dellistées, avoir des gaps de données, présenter du biais de survivance, et être très peu liquides (spread bid-ask élevé). Pour un modèle de VaR académique, les ETF sont idéaux car ils permettent de se concentrer sur la méthodologie sans biais de données.

---

### Q45 : Que penser du fait que les trois méthodes donnent des résultats proches ?

**Réponse courte** : C'est un signal de robustesse — la distribution de ce portefeuille est raisonnablement proche d'une gaussienne, ce qui valide les hypothèses des méthodes simples.

**Réponse détaillée** : La convergence des trois méthodes indique que : (1) la période historique est représentative (pas dominée par un seul événement extrême) ; (2) la distribution des rendements du portefeuille est approximativement normale (bénéfice de diversification et TCL) ; (3) le modèle Monte Carlo est bien calibré. Si les méthodes divergeaient significativement (par exemple, historique à 13 000 EUR mais MC à 25 000 EUR), cela indiquerait soit un problème de calibration MC, soit la présence d'un régime de crise exceptionnel dans les données historiques.

---

### Q46 : Quel est l'impact du choix du nombre de simulations (50 000) sur les résultats ?

**Réponse courte** : Plus de simulations réduisent la variance d'estimation, mais avec des rendements décroissants — 50 000 est un bon compromis précision/temps de calcul.

**Réponse détaillée** : L'erreur standard de la VaR MC à 99% est proportionnelle à $1/\sqrt{N}$. Avec $N = 50\,000$, l'erreur est de l'ordre de ±60 EUR. Doubler à 100 000 simulations ne réduirait cette erreur que de $\sqrt{2} \approx 1.41$ fois — gain modeste pour un doublement du temps de calcul. En dessous de 10 000 simulations, l'erreur devient significative (±130 EUR à 99%). 50 000 est le standard usuel pour ce type de modèle.

---

### Q47 : Comment construire un intervalle de confiance pour la VaR Monte Carlo ?

**Réponse courte** : Par bootstrap : rééchantillonner $B$ fois les $N$ simulations et calculer la VaR sur chaque échantillon pour obtenir la distribution empirique de la VaR.

**Réponse détaillée** : On dispose de $N = 50\,000$ pertes simulées $L_1, \ldots, L_N$. Pour construire un intervalle de confiance à 95% sur la VaR à 99% : (1) tirer $B = 1000$ fois un échantillon de $N$ observations avec remise ; (2) calculer la VaR à 99% sur chaque échantillon $\hat{V}_b$ ; (3) prendre les percentiles 2.5% et 97.5% de la distribution $(\hat{V}_1, \ldots, \hat{V}_{1000})$. Alternativement, l'intervalle asymptotique de normalité donne : $\text{VaR} \pm 1.96 \times \sqrt{\alpha(1-\alpha)} / (N^{1/2} f(\text{VaR}))$.

---

### Q48 : Pourquoi EURUSD est-il inclus dans un portefeuille multi-actifs libellé en EUR ?

**Réponse courte** : Parce que les actifs libellés en dollars (SPY, EFA, AGG, GLD) exposent l'investisseur européen à un risque de change EUR/USD.

**Réponse détaillée** : Un investisseur européen qui achète SPY (libellé en USD) est exposé à deux risques : les mouvements du S&P 500, et les mouvements EUR/USD. Si l'EUR s'apprécie contre l'USD, la valeur en euros de SPY diminue même si le S&P 500 stagne. Le taux EURUSD dans notre portefeuille représente cette exposition implicite. La façon correcte de la modéliser serait de calculer les rendements des actifs USD en EUR : $r_{SPY,EUR} = r_{SPY,USD} + r_{EURUSD}$. L'inclusion explicite d'EURUSD comme actif avec un poids de 10% est une simplification — en réalité, tous les actifs USD ont une exposition implicite à EURUSD.

---

### Q49 : Si le test de Kupiec échouait (trop d'exceptions), que feriez-vous ?

**Réponse courte** : Analyser les exceptions pour comprendre si elles sont clustérisées, recalibrer le modèle avec une fenêtre plus récente, ou utiliser une distribution plus conservatrice.

**Réponse détaillée** : En cas d'échec : (1) **Diagnostic** : vérifier si les exceptions sont concentrées sur une période (indique un changement de régime) ou dispersées (indique une sous-estimation structurelle). (2) **Recalibration** : utiliser une fenêtre plus récente (250 jours vs 1000 jours) pour mieux refléter le régime actuel. (3) **Distribution** : passer de gaussienne à Student-t ou réduire les degrés de liberté. (4) **Ajustement réglementaire** : sous Bâle, un multiplicateur ($\times 1.5$ à $\times 4$) est appliqué si le nombre d'exceptions est trop élevé.

---

### Q50 : Comment présenteriez-vous ce projet à un jury de M1 en 5 minutes ?

**Réponse courte** : Commencer par le problème business (combien peut-on perdre ?), présenter les méthodes, les résultats clés, et conclure par les limites et extensions.

**Réponse détaillée** : Voir le fichier `07_oral_defense.md` pour le plan détaillé. En 5 minutes, la structure idéale est : (1) 45 sec — contexte et problème ; (2) 90 sec — les trois méthodes et leurs hypothèses (avec tableau comparatif) ; (3) 60 sec — résultats numériques clés (VaR MC 99% = 13 162 EUR = 1.32%, ES 99% = 14 993 EUR, Kupiec VALIDE) ; (4) 45 sec — limites honnêtes (stationnarité, corrélations de crise) ; (5) 30 sec — extension principale (GARCH, copules). Ne jamais oublier de lier les chiffres à leur interprétation concrète.
