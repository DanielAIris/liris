def get_annotation_prompt(annotation_type="classification"):
    """
    Retourne le template de prompt pour l'annotation de données
    """
    templates = {
        "classification": """Classifiez l'élément suivant selon les instructions données:

ÉLÉMENT À ANNOTER:
{item}

INSTRUCTIONS:
{instructions}

Veuillez fournir uniquement la catégorie assignée, sans explication supplémentaire.""",

        "sentiment": """Analysez le sentiment de l'élément suivant:

ÉLÉMENT À ANNOTER:
{item}

INSTRUCTIONS:
{instructions}

Fournissez le sentiment en un seul mot: positif, négatif, ou neutre.""",

        "entity_extraction": """Extrayez les entités nommées de l'élément suivant:

ÉLÉMENT À ANNOTER:
{item}

INSTRUCTIONS:
{instructions}

SCHÉMA D'ENTITÉS:
{schema}

Fournissez les entités au format JSON uniquement, sans texte supplémentaire.""",

        "structured": """Annotez l'élément suivant selon le schéma fourni:

ÉLÉMENT À ANNOTER:
{item}

INSTRUCTIONS:
{instructions}

SCHÉMA:
{schema}

Fournissez l'annotation complète au format JSON.""",

        "custom": """Effectuez l'annotation selon les instructions suivantes:

ÉLÉMENT À ANNOTER:
{item}

INSTRUCTIONS DÉTAILLÉES:
{instructions}

Répondez selon le format demandé dans les instructions."""
    }

    return templates.get(annotation_type, templates["custom"])