def get_csv_generation_prompt():
    """
    Retourne le template de prompt pour la génération de CSV
    """
    return """Générez un dataset CSV selon les spécifications suivantes:

DESCRIPTION DU DATASET:
{description}

NOMBRE DE LIGNES: {rows}

COLONNES REQUISES:
{columns}

CONTRAINTES:
{constraints}

EXEMPLE (première ligne seulement):
{example}

Fournissez UNIQUEMENT le contenu CSV (en-têtes + données), sans texte explicatif.

CSV:"""


def get_customer_data_prompt():
    """
    Retourne le template de prompt pour générer des données clients
    """
    return """Générez un dataset CSV de données clients fictives.

COLONNES:
- customer_id: ID unique
- first_name: Prénom
- last_name: Nom de famille
- email: Email valide
- phone: Numéro de téléphone
- city: Ville
- signup_date: Date d'inscription
- purchase_count: Nombre d'achats
- total_spent: Montant total dépensé

NOMBRE DE CLIENTS: {count}

INSTRUCTIONS:
- Données réalistes mais fictives
- Emails valides (mais inventés)
- Dates dans les 2 dernières années
- Montants entre 0 et 5000€

CSV:"""


def get_product_catalog_prompt():
    """
    Retourne le template de prompt pour générer un catalogue produits
    """
    return """Générez un catalogue produits au format CSV.

COLONNES:
- product_id: ID produit
- name: Nom du produit
- description: Description courte
- category: Catégorie
- price: Prix en euros
- stock: Quantité en stock
- brand: Marque
- rating: Note (1-5)

NOMBRE DE PRODUITS: {count}

CATÉGORIES: {categories}

CSV:"""