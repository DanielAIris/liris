"""
Templates pour les opérations de brainstorming
"""

# Templates de prompts pour les différentes phases
SOLUTION_TEMPLATE = """
BRAINSTORMING: PROBLÈME À RÉSOUDRE

{context}

Instructions:
1. Analysez attentivement le problème ci-dessus
2. Proposez une solution innovante et détaillée
3. Expliquez pourquoi cette solution est efficace
4. Présentez les avantages et inconvénients de votre approche
5. Soyez créatif et pensez hors des sentiers battus

Votre solution complète:
"""

EVALUATION_TEMPLATE = """
ÉVALUATION DE SOLUTION

CONTEXTE DU PROBLÈME:
{context}

SOLUTION À ÉVALUER (proposée par {platform}):
{solution}

Instructions d'évaluation:
1. Analysez la solution proposée par rapport au problème
2. Évaluez les points forts et les faiblesses
3. Notez l'originalité et la faisabilité
4. Proposez des améliorations possibles
5. Attribuez un score de 0 à 100 en justifiant

Votre évaluation complète (terminez par 'SCORE: X/100'):
"""

SCORING_TEMPLATE = """
SCORING FINAL DE SOLUTION

CONTEXTE DU PROBLÈME:
{context}

SOLUTION DE {platform}:
{solution}

ÉVALUATIONS DES AUTRES IA:
{evaluations}

Instructions de scoring:
1. Analysez la solution et les évaluations reçues
2. Identifiez les points communs et divergents dans les évaluations
3. Évaluez la pertinence des critiques
4. Déterminez un score final objectif sur 100
5. Justifiez votre décision en quelques lignes

Votre analyse et score final (terminez par 'SCORE FINAL: X/100'):
"""

# Templates pour l'exportation des résultats
EXPORT_TEXT_TEMPLATE = """
RÉSULTATS DE BRAINSTORMING: {session_name}
==========================================================================
Date: {date}
Plateformes IA: {platforms}

CONTEXTE:
--------------------------------------------------------------------------
{context}
--------------------------------------------------------------------------

SOLUTIONS PROPOSÉES:
==========================================================================
{solutions}

CLASSEMENT FINAL:
==========================================================================
{ranking}
"""

SOLUTION_TEXT_TEMPLATE = """
SOLUTION #{index} - {platform}
--------------------------------------------------------------------------
{solution}

SCORE: {score}/100

ÉVALUATIONS:
{evaluations}
==========================================================================
"""

EVALUATION_TEXT_TEMPLATE = """
- {evaluator}: {evaluation_summary}
"""

# Fonctions d'accès aux templates

def get_solution_prompt():
    """Retourne le template pour les prompts de génération de solution"""
    return SOLUTION_TEMPLATE

def get_evaluation_prompt():
    """Retourne le template pour les prompts d'évaluation"""
    return EVALUATION_TEMPLATE

def get_scoring_prompt():
    """Retourne le template pour les prompts de scoring"""
    return SCORING_TEMPLATE

def get_export_text_template():
    """Retourne le template pour l'exportation texte des résultats"""
    return EXPORT_TEXT_TEMPLATE

def get_solution_text_template():
    """Retourne le template pour le formatage texte d'une solution"""
    return SOLUTION_TEXT_TEMPLATE

def get_evaluation_text_template():
    """Retourne le template pour le formatage texte d'une évaluation"""
    return EVALUATION_TEXT_TEMPLATE