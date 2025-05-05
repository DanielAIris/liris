import threading
import time
import queue
from datetime import datetime
from utils.logger import logger
from utils.exceptions import OrchestrationError, SchedulingError


class AIConductor:
    """
    Chef d'orchestre pour coordonner les interactions avec les IA
    """

    def __init__(self, config_provider, scheduler, database=None):
        """
        Initialise le chef d'orchestre

        Args:
            config_provider: Fournisseur de configuration
            scheduler: Planificateur d'IA
            database (Database, optional): Connexion à la base de données
        """
        self.config_provider = config_provider
        self.scheduler = scheduler
        self.database = database

        # Registre des tâches en cours
        self.active_tasks = {}
        self.task_counter = 0

        # File d'attente des tâches
        self.task_queue = queue.Queue()

        # Verrous pour l'accès concurrent
        self.lock = threading.RLock()

        # Flag d'arrêt
        self._shutdown = False

        # Worker thread
        self.worker_thread = None

        logger.info("Chef d'orchestre initialisé")

    def initialize(self):
        """Initialise le système"""
        try:
            # Démarrer le worker thread
            self.worker_thread = threading.Thread(target=self._worker_loop)
            self.worker_thread.daemon = True
            self.worker_thread.start()

            logger.info("Système d'orchestration initialisé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {str(e)}")
            raise OrchestrationError(f"Échec de l'initialisation: {str(e)}")

    def get_available_platforms(self):
        """
        Récupère les plateformes d'IA disponibles

        Returns:
            list: Noms des plateformes disponibles
        """
        try:
            profiles = self.config_provider.get_profiles()
            available = []

            for platform_name in profiles.keys():
                can_use, _ = self.scheduler.can_use_platform(platform_name)
                if can_use:
                    available.append(platform_name)

            logger.debug(f"Plateformes disponibles: {available}")
            return available
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des plateformes: {str(e)}")
            return []

    def send_prompt(self, platform, prompt, mode="standard", priority=0, sync=False, timeout=None):
        """
        Envoie un prompt à une plateforme d'IA

        Args:
            platform (str): Nom de la plateforme
            prompt (str): Texte du prompt
            mode (str): Mode d'opération (standard, brainstorm, analyze)
            priority (int): Priorité de la tâche
            sync (bool): Mode synchrone
            timeout (float, optional): Délai maximum d'attente en mode synchrone

        Returns:
            int/dict: ID de tâche (async) ou résultat (sync)
        """
        try:
            # Vérifier la disponibilité
            can_use, reason = self.scheduler.can_use_platform(platform)
            if not can_use:
                raise SchedulingError(reason)

            # Créer la tâche
            with self.lock:
                self.task_counter += 1
                task_id = self.task_counter

            task = {
                'id': task_id,
                'platform': platform,
                'prompt': prompt,
                'mode': mode,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'timeout': timeout
            }

            # Enregistrer la tâche
            with self.lock:
                self.active_tasks[task_id] = task

            # Mettre la tâche dans la file
            self.task_queue.put((priority, task_id))

            # Mode synchrone : attendre le résultat
            if sync:
                # Attendre la tâche (artificiellement car on n'a pas d'IA réelle)
                if timeout:
                    time.sleep(min(1, timeout))  # Simuler un traitement court
                else:
                    time.sleep(1)  # Délai par défaut

                # Simuler une réponse
                result = {
                    'id': task_id,
                    'status': 'completed',
                    'result': {
                        'response': "Ceci est une réponse simulée. OK",
                        'token_count': len(prompt.split()) * 1.5,
                        'duration': 0.5
                    }
                }

                task['status'] = 'completed'
                task['result'] = result['result']
                task['end_time'] = datetime.now().isoformat()

                return result

            logger.info(f"Tâche {task_id} créée pour {platform}")
            return task_id

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du prompt: {str(e)}")
            raise OrchestrationError(f"Échec de l'envoi: {str(e)}")

    def compare_responses(self, prompt, platforms=None, mode="standard", timeout=60):
        """
        Compare les réponses de plusieurs plateformes

        Args:
            prompt (str): Prompt à envoyer
            platforms (list, optional): Liste des plateformes
            mode (str): Mode d'opération
            timeout (float): Délai maximum

        Returns:
            dict: Résultats par plateforme
        """
        try:
            if platforms is None:
                platforms = self.get_available_platforms()

            results = {}
            threads = []

            def get_response(platform):
                try:
                    start_time = datetime.now()

                    # Simuler un délai différent par plateforme
                    if "chatgpt" in platform.lower():
                        time.sleep(0.5)
                    elif "claude" in platform.lower():
                        time.sleep(0.8)
                    else:
                        time.sleep(0.3)

                    # Réponse simulée
                    duration = (datetime.now() - start_time).total_seconds()

                    results[platform] = {
                        'status': 'completed',
                        'duration': duration,
                        'token_count': int(len(prompt.split()) * 1.5),
                        'result': {
                            'response': f"Réponse simulée de {platform}. OK"
                        }
                    }
                except Exception as e:
                    results[platform] = {
                        'status': 'failed',
                        'error': str(e)
                    }

            # Créer un thread par plateforme
            for platform in platforms:
                thread = threading.Thread(target=get_response, args=(platform,))
                threads.append(thread)
                thread.start()

            # Attendre tous les threads
            for thread in threads:
                thread.join(timeout=timeout)

            return results

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison: {str(e)}")
            raise OrchestrationError(f"Échec de la comparaison: {str(e)}")

    def wait_for_task(self, task_id, timeout=None):
        """
        Attend qu'une tâche soit terminée

        Args:
            task_id (int): ID de la tâche
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultat de la tâche ou None si timeout
        """
        start_time = time.time()

        while True:
            with self.lock:
                task = self.active_tasks.get(task_id)

                if not task:
                    return None

                if task['status'] in ['completed', 'failed']:
                    return task

            # Vérifier le timeout
            if timeout is not None and time.time() - start_time > timeout:
                return None

            # Attendre un peu
            time.sleep(0.1)

    def shutdown(self):
        """Arrêt propre du chef d'orchestre"""
        try:
            self._shutdown = True

            # Attendre la fin des tâches en cours
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5)

            logger.info("Chef d'orchestre arrêté")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt: {str(e)}")

    def _worker_loop(self):
        """Boucle du worker pour traiter les tâches"""
        while not self._shutdown:
            try:
                # Récupérer la tâche la plus prioritaire
                priority, task_id = self.task_queue.get(timeout=1)

                with self.lock:
                    task = self.active_tasks.get(task_id)

                    if not task:
                        continue

                # Traiter la tâche (simulation)
                logger.debug(f"Traitement de la tâche {task_id}")

                # Simuler le traitement
                time.sleep(0.5)

                # Mettre à jour la tâche
                with self.lock:
                    task['status'] = 'completed'
                    task['end_time'] = datetime.now().isoformat()
                    task['result'] = {
                        'response': f"Réponse pour la tâche {task_id}",
                        'token_count': 100,
                        'duration': 0.5
                    }

                # Enregistrer l'utilisation
                self.scheduler.register_usage(task['platform'])

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Erreur dans le worker: {str(e)}")