import time
import threading
import json
from datetime import datetime, timedelta
from utils.logger import logger
from utils.exceptions import SchedulingError


class AIScheduler:
    """
    Classe pour planifier et gérer les limites d'utilisation des IA
    """

    def __init__(self, config_provider):
        """
        Initialise le planificateur

        Args:
            config_provider: Fournisseur de configuration pour les profils d'IA
        """
        logger.info("Initialisation du planificateur d'IA")

        self.config_provider = config_provider

        # Dictionnaire pour suivre l'utilisation par plateforme
        self.usage_counters = {}

        # Verrous pour l'accès concurrent
        self.lock = threading.RLock()

        # Chargement initial des profils
        self.reload_profiles()

    def reload_profiles(self):
        """
        Recharge les profils d'IA depuis le fournisseur de configuration

        Returns:
            bool: True si le rechargement est réussi
        """
        try:
            with self.lock:
                # Obtenir les profiles depuis le fournisseur
                profiles = self.config_provider.get_profiles()

                # Mise à jour des compteurs d'utilisation
                for platform_name, profile in profiles.items():
                    if platform_name not in self.usage_counters:
                        self.usage_counters[platform_name] = {
                            'prompt_count': 0,
                            'token_count': 0,
                            'last_reset': datetime.now().isoformat(),
                            'next_reset': self._calculate_next_reset(profile)
                        }

                logger.debug("Profils d'IA rechargés")
                return True

        except Exception as e:
            logger.error(f"Erreur lors du rechargement des profils: {str(e)}")
            return False

    def _calculate_next_reset(self, profile):
        """
        Calcule la prochaine date de réinitialisation des compteurs

        Args:
            profile (dict): Profil de la plateforme d'IA

        Returns:
            str: Date de réinitialisation au format ISO
        """
        try:
            # Obtenir l'heure de réinitialisation
            reset_time = profile.get('limits', {}).get('reset_time', "00:00:00")

            # Convertir en heures, minutes, secondes
            hours, minutes, seconds = map(int, reset_time.split(':'))

            # Date actuelle
            now = datetime.now()

            # Date de réinitialisation (aujourd'hui)
            reset_date = now.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)

            # Si l'heure est déjà passée, passer au jour suivant
            if now >= reset_date:
                reset_date += timedelta(days=1)

            return reset_date.isoformat()

        except Exception as e:
            logger.error(f"Erreur lors du calcul de réinitialisation: {str(e)}")
            return (datetime.now() + timedelta(days=1)).isoformat()

    def can_use_platform(self, platform_name):
        """
        Vérifie si une plateforme peut être utilisée (quotas non dépassés)

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            tuple: (utilisable, raison)
        """
        try:
            with self.lock:
                profiles = self.config_provider.get_profiles()
                profile = profiles.get(platform_name)

                if not profile:
                    return False, f"Profil non trouvé pour {platform_name}"

                counter = self.usage_counters.get(platform_name, {})

                # Vérifier si une réinitialisation est nécessaire
                self._check_reset_counter(platform_name, profile)

                # Récupérer les limites
                limits = profile.get('limits', {})
                max_prompts = limits.get('prompts_per_day', float('inf'))

                # Vérifier les quotas
                if counter.get('prompt_count', 0) >= max_prompts:
                    next_reset = counter.get('next_reset', 'unknown')
                    if isinstance(next_reset, str):
                        next_reset_dt = datetime.fromisoformat(next_reset)
                        time_left = next_reset_dt - datetime.now()
                        hours, remainder = divmod(time_left.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        time_str = f"{hours}h {minutes}m"
                    else:
                        time_str = "unknown"

                    return False, f"Limite de prompts atteinte pour {platform_name}. Réinitialisation dans {time_str}."

                return True, "OK"

        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'utilisation: {str(e)}")
            return False, f"Erreur: {str(e)}"

    def _check_reset_counter(self, platform_name, profile):
        """
        Vérifie et réinitialise le compteur si nécessaire

        Args:
            platform_name (str): Nom de la plateforme
            profile (dict): Profil de la plateforme
        """
        try:
            counter = self.usage_counters.get(platform_name, {})

            # Vérifier si une réinitialisation est nécessaire
            if 'next_reset' in counter:
                next_reset = counter['next_reset']

                if isinstance(next_reset, str):
                    next_reset_dt = datetime.fromisoformat(next_reset)
                else:
                    next_reset_dt = next_reset

                if datetime.now() >= next_reset_dt:
                    # Réinitialiser les compteurs
                    counter['prompt_count'] = 0
                    counter['token_count'] = 0
                    counter['last_reset'] = datetime.now().isoformat()
                    counter['next_reset'] = self._calculate_next_reset(profile)

                    logger.info(f"Compteurs réinitialisés pour {platform_name}")
            else:
                # Initialiser si c'est la première utilisation
                counter['prompt_count'] = 0
                counter['token_count'] = 0
                counter['last_reset'] = datetime.now().isoformat()
                counter['next_reset'] = self._calculate_next_reset(profile)

            self.usage_counters[platform_name] = counter

        except Exception as e:
            logger.error(f"Erreur lors de la vérification de réinitialisation: {str(e)}")

    def register_usage(self, platform_name, token_count=1):
        """
        Enregistre l'utilisation d'une plateforme

        Args:
            platform_name (str): Nom de la plateforme
            token_count (int): Nombre de tokens utilisés

        Returns:
            bool: True si l'enregistrement est réussi
        """
        try:
            with self.lock:
                # Obtenir le compteur actuel
                counter = self.usage_counters.get(platform_name, {
                    'prompt_count': 0,
                    'token_count': 0,
                    'last_reset': datetime.now().isoformat()
                })

                # Incrémenter les compteurs
                counter['prompt_count'] = counter.get('prompt_count', 0) + 1
                counter['token_count'] = counter.get('token_count', 0) + token_count

                # Mettre à jour
                self.usage_counters[platform_name] = counter

                logger.debug(f"Usage enregistré pour {platform_name}: +1 prompt, +{token_count} tokens")
                return True

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement d'utilisation: {str(e)}")
            return False

    def get_platform_availability(self):
        """
        Récupère la disponibilité de toutes les plateformes

        Returns:
            dict: Statut de disponibilité par plateforme
        """
        try:
            with self.lock:
                profiles = self.config_provider.get_profiles()
                results = {}

                for platform_name in profiles.keys():
                    can_use, reason = self.can_use_platform(platform_name)

                    # Mettre à jour les compteurs si nécessaire
                    self._check_reset_counter(platform_name, profiles[platform_name])

                    # Récupérer les limites
                    limits = profiles[platform_name].get('limits', {})
                    max_prompts = limits.get('prompts_per_day', float('inf'))

                    # Récupérer les compteurs
                    counter = self.usage_counters.get(platform_name, {})
                    prompt_count = counter.get('prompt_count', 0)
                    token_count = counter.get('token_count', 0)
                    next_reset = counter.get('next_reset', '')

                    # Convertir next_reset en un format lisible
                    if isinstance(next_reset, str) and next_reset:
                        try:
                            next_reset_dt = datetime.fromisoformat(next_reset)
                            next_reset = next_reset_dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            pass

                    results[platform_name] = {
                        'available': can_use,
                        'reason': reason,
                        'used_prompts': prompt_count,
                        'max_prompts': max_prompts,
                        'used_tokens': token_count,
                        'next_reset': next_reset
                    }

                return results

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des disponibilités: {str(e)}")
            return {}

    def get_cooldown_time(self, platform_name):
        """
        Récupère le temps de pause recommandé entre les requêtes

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            float: Temps de pause en secondes
        """
        try:
            profiles = self.config_provider.get_profiles()
            profile = profiles.get(platform_name)

            if not profile:
                return 0.0

            # Récupérer le temps de cooldown de la configuration
            cooldown = profile.get('limits', {}).get('cooldown_period', 0)

            return float(cooldown)

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du cooldown: {str(e)}")
            return 0.0

    def create_wait_event(self, platform_name):
        """
        Crée un événement wait pour le temps de cooldown spécifié

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            threading.Event: Événement qui sera déclenché après le cooldown
        """
        cooldown = self.get_cooldown_time(platform_name)
        event = threading.Event()

        if cooldown <= 0:
            # Pas de cooldown nécessaire
            event.set()
            return event

        def trigger_after_cooldown():
            time.sleep(cooldown)
            event.set()

        # Démarrer un thread pour le cooldown
        thread = threading.Thread(target=trigger_after_cooldown)
        thread.daemon = True
        thread.start()

        return event

    def save_usage_stats(self, file_path=None):
        """
        Sauvegarde les statistiques d'utilisation dans un fichier

        Args:
            file_path (str, optional): Chemin du fichier

        Returns:
            bool: True si la sauvegarde est réussie
        """
        try:
            if file_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"usage_stats_{timestamp}.json"

            with self.lock:
                # Préparer les données
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'usage': self.usage_counters
                }

                # Sauvegarder dans le fichier
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)

                logger.info(f"Statistiques d'utilisation sauvegardées: {file_path}")
                return True

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des statistiques: {str(e)}")
            return False

    def load_usage_stats(self, file_path):
        """
        Charge les statistiques d'utilisation depuis un fichier

        Args:
            file_path (str): Chemin du fichier

        Returns:
            bool: True si le chargement est réussi
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            with self.lock:
                if 'usage' in data:
                    self.usage_counters = data['usage']
                    logger.info(f"Statistiques d'utilisation chargées: {file_path}")
                    return True
                else:
                    logger.warning(f"Format de fichier invalide: {file_path}")
                    return False

        except Exception as e:
            logger.error(f"Erreur lors du chargement des statistiques: {str(e)}")
            return False