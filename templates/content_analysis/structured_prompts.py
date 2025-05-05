def get_analysis_prompt(structure_type="json"):
    """
    Retourne le template de prompt pour l'analyse de contenu structuré
    """
    return """Analysez le contenu structuré suivant:

TYPE DE STRUCTURE: {structure_type}

CONTENU:
{content}

SPÉCIFICATIONS D'ANALYSE:
{spec}

INSTRUCTIONS:
1. Analysez la structure du contenu
2. Identifiez les patterns et anomalies
3. Extrayez les informations clés
4. Fournissez un résumé des insights

Format de réponse attendu:

STRUCTURE DÉTECTÉE:
[Description de la structure]

ÉLÉMENTS CLÉS:
- [Élément 1]
- [Élément 2]
- [...]

ANOMALIES:
- [Anomalie 1]
- [Anomalie 2]
- [...]

RÉSUMÉ:
[Résumé des insights principaux]

RECOMMANDATIONS:
- [Recommandation 1]
- [Recommandation 2]
- [...]"""