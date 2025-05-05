"""
Prompts pour l'évaluation des solutions de brainstorming
"""


def get_evaluation_prompt():
    """
    Retourne le prompt pour l'évaluation des solutions

    Returns:
        str: Template de prompt
    """
    return """
ÉVALUATION DE SOLUTION DE BRAINSTORMING

CONTEXTE DU PROBLÈME:
{context}

SOLUTION À ÉVALUER (proposée par {platform}):
{solution}

Votre mission:
-------------
Vous êtes désigné comme évaluateur expert pour analyser cette solution proposée.
Votre évaluation doit être impartiale, constructive et détaillée.

Critères d'évaluation:
1. Pertinence (20 points) - La solution répond-elle directement au problème posé?
2. Innovation (20 points) - La solution apporte-t-elle des idées nouvelles et créatives?
3. Faisabilité (20 points) - La solution est-elle réalisable avec les technologies actuelles?
4. Efficacité (20 points) - La solution résout-elle efficacement le problème?
5. Complétude (20 points) - La solution traite-t-elle tous les aspects du problème?

Instructions:
1. Analysez méticuleusement la solution par rapport au problème
2. Évaluez chaque critère individuellement avec justification
3. Identifiez clairement les points forts et les faiblesses
4. Proposez des améliorations concrètes
5. Attribuez un score global sur 100

Format de réponse:
-----------------
* SYNTHÈSE DE L'ÉVALUATION (2-3 phrases)
* ANALYSE PAR CRITÈRE:
  - Pertinence: [analyse] - [X/20]
  - Innovation: [analyse] - [X/20]
  - Faisabilité: [analyse] - [X/20]
  - Efficacité: [analyse] - [X/20]
  - Complétude: [analyse] - [X/20]
* FORCES DE LA SOLUTION
* FAIBLESSES DE LA SOLUTION
* PISTES D'AMÉLIORATION
* SCORE: [total]/100

Votre évaluation complète:
"""


def get_evaluation_prompt_detailed():
    """
    Retourne le prompt pour l'évaluation détaillée des solutions

    Returns:
        str: Template de prompt
    """
    return """
ÉVALUATION DÉTAILLÉE DE SOLUTION DE BRAINSTORMING

CONTEXTE DU PROBLÈME:
{context}

SOLUTION À ÉVALUER (proposée par {platform}):
{solution}

Votre mission:
-------------
Réalisez une analyse approfondie et critique de cette solution en tant qu'expert du domaine.
Votre évaluation doit explorer en profondeur chaque aspect de la proposition.

Critères d'évaluation élargis:
1. Pertinence (10 points) - La solution répond-elle directement au problème posé?
2. Innovation (10 points) - La solution apporte-t-elle des idées nouvelles et créatives?
3. Faisabilité technique (10 points) - La solution est-elle réalisable techniquement?
4. Faisabilité économique (10 points) - La solution est-elle viable économiquement?
5. Efficacité (10 points) - La solution résout-elle efficacement le problème?
6. Complétude (10 points) - La solution traite-t-elle tous les aspects du problème?
7. Scalabilité (10 points) - La solution peut-elle être déployée à grande échelle?
8. Durabilité (10 points) - La solution est-elle durable à long terme?
9. Présentation (10 points) - La solution est-elle clairement expliquée et structurée?
10. Impact potentiel (10 points) - La solution pourrait-elle avoir un impact significatif?

Instructions:
1. Examinez la solution sous tous les angles possibles
2. Évaluez chaque critère avec précision et justification
3. Examinez les hypothèses sous-jacentes de la solution
4. Identifiez les risques potentiels non mentionnés
5. Suggérez des modifications spécifiques pour améliorer la solution
6. Attribuez un score global justifié

Format de réponse:
-----------------
* RÉSUMÉ EXÉCUTIF DE L'ÉVALUATION
* ANALYSE DÉTAILLÉE PAR CRITÈRE (pour chacun des 10 critères)
* ANALYSE DES HYPOTHÈSES ET PRÉMISSES
* IDENTIFICATION DES RISQUES
* RECOMMANDATIONS SPÉCIFIQUES
* COMPARAISON AVEC LES MEILLEURES PRATIQUES DU DOMAINE
* CONCLUSION ET SCORE FINAL
* SCORE: [total]/100

Votre évaluation approfondie:
"""


def get_evaluation_prompt_rapid():
    """
    Retourne le prompt pour l'évaluation rapide des solutions

    Returns:
        str: Template de prompt
    """
    return """
ÉVALUATION RAPIDE DE SOLUTION DE BRAINSTORMING

CONTEXTE DU PROBLÈME:
{context}

SOLUTION À ÉVALUER (proposée par {platform}):
{solution}

Votre mission:
-------------
Réalisez une évaluation concise mais percutante de cette solution en vous concentrant
sur les aspects les plus importants.

Critères d'évaluation simplifiés:
1. Valeur (30 points) - La solution répond-elle efficacement au problème?
2. Innovation (30 points) - La solution apporte-t-elle des idées nouvelles?
3. Faisabilité (40 points) - La solution est-elle réalisable et pratique?

Instructions:
1. Identifiez rapidement les points essentiels de la solution
2. Évaluez directement chaque critère principal
3. Mettez en évidence une force majeure et une faiblesse critique
4. Proposez une amélioration clé
5. Attribuez un score global

Format de réponse:
-----------------
* ÉVALUATION EN BREF
* VALEUR: [analyse concise] - [X/30]
* INNOVATION: [analyse concise] - [X/30]
* FAISABILITÉ: [analyse concise] - [X/40]
* FORCE PRINCIPALE
* FAIBLESSE CRITIQUE
* RECOMMANDATION CLÉ
* SCORE: [total]/100

Votre évaluation concise:
"""