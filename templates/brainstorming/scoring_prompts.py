def get_scoring_prompt():
    """
    Retourne le template de prompt pour la phase de scoring final
    """
    return """Vous êtes le juge en chef d'un concours de brainstorming. Votre mission est de déterminer le score final.

CONTEXTE:
{context}

SOLUTION DE {platform}:
{solution}

ÉVALUATIONS REÇUES:
{evaluations}

INSTRUCTIONS:
1. Analysez les évaluations reçues
2. Pondérez les différents critères
3. Attribuez un score final sur 100

Format attendu:
ANALYSE DES ÉVALUATIONS:
[Synthèse des points communs et divergences]

SCORE FINAL: [X]/100

JUSTIFICATION:
[Explication du score attribué en tenant compte des évaluations]

MENTION SPÉCIALE:
[Ce qui distingue cette solution]

Le score doit être un nombre entre 0 et 100 qui reflète la qualité globale de la solution."""