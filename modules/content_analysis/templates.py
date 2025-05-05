"""
Templates pour les opérations d'analyse de contenu
"""

# Templates pour l'analyse de texte
TEXT_SUMMARY_TEMPLATE = """
ANALYSE DE CONTENU: RÉSUMÉ

Le texte suivant doit être analysé et résumé:
--------------------------------------------------------------------
{content}
--------------------------------------------------------------------

Instructions:
1. Créez un résumé concis qui capture les points essentiels du texte
2. Identifiez les idées principales et les thèmes clés
3. Préservez la cohérence et le ton du texte original
4. Réduisez le contenu à environ 1/4 de sa longueur originale
5. Assurez-vous que le résumé est autonome et compréhensible

Format du résumé:
* SYNTHÈSE GÉNÉRALE (1-2 phrases)
* POINTS PRINCIPAUX (liste des idées essentielles)
* RÉSUMÉ DÉTAILLÉ (paragraphes cohérents)
* CONCLUSION

Votre résumé complet:
"""

TEXT_KEYWORDS_TEMPLATE = """
ANALYSE DE CONTENU: EXTRACTION DE MOTS-CLÉS

Le texte suivant doit être analysé pour en extraire les mots-clés et concepts importants:
--------------------------------------------------------------------
{content}
--------------------------------------------------------------------

Instructions:
1. Identifiez les mots-clés, termes techniques et concepts centraux
2. Classez-les par importance et pertinence
3. Groupez les termes connexes en catégories thématiques
4. Incluez les définitions pour les termes techniques ou spécialisés
5. Précisez la fréquence ou l'importance relative dans le texte

Format de réponse:
* MOTS-CLÉS PRINCIPAUX (liste des 5-10 termes les plus importants)
* CATÉGORIES THÉMATIQUES
  - [Thème 1]: liste des termes associés
  - [Thème 2]: liste des termes associés
  ...
* LEXIQUE TECHNIQUE (définitions des termes spécialisés)
* ANALYSE DE FRÉQUENCE (termes les plus récurrents)

Votre extraction de mots-clés:
"""

TEXT_SENTIMENT_TEMPLATE = """
ANALYSE DE CONTENU: ANALYSE DE SENTIMENT

Le texte suivant doit être analysé pour déterminer le sentiment global et les émotions exprimées:
--------------------------------------------------------------------
{content}
--------------------------------------------------------------------

Instructions:
1. Déterminez le sentiment global du texte (positif, négatif, neutre, mixte)
2. Identifiez les émotions spécifiques exprimées ou évoquées
3. Repérez les passages clés qui reflètent ces sentiments
4. Analysez l'évolution du ton émotionnel à travers le texte
5. Évaluez l'intensité des sentiments et émotions identifiés

Format de réponse:
* SYNTHÈSE DU SENTIMENT (score global et brève description)
* PALETTE ÉMOTIONNELLE (émotions identifiées et leur importance relative)
* PASSAGES SIGNIFICATIFS (citations illustrant les sentiments dominants)
* ÉVOLUTION DU TON (comment le sentiment change au fil du texte)
* INTENSITÉ ÉMOTIONNELLE (évaluation de la force des émotions exprimées)

Votre analyse de sentiment:
"""

# Templates pour l'analyse de contenu structuré
JSON_ANALYSIS_TEMPLATE = """
ANALYSE DE DONNÉES JSON

Les données JSON suivantes doivent être analysées:
--------------------------------------------------------------------
{content}
--------------------------------------------------------------------

Spécifications d'analyse:
{spec}

Instructions:
1. Analysez la structure générale des données JSON
2. Identifiez les entités, relations et attributs principaux
3. Extrayez les informations clés selon les spécifications
4. Recherchez des motifs, anomalies ou incohérences
5. Présentez les résultats de manière structurée et informative

Format de réponse:
* APERÇU DE LA STRUCTURE (description de l'organisation des données)
* ENTITÉS PRINCIPALES (objets ou collections clés)
* ANALYSE SELON SPÉCIFICATIONS
* INSIGHTS ET OBSERVATIONS
* SYNTHÈSE FINALE

Votre analyse complète:
"""

XML_ANALYSIS_TEMPLATE = """
ANALYSE DE DONNÉES XML

Les données XML suivantes doivent être analysées:
--------------------------------------------------------------------
{content}
--------------------------------------------------------------------

Spécifications d'analyse:
{spec}

Instructions:
1. Analysez la structure générale du document XML
2. Identifiez les éléments, attributs et namespaces principaux
3. Extrayez les informations clés selon les spécifications
4. Examinez les relations hiérarchiques entre les éléments
5. Présentez les résultats de manière structurée et informative

Format de réponse:
* APERÇU DU SCHÉMA (description de l'organisation du document)
* ÉLÉMENTS PRINCIPAUX (nœuds et structures clés)
* ANALYSE SELON SPÉCIFICATIONS
* RELATIONS HIÉRARCHIQUES
* SYNTHÈSE FINALE

Votre analyse complète:
"""

CSV_ANALYSIS_TEMPLATE = """
ANALYSE DE DONNÉES CSV

Les données CSV suivantes doivent être analysées:
--------------------------------------------------------------------
{content}
--------------------------------------------------------------------

Spécifications d'analyse:
{spec}

Instructions:
1. Analysez les en-têtes et la structure des colonnes
2. Identifiez les types de données pour chaque colonne
3. Effectuez une analyse statistique descriptive des données numériques
4. Recherchez des tendances, corrélations ou anomalies
5. Présentez les résultats de manière structurée et informative

Format de réponse:
* APERÇU DE LA STRUCTURE (colonnes et types de données)
* STATISTIQUES DESCRIPTIVES (pour les colonnes numériques)
* DISTRIBUTION DES VALEURS (pour les colonnes catégorielles)
* ANALYSE SELON SPÉCIFICATIONS
* OBSERVATIONS ET INSIGHTS
* SYNTHÈSE FINALE

Votre analyse complète:
"""


# Fonctions d'accès aux templates

def get_summary_prompt(analysis_type="summary"):
    """
    Retourne le template pour l'analyse de texte selon le type

    Args:
        analysis_type (str): Type d'analyse ("summary", "keywords", "sentiment")

    Returns:
        str: Template de prompt
    """
    if analysis_type == "keywords":
        return TEXT_KEYWORDS_TEMPLATE
    elif analysis_type == "sentiment":
        return TEXT_SENTIMENT_TEMPLATE
    else:  # default to summary
        return TEXT_SUMMARY_TEMPLATE


def get_analysis_prompt(structure_type="json"):
    """
    Retourne le template pour l'analyse de contenu structuré selon le type

    Args:
        structure_type (str): Type de structure ("json", "xml", "csv")

    Returns:
        str: Template de prompt
    """
    if structure_type == "xml":
        return XML_ANALYSIS_TEMPLATE
    elif structure_type == "csv":
        return CSV_ANALYSIS_TEMPLATE
    else:  # default to json
        return JSON_ANALYSIS_TEMPLATE