import threading
import time
import json
from datetime import datetime
from utils.logger import logger
from utils.exceptions import BrainstormingError
from templates.brainstorming.competition_prompts import get_solution_prompt
from templates.brainstorming.evaluation_prompts import get_evaluation_prompt
from templates.brainstorming.scoring_prompts import get_scoring_prompt


class BrainstormingOrchestrator:
    """
    Orchestre les sessions de brainstorming multi-IA compétitives
    """

    def __init__(self, conductor, database=None):
        """
        Initialise l'orchestrateur de brainstorming

        Args:
            conductor: Chef d'orchestre pour exécuter les opérations
            database (Database, optional): Connexion à la base de données
        """
        logger.info("Initialisation de l'orchestrateur de brainstorming")

        self.conductor = conductor
        self.database = database

        # Registre des sessions en cours
        self.active_sessions = {}

        # Verrou pour l'accès concurrent
        self.lock = threading.RLock()

    def create_session(self, name, context, platforms=None):
        """
        Crée une nouvelle session de brainstorming

        Args:
            name (str): Nom de la session
            context (str): Contexte/problème à résoudre
            platforms (list, optional): Plateformes d'IA à utiliser

        Returns:
            int: ID de session
        """
        try:
            # Si platforms non spécifié, utiliser toutes les disponibles
            if platforms is None:
                platforms = self.conductor.get_available_platforms()

            # Créer la session en base de données
            session_id = None
            if self.database:
                session_id = self.database.create_brainstorming_session(
                    name, platforms, context
                )
            else:
                # Générer un ID temporaire si pas de base de données
                session_id = int(time.time())

            # Initialiser la session
            session = {
                'id': session_id,
                'name': name,
                'context': context,
                'platforms': platforms,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'solutions': {},
                'evaluations': {},
                'final_scores': {}
            }

            # Enregistrer la session
            with self.lock:
                self.active_sessions[session_id] = session

            logger.info(f"Session de brainstorming créée: {name} (ID: {session_id})")
            return session_id

        except Exception as e:
            logger.error(f"Erreur lors de la création de session: {str(e)}")
            raise BrainstormingError(f"Échec de la création de session: {str(e)}")

    def start_session(self, session_id, sync=False, timeout=None):
        """
        Démarre une session de brainstorming

        Args:
            session_id (int): ID de session
            sync (bool): Mode synchrone
            timeout (float, optional): Délai maximum d'attente en mode synchrone

        Returns:
            bool/dict: True (async) ou résultats complets (sync)
        """
        try:
            # Récupérer la session
            session = self._get_session(session_id)

            # Vérifier si déjà démarrée
            if session['status'] not in ['created', 'failed']:
                raise BrainstormingError(f"La session {session_id} est déjà démarrée ou terminée")

            # Mettre à jour le statut
            session['status'] = 'running'

            # En mode synchrone, exécuter et attendre
            if sync:
                return self._execute_brainstorming(session, timeout)

            # En mode asynchrone, démarrer un thread
            thread = threading.Thread(
                target=self._execute_brainstorming,
                args=(session, None)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"Session de brainstorming {session_id} démarrée en mode asynchrone")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du démarrage de session {session_id}: {str(e)}")
            raise BrainstormingError(f"Échec du démarrage: {str(e)}")

    def _execute_brainstorming(self, session, timeout=None):
        """
        Exécute le processus de brainstorming

        Args:
            session (dict): Informations de session
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultats complets
        """
        session_id = session['id']
        start_time = time.time()

        try:
            # Étape 1: Obtenir les solutions de chaque plateforme
            self._generate_solutions(session, timeout)

            # Vérifier le timeout
            if timeout is not None and time.time() - start_time > timeout:
                raise BrainstormingError("Délai dépassé pendant la génération des solutions")

            # Étape 2: Évaluations croisées
            remaining_time = None
            if timeout is not None:
                remaining_time = max(0, timeout - (time.time() - start_time))

            self._evaluate_solutions(session, remaining_time)

            # Étape 3: Scoring final
            if timeout is not None:
                remaining_time = max(0, timeout - (time.time() - start_time))

            self._calculate_final_scores(session, remaining_time)

            # Mettre à jour le statut
            session['status'] = 'completed'
            session['end_time'] = datetime.now().isoformat()

            # Sauvegarder dans la base de données si disponible
            if self.database:
                self.database.update_brainstorming_status(session_id, 'completed')

            logger.info(f"Session de brainstorming {session_id} terminée avec succès")
            return session

        except Exception as e:
            # Marquer comme échouée
            session['status'] = 'failed'
            session['error'] = str(e)
            session['end_time'] = datetime.now().isoformat()

            if self.database:
                self.database.update_brainstorming_status(session_id, 'failed')

            logger.error(f"Échec de la session de brainstorming {session_id}: {str(e)}")
            return session

    def _generate_solutions(self, session, timeout=None):
        """
        Génère des solutions pour chaque plateforme

        Args:
            session (dict): Informations de session
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Solutions par plateforme
        """
        session_id = session['id']
        platforms = session['platforms']
        context = session['context']

        start_time = time.time()
        task_ids = {}

        # Récupérer le template de prompt
        prompt_template = get_solution_prompt()

        # Envoyer le prompt à chaque plateforme
        for platform in platforms:
            try:
                # Remplir le template
                prompt = prompt_template.format(context=context)

                task_id = self.conductor.send_prompt(
                    platform, prompt, mode="brainstorm", priority=-1
                )
                task_ids[platform] = task_id

                logger.debug(f"Prompt de brainstorming envoyé à {platform} (Tâche: {task_id})")

            except Exception as e:
                logger.error(f"Erreur lors de l'envoi à {platform}: {str(e)}")
                session['solutions'][platform] = {
                    'error': str(e),
                    'status': 'failed'
                }

        # Attendre et collecter les résultats
        for platform, task_id in task_ids.items():
            try:
                # Calculer le temps restant
                if timeout is not None:
                    remaining = max(0, timeout - (time.time() - start_time))
                    if remaining <= 0:
                        logger.warning(f"Délai dépassé pour {platform}, solution ignorée")
                        continue
                else:
                    remaining = None

                # Attendre le résultat
                task_result = self.conductor.wait_for_task(task_id, timeout=remaining)

                if task_result is None:
                    logger.warning(f"Timeout pour {platform}, solution ignorée")
                    continue

                if task_result.get('status') == 'completed':
                    solution = task_result.get('result', {}).get('response', '')

                    # Enregistrer la solution
                    session['solutions'][platform] = {
                        'content': solution,
                        'timestamp': datetime.now().isoformat()
                    }

                    # Enregistrer dans la base de données si disponible
                    if self.database:
                        self.database.record_brainstorming_result(
                            session_id, platform, solution
                        )

                    logger.debug(f"Solution reçue de {platform} ({len(solution)} caractères)")
                else:
                    error = task_result.get('error', 'Erreur inconnue')
                    session['solutions'][platform] = {
                        'error': error,
                        'status': 'failed'
                    }
                    logger.warning(f"Échec de {platform}: {error}")

            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la solution de {platform}: {str(e)}")
                session['solutions'][platform] = {
                    'error': str(e),
                    'status': 'failed'
                }

        return session['solutions']

    def _evaluate_solutions(self, session, timeout=None):
        """
        Fait évaluer les solutions par chaque plateforme

        Args:
            session (dict): Informations de session
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Évaluations par plateforme
        """
        context = session['context']
        solutions = {p: s.get('content', '') for p, s in session['solutions'].items()
                     if isinstance(s, dict) and 'content' in s}

        # Si moins de 2 solutions, pas d'évaluation croisée possible
        if len(solutions) < 2:
            logger.warning("Évaluation impossible: moins de 2 solutions valides")
            return {}

        start_time = time.time()
        task_ids = {}
        evaluations = {}

        # Récupérer le template d'évaluation
        eval_template = get_evaluation_prompt()

        # Pour chaque plateforme, évaluer les solutions des autres
        for evaluator, evaluator_solution in solutions.items():
            evaluations[evaluator] = {}

            # Pour chaque solution (sauf celle de l'évaluateur)
            for platform, solution in solutions.items():
                if platform == evaluator:
                    continue

                # Préparer le prompt
                prompt = eval_template.format(
                    context=context,
                    platform=platform,
                    solution=solution
                )

                try:
                    # Envoyer la demande d'évaluation
                    task_id = self.conductor.send_prompt(
                        evaluator, prompt, mode="standard", priority=0
                    )

                    if platform not in task_ids:
                        task_ids[platform] = {}

                    task_ids[platform][evaluator] = task_id

                    logger.debug(f"{evaluator} évalue la solution de {platform} (Tâche: {task_id})")

                except Exception as e:
                    logger.error(f"Erreur lors de la demande d'évaluation par {evaluator}: {str(e)}")
                    evaluations[evaluator][platform] = f"Erreur: {str(e)}"

        # Attendre et collecter les résultats
        for platform, evaluator_tasks in task_ids.items():
            evaluations_for_platform = {}

            for evaluator, task_id in evaluator_tasks.items():
                try:
                    # Calculer le temps restant
                    if timeout is not None:
                        remaining = max(0, timeout - (time.time() - start_time))
                        if remaining <= 0:
                            logger.warning(f"Délai dépassé pour l'évaluation de {platform} par {evaluator}")
                            continue
                    else:
                        remaining = None

                    # Attendre le résultat
                    task_result = self.conductor.wait_for_task(task_id, timeout=remaining)

                    if task_result is None:
                        logger.warning(f"Timeout pour l'évaluation de {platform} par {evaluator}")
                        continue

                    if task_result.get('status') == 'completed':
                        evaluation = task_result.get('result', {}).get('response', '')
                        evaluations[evaluator][platform] = evaluation
                        evaluations_for_platform[evaluator] = evaluation

                        logger.debug(f"Évaluation reçue de {evaluator} pour {platform}")
                    else:
                        error = task_result.get('error', 'Erreur inconnue')
                        evaluations[evaluator][platform] = f"Échec: {error}"
                        logger.warning(f"Échec de l'évaluation de {platform} par {evaluator}: {error}")

                except Exception as e:
                    logger.error(f"Erreur lors de la récupération de l'évaluation: {str(e)}")
                    evaluations[evaluator][platform] = f"Erreur: {str(e)}"

            # Enregistrer dans la base de données
            if self.database and platform in solutions:
                self.database.record_brainstorming_result(
                    session['id'],
                    platform,
                    solutions[platform],
                    evaluations=evaluations_for_platform
                )

        # Stocker les évaluations
        session['evaluations'] = evaluations

        return evaluations

    def _calculate_final_scores(self, session, timeout=None):
        """
        Calcule les scores finaux des solutions

        Args:
            session (dict): Informations de session
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Scores finaux par plateforme
        """
        # Récupérer solutions et évaluations
        context = session['context']
        solutions = {p: s.get('content', '') for p, s in session['solutions'].items()
                     if isinstance(s, dict) and 'content' in s}
        evaluations = session.get('evaluations', {})

        # Si pas d'évaluations, impossible de calculer les scores
        if not evaluations:
            logger.warning("Scoring impossible: pas d'évaluations disponibles")
            return {}

        start_time = time.time()
        task_ids = {}
        scores = {}

        # Récupérer le template de scoring
        scoring_template = get_scoring_prompt()

        # On demande à une plateforme (arbitrairement la première) de noter
        # toutes les solutions en fonction des évaluations
        if solutions:
            scorer = list(solutions.keys())[0]

            for platform, solution in solutions.items():
                # Récupérer les évaluations pour cette solution
                platform_evals = {}
                for evaluator, evals in evaluations.items():
                    if platform in evals:
                        platform_evals[evaluator] = evals[platform]

                if not platform_evals:
                    logger.warning(f"Pas d'évaluations pour {platform}, scoring impossible")
                    continue

                # Convertir en texte formaté
                evals_text = "\n\n".join([
                    f"ÉVALUATION PAR {e}:\n{v}"
                    for e, v in platform_evals.items()
                ])

                # Préparer le prompt
                prompt = scoring_template.format(
                    context=context,
                    platform=platform,
                    solution=solution,
                    evaluations=evals_text
                )

                try:
                    # Envoyer la demande de scoring
                    task_id = self.conductor.send_prompt(
                        scorer, prompt, mode="standard", priority=0
                    )
                    task_ids[platform] = task_id

                    logger.debug(f"Demande de scoring pour {platform} (Tâche: {task_id})")

                except Exception as e:
                    logger.error(f"Erreur lors de la demande de scoring pour {platform}: {str(e)}")

            # Attendre et collecter les résultats
            for platform, task_id in task_ids.items():
                try:
                    # Calculer le temps restant
                    if timeout is not None:
                        remaining = max(0, timeout - (time.time() - start_time))
                        if remaining <= 0:
                            logger.warning(f"Délai dépassé pour le scoring de {platform}")
                            continue
                    else:
                        remaining = None

                    # Attendre le résultat
                    task_result = self.conductor.wait_for_task(task_id, timeout=remaining)

                    if task_result is None:
                        logger.warning(f"Timeout pour le scoring de {platform}")
                        continue

                    if task_result.get('status') == 'completed':
                        scoring_result = task_result.get('result', {}).get('response', '')

                        # Extraire le score (format attendu: "SCORE FINAL: X/100")
                        import re
                        score_match = re.search(r"SCORE FINAL:\s*(\d+)/100", scoring_result, re.IGNORECASE)

                        if score_match:
                            score = int(score_match.group(1))
                            scores[platform] = min(100, max(0, score))  # Limiter entre 0 et 100
                            logger.debug(f"Score pour {platform}: {scores[platform]}/100")
                        else:
                            logger.warning(f"Format de score invalide pour {platform}")

                        # Mettre à jour dans la base de données
                        if self.database:
                            self.database.record_brainstorming_result(
                                session['id'],
                                platform,
                                solutions[platform],
                                final_score=scores.get(platform)
                            )
                    else:
                        error = task_result.get('error', 'Erreur inconnue')
                        logger.warning(f"Échec du scoring de {platform}: {error}")

                except Exception as e:
                    logger.error(f"Erreur lors de la récupération du scoring: {str(e)}")

        # Stocker les scores
        session['final_scores'] = scores

        return scores

    def _get_session(self, session_id):
        """
        Récupère une session par son ID

        Args:
            session_id (int): ID de session

        Returns:
            dict: Informations de session
        """
        with self.lock:
            session = self.active_sessions.get(session_id)

            if not session:
                raise BrainstormingError(f"Session {session_id} non trouvée")

            return session

    def get_session_status(self, session_id):
        """
        Récupère le statut d'une session

        Args:
            session_id (int): ID de session

        Returns:
            dict: Statut de la session
        """
        try:
            session = self._get_session(session_id)

            return {
                'id': session['id'],
                'name': session['name'],
                'status': session['status'],
                'platforms': session['platforms'],
                'start_time': session['start_time'],
                'end_time': session.get('end_time'),
                'solution_count': len(session.get('solutions', {})),
                'has_evaluations': bool(session.get('evaluations')),
                'has_scores': bool(session.get('final_scores'))
            }

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {str(e)}")
            raise BrainstormingError(f"Échec de la récupération: {str(e)}")

    def get_session_results(self, session_id):
        """
        Récupère les résultats complets d'une session

        Args:
            session_id (int): ID de session

        Returns:
            dict: Résultats complets
        """
        try:
            session = self._get_session(session_id)

            # Vérifier si la session est terminée
            if session['status'] not in ['completed', 'failed']:
                raise BrainstormingError(f"Session {session_id} non terminée: {session['status']}")

            # Retourner une copie pour éviter les modifications
            return dict(session)

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des résultats: {str(e)}")
            raise BrainstormingError(f"Échec de la récupération: {str(e)}")

    def wait_for_session(self, session_id, timeout=None):
        """
        Attend la fin d'une session

        Args:
            session_id (int): ID de session
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultats de la session ou None si timeout
        """
        start_time = time.time()

        while True:
            # Vérifier le timeout
            if timeout is not None and time.time() - start_time > timeout:
                return None

            try:
                session = self._get_session(session_id)

                # Vérifier si terminée
                if session['status'] in ['completed', 'failed']:
                    return session

                # Attendre un peu
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Erreur lors de l'attente: {str(e)}")
                return None

    def export_results(self, session_id, exporter, format='json'):
        """
        Exporte les résultats d'une session

        Args:
            session_id (int): ID de session
            exporter (DataExporter): Exportateur de données
            format (str): Format d'exportation

        Returns:
            str: Chemin du fichier exporté
        """
        try:
            # Récupérer les résultats complets
            session = self.get_session_results(session_id)

            # Format pour l'exportation
            export_data = {
                'session': {
                    'id': session['id'],
                    'name': session['name'],
                    'context': session['context'],
                    'start_time': session['start_time'],
                    'end_time': session.get('end_time'),
                    'platforms': session['platforms'],
                    'status': session['status']
                },
                'solutions': {}
            }

            # Préparer les solutions
            for platform, solution in session.get('solutions', {}).items():
                if isinstance(solution, dict) and 'content' in solution:
                    export_data['solutions'][platform] = {
                        'content': solution.get('content', ''),
                        'evaluations': {},
                        'score': session.get('final_scores', {}).get(platform)
                    }

                    # Ajouter les évaluations si disponibles
                    for evaluator, evals in session.get('evaluations', {}).items():
                        if platform in evals:
                            export_data['solutions'][platform]['evaluations'][evaluator] = evals[platform]

            # Exporter
            return exporter.export_brainstorming_results(
                export_data['session'],
                list(export_data['solutions'].values()),
                format
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des résultats: {str(e)}")
            raise BrainstormingError(f"Échec de l'exportation: {str(e)}")