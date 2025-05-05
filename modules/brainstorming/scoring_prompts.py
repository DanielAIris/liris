"""
Prompts pour le scoring final des solutions de brainstorming
"""


def get_scoring_prompt():
    """
    Retourne le prompt pour le scoring final des solutions

    Returns:
        str: Template de prompt
    """
    return """
SCORING FINAL DE SOLUTION DE BRAINSTORMING

CONTEXTE DU PROBLÈME:
{context}

SOLUTION DE {platform}:
{solution}

ÉVALUATIONS DES AUTRES IA:
{evaluations}

Votre mission:
-------------
En tant qu'arbitre final, vous devez analyser la solution proposée ainsi que toutes
les évaluations reçues pour déterminer un score final objectif.

Instructions:
1. Analysez attentivement la solution originale par rapport au problème
2. Examinez toutes les évaluations fournies par les autres IA
3. Identifiez les points de consensus et de divergence dans les évaluations
4. Évaluez la pertinence et la justesse des critiques émises
5. Établissez un score final impartial qui reflète la qualité réelle de la solution
6. Justifiez votre décision de manière claire et objective

Critères pour la méta-évaluation:
1. Qualité intrinsèque de la solution (50%)
2. Consensus des évaluateurs (30%)
3. Prise en compte des critiques constructives (20%)

Format de réponse:
-----------------
* MÉTA-ANALYSE DE LA SOLUTION
* SYNTHÈSE DES ÉVALUATIONS
  - Points de consensus
  - Points de divergence
  - Évaluation de la pertinence des critiques
* JUGEMENT FINAL
  - Qualité intrinsèque: [analyse] - [impact sur le score]
  - Consensus des évaluateurs: [analyse] - [impact sur le score]
  - Prise en compte des critiques: [analyse] - [impact sur le score]
* JUSTIFICATION DU SCORE FINAL
* SCORE FINAL: [X]/100

Votre scoring final et objectif:
"""


def get_scoring_prompt_detailed():
    """
    Retourne le prompt pour le scoring détaillé des solutions

    Returns:
        str: Template de prompt
    """
    return """
SCORING DÉTAILLÉ DE SOLUTION DE BRAINSTORMING

CONTEXTE DU PROBLÈME:
{context}

SOLUTION DE {platform}:
{solution}

ÉVALUATIONS DES AUTRES IA:
{evaluations}

Votre mission:
-------------
En tant qu'expert en méta-évaluation, vous devez réaliser une analyse approfondie de la solution
et des évaluations pour produire un score final qui tient compte de multiples dimensions.

Instructions:
1. Analysez la solution originale selon les dix critères standards
2. Examinez chaque évaluation pour identifier les biais potentiels
3. Pondérez la crédibilité de chaque évaluateur en fonction de la qualité de son analyse
4. Triangulée les perspectives multiples pour obtenir une vision holistique
5. Déterminez un score composite qui reflète une évaluation multidimensionnelle
6. Fournissez une justification détaillée par dimension

Dimensions d'évaluation composite:
1. Mérite technique (30%)
   - Pertinence et efficacité
   - Faisabilité technique
   - Robustesse
2. Valeur d'innovation (25%)
   - Originalité
   - Potentiel disruptif
   - Perspective unique
3. Viabilité pratique (25%)
   - Faisabilité économique
   - Facilité d'implémentation
   - Durabilité
4. Qualité de communication (10%)
   - Clarté de la présentation
   - Structure logique
   - Argumentation
5. Réactivité aux critiques (10%)
   - Anticipation des objections
   - Réponses aux faiblesses identifiées

Format de réponse:
-----------------
* ANALYSE MULTIDIMENSIONNELLE
* MÉTA-ÉVALUATION DES CRITIQUES
  - Analyse de la qualité des évaluations
  - Biais identifiés
  - Pondération des perspectives
* ÉVALUATION COMPOSITE PAR DIMENSION
  [Pour chacune des 5 dimensions]
* SYNTHÈSE FINALE JUSTIFIÉE
* SCORE FINAL: [X]/100

Votre méta-évaluation détaillée:
"""


def get_scoring_prompt_comparative():
    """
    Retourne le prompt pour le scoring comparatif des solutions

    Returns:
        str: Template de prompt
    """
    return """
SCORING COMPARATIF DE SOLUTIONS DE BRAINSTORMING

CONTEXTE DU PROBLÈME:
{context}

SOLUTION PRINCIPALE ({main_platform}):
{main_solution}

SOLUTIONS CONCURRENTES:
{competing_solutions}

ÉVALUATIONS:
{evaluations}

Votre mission:
-------------
Vous devez évaluer la solution principale en la comparant explicitement aux solutions concurrentes,
tout en tenant compte des évaluations reçues.

Instructions:
1. Analysez la solution principale par rapport au problème posé
2. Comparez-la directement avec chacune des solutions concurrentes
3. Identifiez les avantages et inconvénients relatifs
4. Examinez les évaluations reçues dans ce contexte comparatif
5. Déterminez un classement relatif et un score absolu
6. Justifiez votre décision en termes de positionnement relatif

Aspects à considérer:
1. Avantages distinctifs (30%)
2. Faiblesses relatives (30%)
3. Positionnement global (40%)

Format de réponse:
-----------------
* ANALYSE DE LA SOLUTION PRINCIPALE
* COMPARAISON DIRECTE:
  [Pour chaque solution concurrente]
  - Avantages relatifs
  - Inconvénients relatifs
  - Différenciateurs clés
* SYNTHÈSE DES ÉVALUATIONS DANS LE CONTEXTE COMPARATIF
* POSITIONNEMENT FINAL ET JUSTIFICATION
* CLASSEMENT: [position]/[total]
* SCORE FINAL: [X]/100

Votre évaluation comparative:
"""