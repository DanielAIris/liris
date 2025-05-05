def get_json_generation_prompt():
    """
    Retourne le template de prompt pour la génération de JSON
    """
    return """Générez un dataset JSON selon les spécifications suivantes:

DESCRIPTION DU DATASET:
{description}

NOMBRE D'ENTRÉES: {count}

SCHÉMA JSON:
{schema}

CONTRAINTES:
{constraints}

EXEMPLE (un seul objet):
{example}

Fournissez UNIQUEMENT le JSON valide (array d'objets), sans texte explicatif.

```json"""


def get_user_profile_prompt():
    """
    Retourne le template de prompt pour générer des profils utilisateurs
    """
    return """Générez un dataset JSON de profils utilisateurs fictifs.

SCHÉMA:
{
    "user_id": "identifiant unique",
    "personal_info": {
        "name": "nom complet",
        "age": "nombre entre 18 et 80",
        "email": "email valide fictif",
        "location": "ville, pays"
    },
    "preferences": {
        "language": "langue principale",
        "interests": ["liste d'intérêts"],
        "newsletter": "boolean"
    },
    "activity": {
        "join_date": "date d'inscription",
        "last_login": "dernière connexion",
        "posts_count": "nombre de posts",
        "followers": "nombre de followers"
    }
}

NOMBRE D'UTILISATEURS: {count}

INSTRUCTIONS:
- Données réalistes mais fictives
- 3-5 intérêts par utilisateur
- Dates cohérentes (join_date < last_login)
- Followers entre 0 et 10000

```json"""


def get_event_data_prompt():
    """
    Retourne le template de prompt pour générer des données d'événements
    """
    return """Générez un dataset JSON d'événements fictifs.

SCHÉMA:
{
    "event_id": "identifiant unique",
    "title": "titre de l'événement",
    "description": "description détaillée",
    "type": "conférence|atelier|séminaire|réunion",
    "datetime": {
        "start": "ISO datetime",
        "end": "ISO datetime"
    },
    "location": {
        "venue": "nom du lieu",
        "address": "adresse complète",
        "capacity": "nombre de places"
    },
    "organizer": {
        "name": "nom de l'organisateur",
        "contact": "email ou téléphone"
    },
    "status": "à venir|en cours|terminé",
    "attendees_count": "nombre de participants",
    "tags": ["liste de tags"]
}

NOMBRE D'ÉVÉNEMENTS: {count}

TYPES D'ÉVÉNEMENTS: {event_types}

```json"""