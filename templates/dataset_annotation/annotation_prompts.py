def get_annotation_prompt():
    """
    Retourne le template de prompt pour l'annotation de données
    """
    return """Annotez l'élément suivant selon les instructions données:

ÉLÉMENT À ANNOTER:
{content}

INSTRUCTIONS:
{instructions}

CONTEXTE:
{context}

FORMAT ATTENDU:
{format}

Fournissez l'annotation selon le format spécifié, sans explication supplémentaire."""


def get_classification_prompt():
    """
    Retourne le template de prompt pour la classification
    """
    return """Classifiez l'élément suivant dans l'une des catégories spécifiées:

ÉLÉMENT:
{content}

CATÉGORIES DISPONIBLES:
{categories}

INSTRUCTIONS:
{instructions}

Répondez UNIQUEMENT avec le nom de la catégorie, sans explication."""


def get_sentiment_analysis_prompt():
    """
    Retourne le template de prompt pour l'analyse de sentiment
    """
    return """Analysez le sentiment de l'élément suivant:

TEXTE:
{content}

ÉCHELLE DE SENTIMENT:
{scale}

Répondez UNIQUEMENT avec le niveau de sentiment (ex: positif, négatif, neutre)."""


def get_entity_extraction_prompt():
    """
    Retourne le template de prompt pour l'extraction d'entités
    """
    return """Extrayez les entités nommées de l'élément suivant:

TEXTE:
{content}

TYPES D'ENTITÉS À EXTRAIRE:
{entity_types}

INSTRUCTIONS:
{instructions}

Fournissez les entités au format JSON:
{
    "entités": [
        {"texte": "...", "type": "...", "position": [...]}
    ]
}"""