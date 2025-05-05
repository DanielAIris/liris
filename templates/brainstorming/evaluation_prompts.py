def get_evaluation_prompt():
    """
    Retourne le template de prompt pour la phase d'évaluation
    """
    return """Vous êtes un évaluateur expert participant à un concours de brainstorming.

CONTEXTE DU PROBLÈME:
{context}

SOLUTION À ÉVALUER (proposée par {platform}):
{solution}

CRITÈRES D'ÉVALUATION:
1. ORIGINALITÉ (sur 25 points)
   - Nouveauté de l'approche
   - Pensée créative

2. FAISABILITÉ (sur 25 points)
   - Réalisme de la mise en œuvre
   - Ressources nécessaires

3. EFFICACITÉ (sur 25 points)
   - Résolution du problème
   - Impact potentiel

4. CLARTÉ (sur 25 points)
   - Présentation claire
   - Justification convaincante

Format attendu:
ÉVALUATION:

ORIGINALITÉ: [X/25]
Commentaire: [Justification]

FAISABILITÉ: [X/25]
Commentaire: [Justification]

EFFICACITÉ: [X/25]
Commentaire: [Justification]

CLARTÉ: [X/25]
Commentaire: [Justification]

TOTAL: [X/100]

POINTS FORTS:
- [...]
- [...]

POINTS D'AMÉLIORATION:
- [...]
- [...]

Fournissez une évaluation objective et constructive."""