import queue
import threading
import time
from datetime import datetime
from utils.logger import logger
from utils.exceptions import SchedulingError


class TaskQueue:
    """
    Classe pour gérer une file d'attente des tâches d'automatisation
    """

    def __init__(self, scheduler=None):
        """
        Initialise la file d'attente des tâches

        Args:
            scheduler (AIScheduler, optional): Planificateur pour vérifier les disponibilités
        """
        logger.info("Initialisation de la file d'attente des tâches")

        # File d'attente des tâches
        self.task_queue = queue.PriorityQueue()

        # Planificateur
        self.scheduler = scheduler

        # Verrou pour l'accès concurrent
        self.lock = threading.RLock()

        # Événement pour signaler l'arrêt
        self.stop_event = threading.Event()

        # File d'attente des résultats
        self.results = {}

        # Compteur pour les IDs de tâche
        self.task_counter = 0

    def add_task(self, task_func, platform_name, priority=0, task_args=None, task_kwargs=None):
        """
        Ajoute une tâche à la file d'attente

        Args:
            task_func (callable): Fonction de la tâche
            platform_name (str): Nom de la plateforme d'IA
            priority (int): Priorité (0 = normale, valeurs négatives = plus haute priorité)
            task_args (tuple, optional): Arguments positionnels
            task_kwargs (dict, optional): Arguments nommés

        Returns:
            int: ID de la tâche
        """
        with self.lock:
            self.task_counter += 1
            task_id = self.task_counter

            # Initialiser le résultat
            self.results[task_id] = {
                'status': 'pending',
                'start_time': None,
                'end_time': None,
                'result': None,
                'error': None
            }

            # Créer la tâche
            task = {
                'id': task_id,
                'func': task_func,
                'platform': platform_name,
                'args': task_args or (),
                'kwargs': task_kwargs or {},
                'added_time': datetime.now()
            }

            # Ajouter à la file d'attente
            self.task_queue.put((priority, task))

            logger.debug(f"Tâche {task_id} ajoutée à la file d'attente pour {platform_name}")
            return task_id

    def get_task_result(self, task_id):
        """
        Récupère le résultat d'une tâche

        Args:
            task_id (int): ID de la tâche

        Returns:
            dict: Informations sur la tâche et son résultat
        """
        with self.lock:
            return self.results.get(task_id, {'status': 'unknown'})

    def wait_for_task(self, task_id, timeout=None):
        """
        Attend que la tâche soit terminée

        Args:
            task_id (int): ID de la tâche
            timeout (float, optional): Délai d'attente en secondes

        Returns:
            dict: Résultat de la tâche ou None si timeout
        """
        start_time = time.time()

        while True:
            result = self.get_task_result(task_id)
            status = result.get('status')

            if status in ['completed', 'failed']:
                return result

            # Vérifier le timeout
            if timeout is not None and time.time() - start_time > timeout:
                return None

            # Attendre un peu avant de vérifier à nouveau
            time.sleep(0.1)

    def start_processing(self, num_workers=1):
        """
        Démarre le traitement des tâches

        Args:
            num_workers (int): Nombre de workers

        Returns:
            list: Liste des threads workers
        """
        self.stop_event.clear()
        workers = []

        for i in range(num_workers):
            worker = threading.Thread(target=self._worker_thread, args=(i,))
            worker.daemon = True
            worker.start()
            workers.append(worker)

        logger.info(f"{num_workers} worker(s) démarré(s) pour le traitement des tâches")
        return workers

    def stop_processing(self, wait=True):
        """
        Arrête le traitement des tâches

        Args:
            wait (bool): Attendre que les tâches en cours se terminent

        Returns:
            bool: True si l'arrêt est réussi
        """
        self.stop_event.set()

        if wait:
            # Attendre que la file d'attente soit vide
            while not self.task_queue.empty():
                time.sleep(0.1)

        logger.info("Traitement des tâches arrêté")
        return True

    def clear_queue(self):
        """
        Vide la file d'attente des tâches

        Returns:
            int: Nombre de tâches supprimées
        """
        with self.lock:
            # Compter les tâches
            count = self.task_queue.qsize()

            # Créer une nouvelle file d'attente
            self.task_queue = queue.PriorityQueue()

            # Marquer les tâches comme annulées
            for task_id, result in self.results.items():
                if result['status'] == 'pending':
                    self.results[task_id]['status'] = 'cancelled'

            logger.info(f"{count} tâche(s) supprimée(s) de la file d'attente")
            return count

    def get_queue_status(self):
        """
        Récupère le statut de la file d'attente

        Returns:
            dict: Informations sur la file d'attente
        """
        with self.lock:
            pending_count = self.task_queue.qsize()

            # Compter les tâches par statut
            status_counts = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0, 'cancelled': 0}

            for result in self.results.values():
                status = result.get('status', 'unknown')
                if status in status_counts:
                    status_counts[status] += 1

            # Ajouter le nombre en attente
            status_counts['pending'] = pending_count

            return {
                'queue_size': pending_count,
                'status_counts': status_counts,
                'processing_active': not self.stop_event.is_set()
            }

    def _worker_thread(self, worker_id):
        """
        Fonction exécutée par chaque thread worker

        Args:
            worker_id (int): ID du worker
        """
        logger.debug(f"Worker {worker_id} démarré")

        while not self.stop_event.is_set():
            try:
                # Récupérer une tâche avec un timeout
                try:
                    priority, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                task_id = task['id']
                platform = task['platform']

                logger.debug(f"Worker {worker_id} traite la tâche {task_id} pour {platform}")

                # Vérifier la disponibilité de la plateforme
                if self.scheduler:
                    can_use, reason = self.scheduler.can_use_platform(platform)

                    if not can_use:
                        logger.warning(f"Plateforme {platform} non disponible: {reason}")

                        # Remettre la tâche dans la file d'attente avec un délai
                        time.sleep(5)  # Attendre un peu avant de réessayer
                        self.task_queue.put((priority, task))
                        self.task_queue.task_done()
                        continue

                # Marquer comme en cours d'exécution
                with self.lock:
                    self.results[task_id]['status'] = 'running'
                    self.results[task_id]['start_time'] = datetime.now()

                # Exécuter la tâche
                try:
                    result = task['func'](*task['args'], **task['kwargs'])

                    # Marquer comme terminée
                    with self.lock:
                        self.results[task_id]['status'] = 'completed'
                        self.results[task_id]['end_time'] = datetime.now()
                        self.results[task_id]['result'] = result

                    # Enregistrer l'utilisation si disponible
                    if self.scheduler:
                        self.scheduler.register_usage(platform)

                    logger.debug(f"Tâche {task_id} terminée avec succès")

                except Exception as e:
                    # Marquer comme échouée
                    with self.lock:
                        self.results[task_id]['status'] = 'failed'
                        self.results[task_id]['end_time'] = datetime.now()
                        self.results[task_id]['error'] = str(e)

                    logger.error(f"Échec de la tâche {task_id}: {str(e)}")

                # Marquer la tâche comme terminée dans la file d'attente
                self.task_queue.task_done()

                # Appliquer le cooldown si nécessaire
                if self.scheduler:
                    cooldown = self.scheduler.get_cooldown_time(platform)
                    if cooldown > 0:
                        logger.debug(f"Cooldown de {cooldown}s pour {platform}")
                        time.sleep(cooldown)

            except Exception as e:
                logger.error(f"Erreur dans le worker {worker_id}: {str(e)}")
                time.sleep(1)  # Éviter une boucle d'erreurs trop rapide

        logger.debug(f"Worker {worker_id} arrêté")