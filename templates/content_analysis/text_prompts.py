def get_summary_prompt(analysis_type="summary"):
    """
    Retourne le template de prompt pour l'analyse de texte
    """
    if analysis_type == "summary":
        return """Analysez et résumez le texte suivant:

{content}

Fournissez:
1. Un résumé en 2-3 phrases
2. Les points clés
3. Le ton/style du texte

RÉSUMÉ:
[Résumé concis]

POINTS CLÉS:
- [Point 1]
- [Point 2]
- [Point 3]

TON:
[Description du ton]"""

    elif analysis_type == "keywords":
        return """Extrayez les mots-clés et concepts importants du texte suivant:

{content}

Fournissez:
1. 5-10 mots-clés principaux
2. 3-5 concepts clés

MOTS-CLÉS:
- [Mot-clé 1]
- [Mot-clé 2]
- [...]

CONCEPTS:
- [Concept 1]
- [Concept 2]
- [...]"""

    elif analysis_type == "sentiment":
        return """Analysez le sentiment du texte suivant:

{content}

Déterminez:
1. Le sentiment global (positif, négatif, neutre)
2. L'intensité (faible, modérée, forte)
3. Les émotions détectées

SENTIMENT GLOBAL:
[Positif/Négatif/Neutre]

INTENSITÉ:
[Faible/Modérée/Forte]

ÉMOTIONS DÉTECTÉES:
- [Émotion 1]
- [Émotion 2]
- [...]

JUSTIFICATION:
[Explication du sentiment]"""

    else:
        return get_summary_prompt("summary")