import re
import json
import html
from utils.logger import logger
from utils.exceptions import DatabaseError


class ResponseParser:
    """
    Classe pour analyser et extraire des informations des réponses d'IA
    """

    def __init__(self):
        """
        Initialise le parseur de réponses
        """
        logger.info("Initialisation du parseur de réponses")

    def extract_text_content(self, response):
        """
        Extrait le contenu textuel d'une réponse HTML/markdown

        Args:
            response (str): Réponse brute à analyser

        Returns:
            str: Contenu textuel nettoyé
        """
        try:
            # Supprimer les balises HTML si présentes
            text = re.sub(r'<[^>]+>', ' ', response)

            # Décoder les entités HTML
            text = html.unescape(text)

            # Supprimer les formatages markdown
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Gras
            text = re.sub(r'\*(.*?)\*', r'\1', text)  # Italique
            text = re.sub(r'__(.*?)__', r'\1', text)  # Souligné
            text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Blocs de code

            # Nettoyer les espaces multiples et retours à la ligne
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()

            return text

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
            return response  # Retourner la réponse brute en cas d'erreur

    def extract_code_blocks(self, response):
        """
        Extrait les blocs de code d'une réponse markdown

        Args:
            response (str): Réponse markdown

        Returns:
            list: Liste des blocs de code avec leur langage
        """
        try:
            # Regex pour capturer les blocs de code avec leur langage
            code_pattern = r'```(\w*)\n(.*?)```'
            matches = re.findall(code_pattern, response, re.DOTALL)

            code_blocks = []
            for lang, code in matches:
                code_blocks.append({
                    'language': lang.strip() or 'text',
                    'code': code.strip()
                })

            return code_blocks

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des blocs de code: {str(e)}")
            return []

    def extract_json_data(self, response):
        """
        Extrait les données JSON d'une réponse

        Args:
            response (str): Réponse contenant du JSON

        Returns:
            dict/list: Données JSON extraites ou None si aucune
        """
        try:
            # Chercher des structures JSON dans la réponse
            json_pattern = r'```(?:json)?\s*(\{.*?\}|\[.*?\])```'
            matches = re.search(json_pattern, response, re.DOTALL)

            if matches:
                json_str = matches.group(1)
                return json.loads(json_str)

            # Si pas trouvé dans un bloc de code, chercher directement
            json_pattern = r'(\{.*\}|\[.*\])'
            matches = re.search(json_pattern, response, re.DOTALL)

            if matches:
                try:
                    json_str = matches.group(1)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            return None

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données JSON: {str(e)}")
            return None

    def extract_list_items(self, response):
        """
        Extrait les éléments de liste d'une réponse

        Args:
            response (str): Réponse à analyser

        Returns:
            list: Liste des éléments extraits
        """
        try:
            # Modèle pour les listes numérotées et à puces
            numbered_list = r'^\d+\.\s+(.*?)$'
            bullet_list = r'^[-*]\s+(.*?)$'

            # Extraire les lignes
            lines = response.split('\n')

            items = []
            for line in lines:
                line = line.strip()

                # Vérifier si c'est une liste numérotée
                num_match = re.match(numbered_list, line)
                if num_match:
                    items.append(num_match.group(1))
                    continue

                # Vérifier si c'est une liste à puces
                bullet_match = re.match(bullet_list, line)
                if bullet_match:
                    items.append(bullet_match.group(1))

            return items

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des listes: {str(e)}")
            return []

    def extract_dataset_items(self, response, format='auto'):
        """
        Extrait les éléments d'un dataset à partir d'une réponse

        Args:
            response (str): Réponse contenant des données structurées
            format (str): Format attendu ('json', 'csv', 'auto')

        Returns:
            list: Liste d'éléments extraits
        """
        try:
            if format == 'json' or format == 'auto':
                # Essayer d'extraire du JSON
                json_data = self.extract_json_data(response)
                if json_data:
                    # Convertir en liste si c'est un dictionnaire
                    if isinstance(json_data, dict):
                        return [json_data]
                    elif isinstance(json_data, list):
                        return json_data

            if format == 'csv' or format == 'auto':
                # Extraire des données CSV (simplifiée)
                lines = response.strip().split('\n')
                if len(lines) >= 2:
                    # Supposer que la première ligne est l'en-tête
                    headers = [h.strip() for h in lines[0].split(',')]

                    items = []
                    for line in lines[1:]:
                        if line.strip():
                            values = [v.strip() for v in line.split(',')]
                            if len(values) == len(headers):
                                items.append(dict(zip(headers, values)))

                    if items:
                        return items

            # Si aucun format structuré n'est détecté, extraire des listes
            list_items = self.extract_list_items(response)
            if list_items:
                return list_items

            # En dernier recours, retourner le texte en un seul élément
            return [self.extract_text_content(response)]

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des éléments de dataset: {str(e)}")
            return []

    def detect_error_patterns(self, response, error_patterns):
        """
        Détecte les patterns d'erreur dans une réponse

        Args:
            response (str): Réponse à analyser
            error_patterns (list): Liste des patterns d'erreur à rechercher

        Returns:
            tuple: (erreur_détectée, pattern_correspondant)
        """
        try:
            # Extraction du texte brut
            text = self.extract_text_content(response).lower()

            for pattern in error_patterns:
                if pattern.lower() in text:
                    logger.warning(f"Pattern d'erreur détecté: {pattern}")
                    return True, pattern

            return False, None

        except Exception as e:
            logger.error(f"Erreur lors de la détection des patterns: {str(e)}")
            return False, None