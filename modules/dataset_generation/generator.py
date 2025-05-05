import json
import csv
import threading
import time
from datetime import datetime
from utils.logger import logger
from utils.exceptions import DatabaseError, AIAutomationError
from .templates import get_generation_prompt


class DatasetGenerator:
    """
    Classe pour générer des datasets avec l'aide de l'IA
    """

    def __init__(self, conductor, database=None):
        """
        Initialise le générateur de dataset

        Args:
            conductor: Chef d'orchestre pour exécuter les opérations
            database (Database, optional): Connexion à la base de données
        """
        logger.info("Initialisation du générateur de dataset")

        self.conductor = conductor
        self.database = database

        # Registre des générations en cours
        self.active_generations = {}

        # Verrou pour l'accès concurrent
        self.lock = threading.RLock()

    def generate_dataset(self, generation_config, platform=None, sync=True, timeout=300):
        """
        Génère un dataset selon la configuration fournie

        Args:
            generation_config (dict): Configuration de la génération
            platform (str, optional): Plateforme IA à utiliser
            sync (bool): Mode synchrone
            timeout (float, optional): Délai maximum d'attente en mode synchrone

        Returns:
            dict/str: Résultats de la génération ou ID de la génération (async)
        """
        try:
            # Choisir une plateforme disponible
            if platform is None:
                available = self.conductor.get_available_platforms()
                if not available:
                    raise AIAutomationError("Aucune plateforme disponible")
                platform = available[0]

            # Créer l'ID de génération
            generation_id = f"generation_{int(time.time())}"

            # Initialiser la génération
            generation = {
                'id': generation_id,
                'config': generation_config,
                'platform': platform,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'results': [],
                'progress': 0
            }

            # Enregistrer la génération
            with self.lock:
                self.active_generations[generation_id] = generation

            # Mode synchrone : exécuter et attendre
            if sync:
                return self._execute_generation(generation, timeout)

            # Mode asynchrone : démarrer un thread
            thread = threading.Thread(
                target=self._execute_generation,
                args=(generation, None)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"Génération {generation_id} démarrée en mode asynchrone sur {platform}")
            return generation_id

        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset: {str(e)}")
            raise AIAutomationError(f"Échec de la génération: {str(e)}")

    def _execute_generation(self, generation, timeout=None):
        """
        Exécute la génération du dataset

        Args:
            generation (dict): Informations sur la génération
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultats de la génération
        """
        generation_id = generation['id']
        platform = generation['platform']
        config = generation['config']

        try:
            # Mettre à jour le statut
            generation['status'] = 'running'

            # Préparer le prompt
            prompt_template = get_generation_prompt(config.get('format', 'csv'))

            # Prompt basique
            prompt = prompt_template.format(
                description=config.get('description', ''),
                count=config.get('count', 10),
                schema=config.get('schema', ''),
                instructions=config.get('instructions', '')
            )

            # Envoyer le prompt
            response = self.conductor.send_prompt(
                platform, prompt, mode="standard", sync=True, timeout=timeout
            )

            # Analyser la réponse
            if response and 'result' in response:
                raw_data = response['result'].get('response', '')

                # Parser les résultats selon le format
                parsed_data = self._parse_generation_result(raw_data, config.get('format', 'csv'))

                generation['results'] = parsed_data
                generation['status'] = 'completed'
                generation['end_time'] = datetime.now().isoformat()
                generation['progress'] = 100

                # Enregistrer dans la base de données si disponible
                if self.database:
                    self._save_dataset_to_db(generation)

                logger.info(f"Génération {generation_id} terminée avec succès")
                return generation
            else:
                raise AIAutomationError("Pas de résultat valide reçu")

        except Exception as e:
            # Marquer comme échouée
            generation['status'] = 'failed'
            generation['error'] = str(e)
            generation['end_time'] = datetime.now().isoformat()

            logger.error(f"Échec de la génération {generation_id}: {str(e)}")
            return generation

    def _parse_generation_result(self, raw_data, format):
        """
        Parse les résultats de génération selon le format

        Args:
            raw_data (str): Données brutes
            format (str): Format des données

        Returns:
            list: Données parsées
        """
        try:
            if format == 'json':
                # Nettoyer le JSON
                cleaned_data = raw_data.strip()
                if cleaned_data.startswith('```json'):
                    cleaned_data = cleaned_data[7:]
                if cleaned_data.endswith('```'):
                    cleaned_data = cleaned_data[:-3]

                return json.loads(cleaned_data)

            elif format == 'csv':
                # Parser le CSV
                lines = raw_data.strip().split('\n')
                reader = csv.reader(lines)
                return list(reader)

            else:
                # Format non reconnu, retourner en liste
                return raw_data.strip().split('\n')

        except Exception as e:
            logger.error(f"Erreur lors du parsing des résultats: {str(e)}")
            return []

    def _save_dataset_to_db(self, generation):
        """
        Sauvegarde le dataset généré dans la base de données

        Args:
            generation (dict): Données de génération
        """
        try:
            config = generation['config']
            results = generation['results']

            # Sauvegarder le dataset
            dataset_id = self.database.record_dataset(
                name=config.get('name', f"Dataset {generation['id']}"),
                dataset_type=config.get('type', 'generated'),
                format=config.get('format', 'csv'),
                item_count=len(results),
                filepath=f"generated_{generation['id']}.{config.get('format', 'csv')}"
            )

            # Mettre à jour la génération avec l'ID du dataset
            generation['dataset_id'] = dataset_id

            logger.debug(f"Dataset {dataset_id} enregistré en base de données")

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde en DB: {str(e)}")

    def get_generation_status(self, generation_id):
        """
        Récupère le statut d'une génération

        Args:
            generation_id (str): ID de la génération

        Returns:
            dict: Statut de la génération
        """
        with self.lock:
            generation = self.active_generations.get(generation_id)

            if not generation:
                raise AIAutomationError(f"Génération {generation_id} non trouvée")

            return {
                'id': generation['id'],
                'status': generation['status'],
                'progress': generation.get('progress', 0),
                'start_time': generation['start_time'],
                'end_time': generation.get('end_time'),
                'error': generation.get('error')
            }

    def get_generation_results(self, generation_id):
        """
        Récupère les résultats d'une génération

        Args:
            generation_id (str): ID de la génération

        Returns:
            dict: Résultats complets de la génération
        """
        with self.lock:
            generation = self.active_generations.get(generation_id)

            if not generation:
                raise AIAutomationError(f"Génération {generation_id} non trouvée")

            # Vérifier si la génération est terminée
            if generation['status'] not in ['completed', 'failed']:
                raise AIAutomationError(f"Génération {generation_id} en cours: {generation['status']}")

            return dict(generation)

    def export_results(self, generation_id, output_path=None, format=None):
        """
        Exporte les résultats d'une génération

        Args:
            generation_id (str): ID de la génération
            output_path (str, optional): Chemin de sortie
            format (str, optional): Format d'exportation

        Returns:
            str: Chemin du fichier exporté
        """
        try:
            # Récupérer les résultats
            generation = self.get_generation_results(generation_id)

            # Déterminer le format
            if format is None:
                format = generation['config'].get('format', 'csv')

            # Préparer le nom de fichier
            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"dataset_{generation_id}_{timestamp}.{format}"

            # Exporter
            results = generation['results']

            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)

            elif format == 'csv':
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    for row in results:
                        writer.writerow(row)

            else:
                # Exporter en texte brut
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(str(item) for item in results))

            logger.info(f"Résultats de génération exportés: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des résultats: {str(e)}")
            raise AIAutomationError(f"Échec de l'exportation: {str(e)}")