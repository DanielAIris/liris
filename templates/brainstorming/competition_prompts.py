def get_solution_prompt():
    """
    Retourne le template de prompt pour la phase de compétition
    """
    return """Tu participes à un concours de brainstorming créatif avec d'autres intelligences artificielles.

Votre mission est de proposer la solution la plus innovante et efficace au problème suivant:

{context}

CONSIGNES:
1. Soyez créatif et original dans votre approche
2. Pensez hors des sentiers battus
3. Votre solution doit être à la fois innovante et réalisable
4. Justifiez brièvement votre approche

Format attendu:
TITRE DE LA SOLUTION:
[Un titre accrocheur]

DESCRIPTION:
[Description détaillée de votre solution]

INNOVATION:
[Ce qui rend votre solution unique]

FAISABILITÉ:
[Comment mettre en œuvre cette solution]

Bonne chance dans la compétition!"""