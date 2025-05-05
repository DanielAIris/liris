import json
import csv
import threading
import time
from datetime import datetime
from utils.logger import logger
from utils.exceptions import DatabaseError, AIAutomationError
from .templates import get_annotation_prompt


class DatasetAnnotator:
    """
    Classe pour l'annotation de datasets avec l'aide de l'IA
    """

    def __init__(self, conductor, database=None):
        """
        Initialise l'annotateur de dataset

        Args:
            conductor: Chef d'orchestre pour exécuter les opérations
            database (Database, optional): Connexion à la base de données
        """
        logger.info("Initialisation de l'annotateur de dataset")

        self.conductor = conductor
        self.database = database

        # Registre des annotations en cours
        self.active_annotations = {}

        # Verrou pour l'accès concurrent
        self.lock = threading.RLock()

    def annotate_dataset(self, dataset_path, annotation_config, platform=None, sync=True, timeout=300):
        """
        Annote un dataset complet

        Args:
            dataset_path (str): Chemin vers le dataset
            annotation_config (dict): Configuration de l'annotation
            platform (str, optional): Plateforme IA à utiliser
            sync (bool): Mode synchrone
            timeout (float, optional): Délai maximum d'attente en mode synchrone

        Returns:
            dict/str: Résultats d'annotation ou ID de l'annotation (async)
        """
        try:
            # Choisir une plateforme disponible
            if platform is None:
                available = self.conductor.get_available_platforms()
                if not available:
                    raise AIAutomationError("Aucune plateforme disponible")
                platform = available[0]

            # Créer l'ID d'annotation
            annotation_id = f"annotation_{int(time.time())}"

            # Charger le dataset
            dataset = self._load_dataset(dataset_path)

            # Initialiser l'annotation
            annotation = {
                'id': annotation_id,
                'dataset_path': dataset_path,
                'platform': platform,
                'config': annotation_config,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'results': [],
                'progress': 0
            }

            # Enregistrer l'annotation
            with self.lock:
                self.active_annotations[annotation_id] = annotation

            # Mode synchrone : exécuter et attendre
            if sync:
                return self._execute_annotation(annotation, dataset, timeout)

            # Mode asynchrone : démarrer un thread
            thread = threading.Thread(
                target=self._execute_annotation,
                args=(annotation, dataset, None)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"Annotation {annotation_id} démarrée en mode asynchrone sur {platform}")
            return annotation_id

        except Exception as e:
            logger.error(f"Erreur lors de l'annotation du dataset: {str(e)}")
            raise AIAutomationError(f"Échec de l'annotation: {str(e)}")

    def _load_dataset(self, dataset_path):
        """
        Charge un dataset depuis un fichier

        Args:
            dataset_path (str): Chemin vers le dataset

        Returns:
            list: Dataset chargé
        """
        try:
            if dataset_path.endswith('.csv'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    return list(reader)
            elif dataset_path.endswith('.json'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise AIAutomationError(f"Format de dataset non supporté: {dataset_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du dataset: {str(e)}")
            raise AIAutomationError(f"Échec du chargement: {str(e)}")

    def _execute_annotation(self, annotation, dataset, timeout=None):
        """
        Exécute l'annotation du dataset

        Args:
            annotation (dict): Informations sur l'annotation
            dataset (list): Dataset à annoter
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultats de l'annotation
        """
        annotation_id = annotation['id']
        platform = annotation['platform']
        config = annotation['config']

        try:
            # Mettre à jour le statut
            annotation['status'] = 'running'

            # Préparer le prompt
            prompt_template = get_annotation_prompt(config.get('type', 'classification'))

            results = []
            total_items = len(dataset)

            for i, item in enumerate(dataset):
                # Vérifier l'interruption
                if timeout is not None and time.time() - float(annotation['start_time']) > timeout:
                    raise AIAutomationError("Timeout atteint")

                # Préparer le prompt pour cet élément
                prompt = prompt_template.format(
                    item=str(item),
                    instructions=config.get('instructions', ''),
                    schema=config.get('schema', {})
                )

                # Envoyer le prompt
                response = self.conductor.send_prompt(
                    platform, prompt, mode="standard", sync=True, timeout=30
                )

                # Analyser la réponse
                if response and 'result' in response:
                    result = {
                        'item_index': i,
                        'original': item,
                        'annotation': response['result'].get('response', ''),
                        'status': 'completed'
                    }
                else:
                    raise AIAutomationError("Pas de résultat valide reçu")

                results.append(result)

                # Mettre à jour la progression
                annotation['progress'] = int((i + 1) / total_items * 100)
                annotation['results'] = results

                logger.debug(f"Annotation {annotation_id}: {i+1}/{total_items} complété")

            # Marquer comme terminée
            annotation['status'] = 'completed'
            annotation['end_time'] = datetime.now().isoformat()

            logger.info(f"Annotation {annotation_id} terminée avec succès")
            return annotation

        except Exception as e:
            # Marquer comme échouée
            annotation['status'] = 'failed'
            annotation['error'] = str(e)
            annotation['end_time'] = datetime.now().isoformat()

            logger.error(f"Échec de l'annotation {annotation_id}: {str(e)}")
            return annotation

    def get_annotation_status(self, annotation_id):
        """
        Récupère le statut d'une annotation

        Args:
            annotation_id (str): ID de l'annotation

        Returns:
            dict: Statut de l'annotation
        """
        with self.lock:
            annotation = self.active_annotations.get(annotation_id)

            if not annotation:
                raise AIAutomationError(f"Annotation {annotation_id} non trouvée")

            return {
                'id': annotation['id'],
                'status': annotation['status'],
                'progress': annotation.get('progress', 0),
                'start_time': annotation['start_time'],
                'end_time': annotation.get('end_time'),
                'error': annotation.get('error')
            }

    def get_annotation_results(self, annotation_id):
        """
        Récupère les résultats d'une annotation

        Args:
            annotation_id (str): ID de l'annotation

        Returns:
            dict: Résultats complets de l'annotation
        """
        with self.lock:
            annotation = self.active_annotations.get(annotation_id)

            if not annotation:
                raise AIAutomationError(f"Annotation {annotation_id} non trouvée")

            # Vérifier si l'annotation est terminée
            if annotation['status'] not in ['completed', 'failed']:
                raise AIAutomationError(f"Annotation {annotation_id} en cours: {annotation['status']}")

            return dict(annotation)

    def export_results(self, annotation_id, output_path=None, format='json'):
        """
        Exporte les résultats d'une annotation

        Args:
            annotation_id (str): ID de l'annotation
            output_path (str, optional): Chemin de sortie
            format (str): Format d'exportation

        Returns:
            str: Chemin du fichier exporté
        """
        try:
            # Récupérer les résultats
            annotation = self.get_annotation_results(annotation_id)

            # Préparer le nom de fichier
            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                if format == 'json':
                    output_path = f"annotation_{annotation_id}_{timestamp}.json"
                elif format == 'csv':
                    output_path = f"annotation_{annotation_id}_{timestamp}.csv"
                else:
                    raise AIAutomationError(f"Format non supporté: {format}")

            # Exporter
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(annotation, f, indent=2, ensure_ascii=False)
            elif format == 'csv':
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['item_index', 'original', 'annotation', 'status'])

                    for result in annotation['results']:
                        writer.writerow([
                            result['item_index'],
                            json.dumps(result['original']),
                            result['annotation'],
                            result['status']
                        ])

            logger.info(f"Résultats d'annotation exportés: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des résultats: {str(e)}")
            raise AIAutomationError(f"Échec de l'exportation: {str(e)}")