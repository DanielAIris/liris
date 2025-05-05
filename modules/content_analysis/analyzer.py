import threading
import time
import json
from datetime import datetime
from utils.logger import logger
from utils.exceptions import ContentAnalysisError
from templates.content_analysis.structured_prompts import get_analysis_prompt
from templates.content_analysis.text_prompts import get_summary_prompt


class ContentAnalyzer:
    """
    Classe pour analyser du contenu texte et structuré avec l'IA
    """

    def __init__(self, conductor, database=None):
        """
        Initialise l'analyseur de contenu

        Args:
            conductor: Chef d'orchestre pour exécuter les opérations
            database (Database, optional): Connexion à la base de données
        """
        logger.info("Initialisation de l'analyseur de contenu")

        self.conductor = conductor
        self.database = database

        # Registre des analyses en cours
        self.active_analyses = {}

        # Verrou pour l'accès concurrent
        self.lock = threading.RLock()

    def analyze_text(self, content, analysis_type="summary", platform=None, sync=True, timeout=60):
        """
        Analyse un contenu textuel

        Args:
            content (str): Contenu à analyser
            analysis_type (str): Type d'analyse ("summary", "keywords", "sentiment", etc.)
            platform (str, optional): Plateforme IA à utiliser
            sync (bool): Mode synchrone
            timeout (float, optional): Délai maximum d'attente en mode synchrone

        Returns:
            dict/str: Résultats de l'analyse ou ID de l'analyse (async)
        """
        try:
            # Valider le contenu
            if not content:
                raise ContentAnalysisError("Contenu vide, impossible à analyser")

            # Choisir une plateforme disponible
            if platform is None:
                available = self.conductor.get_available_platforms()
                if not available:
                    raise ContentAnalysisError("Aucune plateforme disponible")
                platform = available[0]

            # Créer la session d'analyse
            analysis_id = f"analysis_{int(time.time())}"

            # Préparer le prompt selon le type d'analyse
            if analysis_type == "summary":
                prompt_template = get_summary_prompt()
                mode = "analyze"
            elif analysis_type == "keywords":
                prompt_template = get_summary_prompt("keywords")
                mode = "analyze"
            elif analysis_type == "sentiment":
                prompt_template = get_summary_prompt("sentiment")
                mode = "analyze"
            else:
                # Type par défaut
                prompt_template = get_summary_prompt()
                mode = "analyze"

            # Remplir le template
            prompt = prompt_template.format(content=content)

            # Initialiser l'analyse
            analysis = {
                'id': analysis_id,
                'content_preview': content[:100] + "..." if len(content) > 100 else content,
                'type': analysis_type,
                'platform': platform,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'result': None
            }

            # Enregistrer l'analyse
            with self.lock:
                self.active_analyses[analysis_id] = analysis

            # Mode synchrone : exécuter et attendre
            if sync:
                return self._execute_analysis(analysis, prompt, mode, timeout)

            # Mode asynchrone : démarrer un thread
            thread = threading.Thread(
                target=self._execute_analysis,
                args=(analysis, prompt, mode, None)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"Analyse {analysis_id} démarrée en mode asynchrone sur {platform}")
            return analysis_id

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de texte: {str(e)}")
            raise ContentAnalysisError(f"Échec de l'analyse: {str(e)}")

    def analyze_structured(self, content, structure_type="json", analysis_spec=None, platform=None, sync=True,
                           timeout=60):
        """
        Analyse un contenu structuré (JSON, XML, etc.)

        Args:
            content (dict/str): Contenu à analyser
            structure_type (str): Type de structure ("json", "xml", etc.)
            analysis_spec (dict): Spécifications d'analyse
            platform (str, optional): Plateforme IA à utiliser
            sync (bool): Mode synchrone
            timeout (float, optional): Délai maximum d'attente en mode synchrone

        Returns:
            dict/str: Résultats de l'analyse ou ID de l'analyse (async)
        """
        try:
            # Valider le contenu
            if not content:
                raise ContentAnalysisError("Contenu vide, impossible à analyser")

            # Choisir une plateforme disponible
            if platform is None:
                available = self.conductor.get_available_platforms()
                if not available:
                    raise ContentAnalysisError("Aucune plateforme disponible")
                platform = available[0]

            # Créer la session d'analyse
            analysis_id = f"analysis_{int(time.time())}"

            # Convertir en chaîne si nécessaire
            content_str = content
            if isinstance(content, dict):
                content_str = json.dumps(content, indent=2)

            # Préparer le prompt pour l'analyse structurée
            prompt_template = get_analysis_prompt(structure_type)

            # Préparer les spécifications
            spec_str = ""
            if analysis_spec:
                if isinstance(analysis_spec, dict):
                    spec_str = json.dumps(analysis_spec, indent=2)
                else:
                    spec_str = str(analysis_spec)

            # Remplir le template
            prompt = prompt_template.format(
                content=content_str,
                spec=spec_str
            )

            # Initialiser l'analyse
            analysis = {
                'id': analysis_id,
                'content_preview': str(content)[:100] + "..." if len(str(content)) > 100 else str(content),
                'type': f"structured_{structure_type}",
                'platform': platform,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'result': None
            }

            # Enregistrer l'analyse
            with self.lock:
                self.active_analyses[analysis_id] = analysis

            # Mode synchrone : exécuter et attendre
            if sync:
                return self._execute_analysis(analysis, prompt, "analyze", timeout)

            # Mode asynchrone : démarrer un thread
            thread = threading.Thread(
                target=self._execute_analysis,
                args=(analysis, prompt, "analyze", None)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"Analyse structurée {analysis_id} démarrée en mode asynchrone sur {platform}")
            return analysis_id

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse structurée: {str(e)}")
            raise ContentAnalysisError(f"Échec de l'analyse: {str(e)}")

    def _execute_analysis(self, analysis, prompt, mode, timeout=None):
        """
        Exécute l'analyse via le chef d'orchestre

        Args:
            analysis (dict): Informations sur l'analyse
            prompt (str): Prompt à envoyer
            mode (str): Mode d'opération
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultats de l'analyse
        """
        analysis_id = analysis['id']
        platform = analysis['platform']

        try:
            # Mettre à jour le statut
            analysis['status'] = 'running'

            # Envoyer le prompt
            response = self.conductor.send_prompt(
                platform, prompt, mode=mode, sync=True, timeout=timeout
            )

            # Analyser la réponse
            if response and 'result' in response:
                analysis['result'] = response['result']
                analysis['status'] = 'completed'
                analysis['end_time'] = datetime.now().isoformat()

                logger.info(f"Analyse {analysis_id} terminée avec succès")
                return analysis
            else:
                raise ContentAnalysisError("Pas de résultat valide reçu")

        except Exception as e:
            # Marquer comme échouée
            analysis['status'] = 'failed'
            analysis['error'] = str(e)
            analysis['end_time'] = datetime.now().isoformat()

            logger.error(f"Échec de l'analyse {analysis_id}: {str(e)}")
            return analysis

    def get_analysis_status(self, analysis_id):
        """
        Récupère le statut d'une analyse

        Args:
            analysis_id (str): ID de l'analyse

        Returns:
            dict: Statut de l'analyse
        """
        with self.lock:
            analysis = self.active_analyses.get(analysis_id)

            if not analysis:
                raise ContentAnalysisError(f"Analyse {analysis_id} non trouvée")

            return {
                'id': analysis['id'],
                'type': analysis['type'],
                'platform': analysis['platform'],
                'status': analysis['status'],
                'start_time': analysis['start_time'],
                'end_time': analysis.get('end_time')
            }

    def get_analysis_result(self, analysis_id):
        """
        Récupère le résultat d'une analyse

        Args:
            analysis_id (str): ID de l'analyse

        Returns:
            dict: Résultat complet de l'analyse
        """
        with self.lock:
            analysis = self.active_analyses.get(analysis_id)

            if not analysis:
                raise ContentAnalysisError(f"Analyse {analysis_id} non trouvée")

            # Vérifier si l'analyse est terminée
            if analysis['status'] not in ['completed', 'failed']:
                raise ContentAnalysisError(f"Analyse {analysis_id} en cours: {analysis['status']}")

            return dict(analysis)

    def wait_for_analysis(self, analysis_id, timeout=None):
        """
        Attend la fin d'une analyse

        Args:
            analysis_id (str): ID de l'analyse
            timeout (float, optional): Délai maximum d'attente

        Returns:
            dict: Résultat de l'analyse ou None si timeout
        """
        start_time = time.time()

        while True:
            # Vérifier le timeout
            if timeout is not None and time.time() - start_time > timeout:
                logger.warning(f"Timeout atteint pour l'analyse {analysis_id}")
                return None

            # Vérifier le statut
            with self.lock:
                analysis = self.active_analyses.get(analysis_id)

                if not analysis:
                    raise ContentAnalysisError(f"Analyse {analysis_id} non trouvée")

                if analysis['status'] in ['completed', 'failed']:
                    return analysis

            # Attendre un peu
            time.sleep(0.5)

    def analyze_multi_platform(self, content, analysis_type="summary", platforms=None, timeout=60):
        """
        Analyse un contenu sur plusieurs plateformes

        Args:
            content (str): Contenu à analyser
            analysis_type (str): Type d'analyse
            platforms (list, optional): Liste des plateformes
            timeout (float): Délai maximum d'attente

        Returns:
            dict: Résultats par plateforme
        """
        # Si platforms non spécifié, utiliser toutes les disponibles
        if platforms is None:
            platforms = self.conductor.get_available_platforms()

        analysis_ids = {}
        results = {}

        # Lancer les analyses sur toutes les plateformes
        for platform in platforms:
            try:
                analysis_id = self.analyze_text(
                    content, analysis_type, platform, sync=False
                )
                analysis_ids[platform] = analysis_id
            except Exception as e:
                logger.error(f"Erreur lors du lancement sur {platform}: {str(e)}")
                results[platform] = {'status': 'failed', 'error': str(e)}

        # Attendre et récupérer les résultats
        start_time = time.time()

        for platform, analysis_id in analysis_ids.items():
            try:
                # Calculer le temps restant
                elapsed = time.time() - start_time
                remaining = max(0, timeout - elapsed)

                # Attendre le résultat
                result = self.wait_for_analysis(analysis_id, timeout=remaining)

                if result is None:
                    results[platform] = {'status': 'timeout', 'error': 'Délai expiré'}
                else:
                    results[platform] = result

            except Exception as e:
                logger.error(f"Erreur lors de la récupération pour {platform}: {str(e)}")
                results[platform] = {'status': 'failed', 'error': str(e)}

        return results

    def compare_analyses(self, results):
        """
        Compare les résultats d'analyses multiples

        Args:
            results (dict): Résultats par plateforme

        Returns:
            dict: Comparaison et consensus
        """
        try:
            # Vérifier s'il y a des résultats
            completed_results = {}

            for platform, result in results.items():
                if result.get('status') == 'completed' and 'result' in result:
                    response = result.get('result', {}).get('response', '')
                    if response:
                        completed_results[platform] = response

            # S'il n'y a pas assez de résultats pour comparer
            if len(completed_results) < 2:
                return {
                    'status': 'incomplete',
                    'message': f"Pas assez de résultats pour comparer ({len(completed_results)}/2 minimum)",
                    'results': results
                }

            # Analyser les similitudes et différences
            # Note: Cette fonction pourrait être améliorée avec une comparaison plus sophistiquée

            # Pour l'instant, retourner les résultats bruts
            return {
                'status': 'completed',
                'platforms': list(completed_results.keys()),
                'results_count': len(completed_results),
                'individual_results': completed_results,
                # Ici, on pourrait ajouter une analyse des similitudes et différences
            }

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison des analyses: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'results': results
            }