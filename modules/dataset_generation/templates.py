def get_generation_prompt(format="csv"):
    """
    Retourne le template de prompt pour la génération de datasets
    """
    if format == "csv":
        return """Générez un dataset CSV selon les spécifications suivantes:

DESCRIPTION:
{description}

NOMBRE D'ENTRÉES: {count}

SCHÉMA:
{schema}

INSTRUCTIONS SUPPLÉMENTAIRES:
{instructions}

Fournissez UNIQUEMENT le contenu CSV, rien d'autre. Pas de texte explicatif avant ou après.
Format: Header dans la première ligne, puis les données.

CSV:"""

    elif format == "json":
        return """Générez un dataset JSON selon les spécifications suivantes:

DESCRIPTION:
{description}

NOMBRE D'ENTRÉES: {count}

SCHÉMA:
{schema}

INSTRUCTIONS SUPPLÉMENTAIRES:
{instructions}

Fournissez UNIQUEMENT le JSON valide, sans texte explicatif.
Format: Array d'objets JSON.

```json"""

    elif format == "structured":
        return """Générez un dataset structuré selon les spécifications suivantes:

DESCRIPTION:
{description}

NOMBRE D'ENTRÉES: {count}

SCHÉMA:
{schema}

INSTRUCTIONS SUPPLÉMENTAIRES:
{instructions}

Respectez strictement le schéma fourni.

DATASET:"""

    else:
        return """Générez un dataset selon les spécifications suivantes:

DESCRIPTION:
{description}

NOMBRE D'ENTRÉES: {count}

SCHÉMA:
{schema}

INSTRUCTIONS SUPPLÉMENTAIRES:
{instructions}

Fournissez les données dans le format demandé, sans texte supplémentaire.

DATASET:"""