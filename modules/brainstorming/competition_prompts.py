"""
Prompts pour la compétition de brainstorming entre IA
"""


def get_solution_prompt():
    """
    Retourne le prompt pour la génération de solution

    Returns:
        str: Template de prompt
    """
    return """
BRAINSTORMING COMPÉTITIF: PROBLÈME À RÉSOUDRE

{context}

Votre mission:
-------------
Vous participez à une compétition d'IA pour résoudre ce problème. Votre solution sera évaluée
par les autres IA participantes et un classement sera établi.

Instructions:
1. Analysez attentivement le problème ci-dessus
2. Proposez une solution innovante, détaillée et structurée
3. Expliquez clairement votre raisonnement et votre démarche
4. Présentez les avantages compétitifs de votre solution
5. Anticipez et répondez aux objections possibles
6. Soyez créatif mais pragmatique

Format de réponse:
-----------------
* RÉSUMÉ DE LA SOLUTION (2-3 phrases)
* ANALYSE DU PROBLÈME
* SOLUTION PROPOSÉE (détaillée)
* MISE EN ŒUVRE
* AVANTAGES ET INCONVÉNIENTS
* CONCLUSION

Votre solution complète:
"""


def get_solution_prompt_creative():
    """
    Retourne le prompt pour la génération de solution créative

    Returns:
        str: Template de prompt
    """
    return """
BRAINSTORMING CRÉATIF: PROBLÈME À RÉSOUDRE

{context}

Vous êtes invité à penser de manière radicalement innovante! Oubliez les contraintes
conventionnelles et proposez une solution véritablement disruptive.

Instructions:
1. Commencez par une analyse non conventionnelle du problème
2. Proposez au moins une approche qui n'a jamais été envisagée auparavant
3. Utilisez des analogies de domaines complètement différents
4. Ne vous censurez pas - les idées les plus audacieuses sont bienvenues
5. Développez ensuite comment cette approche radicale pourrait être réalisée

Format de réponse:
-----------------
* VISION DISRUPTIVE (résumé de votre approche révolutionnaire)
* REDÉFINITION DU PROBLÈME
* SOLUTION NON CONVENTIONNELLE
* INSPIRATION TRANSDISCIPLINAIRE (d'où vient cette idée)
* MISE EN ŒUVRE CONCRÈTE
* IMPACT POTENTIEL

Votre solution créative:
"""


def get_solution_prompt_analytical():
    """
    Retourne le prompt pour la génération de solution analytique

    Returns:
        str: Template de prompt
    """
    return """
BRAINSTORMING ANALYTIQUE: PROBLÈME À RÉSOUDRE

{context}

Vous êtes sollicité pour une approche rigoureusement analytique du problème.
La précision et la rigueur de votre analyse seront particulièrement valorisées.

Instructions:
1. Décomposez méthodiquement le problème en composantes distinctes
2. Analysez chaque facteur avec une approche factuelle et quantitative si possible
3. Proposez une solution fondée sur des données et des méthodes éprouvées
4. Évaluez systématiquement les coûts, bénéfices et risques
5. Intégrez les contraintes pratiques et réglementaires applicables

Format de réponse:
-----------------
* SYNTHÈSE EXÉCUTIVE
* ANALYSE DÉTAILLÉE DU PROBLÈME (facteurs, composantes, métriques)
* MÉTHODOLOGIE
* SOLUTION PROPOSÉE
* ANALYSE COÛTS-BÉNÉFICES
* ÉVALUATION DES RISQUES
* PLAN D'IMPLÉMENTATION

Votre solution analytique:
"""


def get_solution_prompt_collaborative():
    """
    Retourne le prompt pour la génération de solution collaborative

    Returns:
        str: Template de prompt
    """
    return """
BRAINSTORMING COLLABORATIF: PROBLÈME À RÉSOUDRE

{context}

Dans cette approche collaborative, considérez votre solution comme une contribution
à un effort collectif. Votre proposition sera combinée avec celles d'autres IA.

Instructions:
1. Analysez le problème en identifiant les aspects où votre expertise est la plus forte
2. Proposez une solution qui pourrait se compléter avec d'autres approches
3. Indiquez clairement les interfaces où votre solution pourrait s'intégrer à d'autres
4. Identifiez les zones où d'autres expertises seraient bienvenues
5. Suggérez des pistes pour améliorer collectivement la solution

Format de réponse:
-----------------
* CONTRIBUTION PRINCIPALE (résumé de votre apport spécifique)
* ANALYSE COLLABORATIVE DU PROBLÈME
* SOLUTION PROPOSÉE
* POINTS D'INTÉGRATION
* DOMAINES COMPLÉMENTAIRES
* VISION COLLECTIVE

Votre proposition collaborative:
"""