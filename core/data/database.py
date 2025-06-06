import sqlite3
import os
import json
from datetime import datetime
from utils.logger import logger
from utils.exceptions import DatabaseError


class Database:
    """
    Classe pour gérer les interactions avec la base de données SQLite
    """

    def __init__(self, db_path=None):
        """
        Initialise la connexion à la base de données

        Args:
            db_path (str, optional): Chemin vers le fichier de base de données
        """
        if db_path is None:
            # Utiliser un chemin par défaut s'il n'est pas spécifié
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                        "data", "liris.db")
        else:
            self.db_path = db_path

        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        logger.info(f"Initialisation de la base de données: {self.db_path}")

        # Établir la connexion
        self.connect()

        # Initialiser les tables
        self._init_tables()

        # Effectuer la migration automatique des profils existants
        self._migrate_existing_profiles()

    def connect(self):
        """
        Établit la connexion à la base de données

        Returns:
            bool: True si la connexion est établie, False sinon
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Activer les foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Configurer pour retourner les résultats comme des dictionnaires
            self.conn.row_factory = sqlite3.Row

            logger.debug("Connexion établie à la base de données")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la connexion à la base de données: {str(e)}")
            raise DatabaseError(f"Échec de connexion à la base de données: {str(e)}")

    def _init_tables(self):
        """
        Initialise les tables nécessaires dans la base de données

        Returns:
            bool: True si l'initialisation est réussie, False sinon
        """
        try:
            cursor = self.conn.cursor()

            # Table des plateformes et leurs configurations
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS platforms
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               name
                               TEXT
                               NOT
                               NULL
                               UNIQUE,
                               profile_data
                               TEXT
                               NOT
                               NULL,
                               created_at
                               TEXT
                               NOT
                               NULL,
                               updated_at
                               TEXT
                               NOT
                               NULL
                           )
                           ''')

            # Table de configuration du clavier (simplifiée)
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS keyboard_config
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               layout_type
                               TEXT
                               NOT
                               NULL,
                               key_delay
                               INTEGER
                               DEFAULT
                               50,
                               accent_delay
                               INTEGER
                               DEFAULT
                               100,
                               accent_method
                               TEXT
                               NOT
                               NULL,
                               block_alt_tab
                               BOOLEAN
                               DEFAULT
                               1,
                               focus_lock
                               BOOLEAN
                               DEFAULT
                               1,
                               protection_timeout
                               INTEGER
                               DEFAULT
                               30,
                               created_at
                               TEXT
                               NOT
                               NULL,
                               updated_at
                               TEXT
                               NOT
                               NULL,
                               is_active
                               BOOLEAN
                               DEFAULT
                               1
                           )
                           ''')

            # Table des sessions d'IA
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS ai_sessions
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               platform_name
                               TEXT
                               NOT
                               NULL,
                               session_date
                               TEXT
                               NOT
                               NULL,
                               prompt_count
                               INTEGER
                               DEFAULT
                               0,
                               token_count
                               INTEGER
                               DEFAULT
                               0,
                               status
                               TEXT
                               DEFAULT
                               'active'
                           )
                           ''')

            # Table des prompts
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS prompts
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               session_id
                               INTEGER,
                               timestamp
                               TEXT
                               NOT
                               NULL,
                               content
                               TEXT
                               NOT
                               NULL,
                               token_count
                               INTEGER
                               DEFAULT
                               0,
                               operation_type
                               TEXT
                               NOT
                               NULL,
                               FOREIGN
                               KEY
                           (
                               session_id
                           ) REFERENCES ai_sessions
                           (
                               id
                           )
                               )
                           ''')

            # Table des réponses
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS responses
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               prompt_id
                               INTEGER,
                               timestamp
                               TEXT
                               NOT
                               NULL,
                               content
                               TEXT
                               NOT
                               NULL,
                               status
                               TEXT
                               DEFAULT
                               'success',
                               FOREIGN
                               KEY
                           (
                               prompt_id
                           ) REFERENCES prompts
                           (
                               id
                           )
                               )
                           ''')

            # Table des datasets générés
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS datasets
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               name
                               TEXT
                               NOT
                               NULL,
                               creation_date
                               TEXT
                               NOT
                               NULL,
                               type
                               TEXT
                               NOT
                               NULL,
                               format
                               TEXT
                               NOT
                               NULL,
                               item_count
                               INTEGER
                               DEFAULT
                               0,
                               filepath
                               TEXT
                               NOT
                               NULL
                           )
                           ''')

            # Table des sessions de brainstorming
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS brainstorming_sessions
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               name
                               TEXT
                               NOT
                               NULL,
                               creation_date
                               TEXT
                               NOT
                               NULL,
                               ai_platforms
                               TEXT
                               NOT
                               NULL,
                               context
                               TEXT
                               NOT
                               NULL,
                               status
                               TEXT
                               DEFAULT
                               'in_progress'
                           )
                           ''')

            # Table des résultats de brainstorming
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS brainstorming_results
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               session_id
                               INTEGER,
                               platform_name
                               TEXT
                               NOT
                               NULL,
                               solution
                               TEXT
                               NOT
                               NULL,
                               evaluations
                               TEXT,
                               final_score
                               INTEGER,
                               FOREIGN
                               KEY
                           (
                               session_id
                           ) REFERENCES brainstorming_sessions
                           (
                               id
                           )
                               )
                           ''')

            self.conn.commit()
            logger.info("Initialisation des tables terminée")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des tables: {str(e)}")
            raise DatabaseError(f"Échec de l'initialisation des tables: {str(e)}")

    def close(self):
        """
        Ferme la connexion à la base de données

        Returns:
            bool: True si la fermeture est réussie, False sinon
        """
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                logger.debug("Connexion à la base de données fermée")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la connexion: {str(e)}")
            return False

    # =====================================================
    # NOUVELLES MÉTHODES POUR GESTION MULTI-FENÊTRES
    # =====================================================

    def _get_default_browser_config(self):
        """
        Retourne la configuration navigateur par défaut avec support multi-fenêtres

        Returns:
            dict: Configuration par défaut
        """
        return {
            "type": "Chrome",
            "path": "",
            "url": "",
            "fullscreen": False,
            # NOUVELLES OPTIONS MULTI-FENÊTRES (avec valeurs par défaut conservant comportement actuel)
            "window_selection_method": "auto",  # "auto" = comportement actuel (première fenêtre)
            "window_order": 1,  # 1 = première fenêtre = comportement actuel
            "window_title_pattern": "",  # Vide = pas de filtrage par titre
            "window_position": None,  # None = pas de filtrage par position
            "window_id": None,  # None = pas de fenêtre spécifique mémorisée
            "window_size": None,  # None = pas de contrainte de taille
            "remember_window": False  # False = ne pas mémoriser la sélection
        }

    def _migrate_browser_config(self, browser_config):
        """
        Migre une configuration navigateur vers le nouveau format multi-fenêtres

        Args:
            browser_config (dict): Configuration existante

        Returns:
            dict: Configuration migrée
        """
        if not browser_config:
            return self._get_default_browser_config()

        # Créer la nouvelle configuration en préservant l'existante
        default_config = self._get_default_browser_config()
        migrated_config = default_config.copy()

        # Préserver toutes les valeurs existantes
        for key, value in browser_config.items():
            migrated_config[key] = value

        # Ajouter les nouveaux champs s'ils n'existent pas
        for key, default_value in default_config.items():
            if key not in migrated_config:
                migrated_config[key] = default_value

        logger.debug(f"Configuration navigateur migrée: {list(migrated_config.keys())}")
        return migrated_config

    def _migrate_existing_profiles(self):
        """
        Migre automatiquement tous les profils existants vers le nouveau format
        """
        try:
            logger.info("Vérification de la migration des profils existants...")

            cursor = self.conn.cursor()
            cursor.execute('SELECT name, profile_data FROM platforms')
            results = cursor.fetchall()

            migration_count = 0

            for row in results:
                try:
                    platform_name = row['name']
                    profile_data = json.loads(row['profile_data'])

                    # Vérifier si la migration est nécessaire
                    browser_config = profile_data.get('browser', {})
                    needs_migration = 'window_selection_method' not in browser_config

                    if needs_migration:
                        logger.debug(f"Migration du profil {platform_name}...")

                        # Migrer la configuration navigateur
                        profile_data['browser'] = self._migrate_browser_config(browser_config)

                        # Sauvegarder le profil migré
                        now = datetime.now().isoformat()
                        profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)

                        cursor.execute('''
                                       UPDATE platforms
                                       SET profile_data = ?,
                                           updated_at   = ?
                                       WHERE name = ?
                                       ''', (profile_json, now, platform_name))

                        migration_count += 1
                        logger.debug(f"Profil {platform_name} migré avec succès")

                except Exception as e:
                    logger.error(f"Erreur migration profil {row['name']}: {str(e)}")
                    continue

            if migration_count > 0:
                self.conn.commit()
                logger.info(f"Migration terminée: {migration_count} profils migrés")
            else:
                logger.debug("Aucune migration nécessaire")

        except Exception as e:
            logger.error(f"Erreur lors de la migration automatique: {str(e)}")

    def validate_browser_config(self, browser_config):
        """
        Valide et normalise une configuration navigateur

        Args:
            browser_config (dict): Configuration à valider

        Returns:
            tuple: (is_valid, normalized_config, error_message)
        """
        try:
            if not browser_config:
                return True, self._get_default_browser_config(), None

            # Cloner la configuration
            normalized = browser_config.copy()

            # Valider window_selection_method
            valid_methods = ["auto", "order", "title", "position", "manual"]
            method = normalized.get('window_selection_method', 'auto')
            if method not in valid_methods:
                normalized['window_selection_method'] = 'auto'
                logger.warning(f"Méthode de sélection invalide '{method}', fallback sur 'auto'")

            # Valider window_order
            order = normalized.get('window_order', 1)
            if not isinstance(order, int) or order < 1:
                normalized['window_order'] = 1
                logger.warning(f"Ordre de fenêtre invalide '{order}', fallback sur 1")

            # Valider window_title_pattern
            title_pattern = normalized.get('window_title_pattern')
            if title_pattern is not None and not isinstance(title_pattern, str):
                normalized['window_title_pattern'] = ""
                logger.warning("Pattern de titre invalide, réinitialisé")

            # Valider window_position
            position = normalized.get('window_position')
            if position is not None:
                if not isinstance(position, dict) or 'x' not in position or 'y' not in position:
                    normalized['window_position'] = None
                    logger.warning("Position de fenêtre invalide, réinitialisée")
                else:
                    try:
                        normalized['window_position']['x'] = int(position['x'])
                        normalized['window_position']['y'] = int(position['y'])
                    except (ValueError, TypeError):
                        normalized['window_position'] = None
                        logger.warning("Coordonnées de position invalides, réinitialisées")

            # S'assurer que tous les champs requis existent
            default_config = self._get_default_browser_config()
            for key, default_value in default_config.items():
                if key not in normalized:
                    normalized[key] = default_value

            return True, normalized, None

        except Exception as e:
            error_msg = f"Erreur validation config navigateur: {str(e)}"
            logger.error(error_msg)
            return False, self._get_default_browser_config(), error_msg

    def get_window_selection_info(self, platform_name):
        """
        Récupère les informations de sélection de fenêtre pour une plateforme

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            dict: Informations de sélection ou None si non trouvé
        """
        try:
            profile = self.get_platform(platform_name)
            if not profile:
                return None

            browser_config = profile.get('browser', {})

            return {
                'method': browser_config.get('window_selection_method', 'auto'),
                'order': browser_config.get('window_order', 1),
                'title_pattern': browser_config.get('window_title_pattern', ''),
                'position': browser_config.get('window_position'),
                'window_id': browser_config.get('window_id'),
                'remember_window': browser_config.get('remember_window', False)
            }

        except Exception as e:
            logger.error(f"Erreur récupération info sélection fenêtre {platform_name}: {str(e)}")
            return None

    def update_window_selection(self, platform_name, selection_info):
        """
        Met à jour les informations de sélection de fenêtre pour une plateforme

        Args:
            platform_name (str): Nom de la plateforme
            selection_info (dict): Nouvelles informations de sélection

        Returns:
            bool: True si mise à jour réussie
        """
        try:
            profile = self.get_platform(platform_name)
            if not profile:
                logger.error(f"Plateforme {platform_name} non trouvée pour mise à jour sélection fenêtre")
                return False

            # Mettre à jour la configuration navigateur
            browser_config = profile.get('browser', {})

            if 'method' in selection_info:
                browser_config['window_selection_method'] = selection_info['method']
            if 'order' in selection_info:
                browser_config['window_order'] = selection_info['order']
            if 'title_pattern' in selection_info:
                browser_config['window_title_pattern'] = selection_info['title_pattern']
            if 'position' in selection_info:
                browser_config['window_position'] = selection_info['position']
            if 'window_id' in selection_info:
                browser_config['window_id'] = selection_info['window_id']
            if 'remember_window' in selection_info:
                browser_config['remember_window'] = selection_info['remember_window']

            # Valider la configuration
            is_valid, normalized_config, error = self.validate_browser_config(browser_config)
            if not is_valid:
                logger.error(f"Configuration invalide: {error}")
                return False

            profile['browser'] = normalized_config

            # Sauvegarder
            return self.save_platform(platform_name, profile)

        except Exception as e:
            logger.error(f"Erreur mise à jour sélection fenêtre {platform_name}: {str(e)}")
            return False

    # =====================================================
    # MÉTHODES POUR GESTION DES PLATEFORMES (ENRICHIES)
    # =====================================================

    def save_platform(self, platform_name, profile_data):
        """
        Sauvegarde un profil de plateforme en base de données avec support multi-fenêtres

        Args:
            platform_name (str): Nom de la plateforme
            profile_data (dict): Données du profil à sauvegarder

        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        try:
            logger.debug(f"Sauvegarde plateforme {platform_name} en base de données")

            # Validation et normalisation de la configuration navigateur
            if 'browser' in profile_data:
                is_valid, normalized_browser, error = self.validate_browser_config(profile_data['browser'])
                if not is_valid:
                    logger.error(f"Configuration navigateur invalide pour {platform_name}: {error}")
                    return False
                profile_data['browser'] = normalized_browser
            else:
                # Ajouter configuration par défaut si absente
                profile_data['browser'] = self._get_default_browser_config()

            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            # Convertir le profil en JSON
            profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)

            # Vérifier si la plateforme existe déjà
            cursor.execute('SELECT id FROM platforms WHERE name = ?', (platform_name,))
            existing = cursor.fetchone()

            if existing:
                # Mettre à jour
                cursor.execute('''
                               UPDATE platforms
                               SET profile_data = ?,
                                   updated_at   = ?
                               WHERE name = ?
                               ''', (profile_json, now, platform_name))
                logger.info(f"Profil {platform_name} mis à jour en base de données")
            else:
                # Créer nouveau
                cursor.execute('''
                               INSERT INTO platforms (name, profile_data, created_at, updated_at)
                               VALUES (?, ?, ?, ?)
                               ''', (platform_name, profile_json, now, now))
                logger.info(f"Nouveau profil {platform_name} créé en base de données")

            self.conn.commit()

            # Vérification de la sauvegarde
            saved_profile = self.get_platform(platform_name)
            if saved_profile:
                logger.debug(f"Vérification sauvegarde {platform_name}: OK")
                return True
            else:
                logger.error(f"Échec vérification sauvegarde {platform_name}")
                return False

        except Exception as e:
            logger.error(f"Erreur sauvegarde plateforme {platform_name}: {str(e)}")
            return False

    def get_platform(self, platform_name):
        """
        Récupère un profil de plateforme depuis la base de données avec migration automatique

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            dict: Profil de la plateforme ou None si non trouvé
        """
        try:
            logger.debug(f"Récupération plateforme {platform_name} depuis la base de données")

            cursor = self.conn.cursor()

            cursor.execute('SELECT profile_data FROM platforms WHERE name = ?', (platform_name,))
            result = cursor.fetchone()

            if result:
                # Décoder le JSON
                profile_data = json.loads(result['profile_data'])

                # Migration automatique si nécessaire
                browser_config = profile_data.get('browser', {})
                if 'window_selection_method' not in browser_config:
                    logger.debug(f"Migration automatique du profil {platform_name}")
                    profile_data['browser'] = self._migrate_browser_config(browser_config)

                    # Sauvegarder la version migrée
                    self.save_platform(platform_name, profile_data)

                logger.debug(
                    f"Profil {platform_name} récupéré depuis la base (taille: {len(str(profile_data))} caractères)")

                return profile_data
            else:
                logger.debug(f"Profil {platform_name} non trouvé en base de données")
                return None

        except Exception as e:
            logger.error(f"Erreur récupération plateforme {platform_name}: {str(e)}")
            return None

    def get_all_platforms(self):
        """
        Récupère tous les profils de plateformes avec migration automatique

        Returns:
            dict: Dictionnaire des profils {nom: profil}
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT name, profile_data FROM platforms')
            results = cursor.fetchall()

            platforms = {}
            migration_needed = False

            for row in results:
                try:
                    platform_name = row['name']
                    profile_data = json.loads(row['profile_data'])

                    # Migration automatique si nécessaire
                    browser_config = profile_data.get('browser', {})
                    if 'window_selection_method' not in browser_config:
                        logger.debug(f"Migration automatique du profil {platform_name}")
                        profile_data['browser'] = self._migrate_browser_config(browser_config)
                        migration_needed = True

                        # Sauvegarder la version migrée
                        now = datetime.now().isoformat()
                        profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)
                        cursor.execute('''
                                       UPDATE platforms
                                       SET profile_data = ?,
                                           updated_at   = ?
                                       WHERE name = ?
                                       ''', (profile_json, now, platform_name))

                    platforms[platform_name] = profile_data

                except Exception as e:
                    logger.error(f"Erreur décodage profil {row['name']}: {str(e)}")

            if migration_needed:
                self.conn.commit()
                logger.info("Migration automatique effectuée lors de get_all_platforms")

            logger.debug(f"{len(platforms)} profils de plateformes récupérés")
            return platforms

        except Exception as e:
            logger.error(f"Erreur récupération tous les profils: {str(e)}")
            return {}

    def platform_exists(self, platform_name):
        """
        Vérifie si une plateforme existe

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            bool: True si la plateforme existe
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM platforms WHERE name = ?', (platform_name,))
            return cursor.fetchone() is not None

        except Exception as e:
            logger.error(f"Erreur vérification existence plateforme {platform_name}: {str(e)}")
            return False

    def was_platform_deleted(self, platform_name):
        """
        Vérifie si une plateforme a été délibérément supprimée

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            bool: True si la plateforme a été supprimée
        """
        # Pour l'instant, retourne toujours False
        return False

    def delete_platform(self, platform_name):
        """
        Supprime une plateforme de la base de données

        Args:
            platform_name (str): Nom de la plateforme

        Returns:
            bool: True si suppression réussie
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM platforms WHERE name = ?', (platform_name,))

            if cursor.rowcount > 0:
                self.conn.commit()
                logger.info(f"Plateforme {platform_name} supprimée de la base")
                return True
            else:
                logger.warning(f"Plateforme {platform_name} non trouvée pour suppression")
                return False

        except Exception as e:
            logger.error(f"Erreur suppression plateforme {platform_name}: {str(e)}")
            return False

    # =====================================================
    # MÉTHODES POUR GESTION DU CLAVIER (INCHANGÉES)
    # =====================================================

    def save_keyboard_config(self, config_data):
        """
        Sauvegarde la configuration du clavier

        Args:
            config_data (dict): Configuration du clavier

        Returns:
            bool: True si sauvegarde réussie
        """
        try:
            logger.debug("Sauvegarde configuration clavier")

            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            # Désactiver l'ancienne configuration
            cursor.execute('UPDATE keyboard_config SET is_active = 0 WHERE is_active = 1')

            # Insérer la nouvelle configuration
            cursor.execute('''
                           INSERT INTO keyboard_config (layout_type, key_delay, accent_delay, accent_method,
                                                        block_alt_tab, focus_lock, protection_timeout,
                                                        created_at, updated_at, is_active)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ''', (
                               config_data.get('layout', 'AZERTY (Français)'),
                               config_data.get('key_delay', 50),
                               config_data.get('accent_delay', 100),
                               config_data.get('accent_method', 'direct'),
                               config_data.get('block_alt_tab', True),
                               config_data.get('focus_lock', True),
                               config_data.get('protection_timeout', 30),
                               now, now, True
                           ))

            self.conn.commit()
            logger.info("Configuration clavier sauvegardée")
            return True

        except Exception as e:
            logger.error(f"Erreur sauvegarde configuration clavier: {str(e)}")
            return False

    def get_keyboard_config(self):
        """
        Récupère la configuration active du clavier

        Returns:
            dict: Configuration du clavier ou None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                           SELECT *
                           FROM keyboard_config
                           WHERE is_active = 1
                           ORDER BY updated_at DESC LIMIT 1
                           ''')

            result = cursor.fetchone()

            if result:
                config_data = {
                    'layout': result['layout_type'],
                    'key_delay': result['key_delay'],
                    'accent_delay': result['accent_delay'],
                    'accent_method': result['accent_method'],
                    'block_alt_tab': bool(result['block_alt_tab']),
                    'focus_lock': bool(result['focus_lock']),
                    'protection_timeout': result['protection_timeout'],
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at']
                }

                logger.debug("Configuration clavier récupérée")
                return config_data
            else:
                logger.debug("Aucune configuration clavier trouvée")
                return None

        except Exception as e:
            logger.error(f"Erreur récupération configuration clavier: {str(e)}")
            return None

    # =====================================================
    # MÉTHODES EXISTANTES (SESSIONS, PROMPTS, ETC.) - INCHANGÉES
    # =====================================================

    def create_session(self, platform_name):
        """
        Crée une nouvelle session pour une plateforme d'IA

        Args:
            platform_name (str): Nom de la plateforme d'IA

        Returns:
            int: ID de la session créée
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute('''
                           INSERT INTO ai_sessions (platform_name, session_date, status)
                           VALUES (?, ?, ?)
                           ''', (platform_name, now, 'active'))

            self.conn.commit()
            session_id = cursor.lastrowid

            logger.debug(f"Nouvelle session créée pour {platform_name}, ID: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"Erreur lors de la création de session: {str(e)}")
            raise DatabaseError(f"Échec de la création de session: {str(e)}")

    def record_prompt(self, session_id, content, token_count, operation_type):
        """
        Enregistre un prompt envoyé

        Args:
            session_id (int): ID de la session
            content (str): Contenu du prompt
            token_count (int): Nombre de tokens
            operation_type (str): Type d'opération (analyse, génération, annotation, brainstorming)

        Returns:
            int: ID du prompt enregistré
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute('''
                           INSERT INTO prompts (session_id, timestamp, content, token_count, operation_type)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (session_id, now, content, token_count, operation_type))

            # Mettre à jour les compteurs de la session
            cursor.execute('''
                           UPDATE ai_sessions
                           SET prompt_count = prompt_count + 1,
                               token_count  = token_count + ?
                           WHERE id = ?
                           ''', (token_count, session_id))

            self.conn.commit()
            prompt_id = cursor.lastrowid

            logger.debug(f"Prompt enregistré, ID: {prompt_id}")
            return prompt_id

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du prompt: {str(e)}")
            raise DatabaseError(f"Échec de l'enregistrement du prompt: {str(e)}")

    def record_response(self, prompt_id, content, status='success'):
        """
        Enregistre une réponse reçue

        Args:
            prompt_id (int): ID du prompt correspondant
            content (str): Contenu de la réponse
            status (str): Statut de la réponse ('success', 'error', etc.)

        Returns:
            int: ID de la réponse enregistrée
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute('''
                           INSERT INTO responses (prompt_id, timestamp, content, status)
                           VALUES (?, ?, ?, ?)
                           ''', (prompt_id, now, content, status))

            self.conn.commit()
            response_id = cursor.lastrowid

            logger.debug(f"Réponse enregistrée, ID: {response_id}")
            return response_id

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la réponse: {str(e)}")
            raise DatabaseError(f"Échec de l'enregistrement de la réponse: {str(e)}")

    def get_session_stats(self, platform_name=None, date_from=None, date_to=None):
        """
        Récupère les statistiques des sessions

        Args:
            platform_name (str, optional): Filtrer par plateforme
            date_from (str, optional): Date de début (format ISO)
            date_to (str, optional): Date de fin (format ISO)

        Returns:
            list: Liste des statistiques de session
        """
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM ai_sessions WHERE 1=1"
            params = []

            if platform_name:
                query += " AND platform_name = ?"
                params.append(platform_name)

            if date_from:
                query += " AND session_date >= ?"
                params.append(date_from)

            if date_to:
                query += " AND session_date <= ?"
                params.append(date_to)

            query += " ORDER BY session_date DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Convertir les résultats en dictionnaires
            stats = []
            for row in results:
                stats.append(dict(row))

            return stats

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            raise DatabaseError(f"Échec de la récupération des statistiques: {str(e)}")

    def record_dataset(self, name, dataset_type, format, item_count, filepath):
        """
        Enregistre un dataset généré

        Args:
            name (str): Nom du dataset
            dataset_type (str): Type de dataset
            format (str): Format du dataset (CSV, JSON, etc.)
            item_count (int): Nombre d'éléments
            filepath (str): Chemin vers le fichier

        Returns:
            int: ID du dataset enregistré
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute('''
                           INSERT INTO datasets (name, creation_date, type, format, item_count, filepath)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (name, now, dataset_type, format, item_count, filepath))

            self.conn.commit()
            dataset_id = cursor.lastrowid

            logger.debug(f"Dataset enregistré, ID: {dataset_id}")
            return dataset_id

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du dataset: {str(e)}")
            raise DatabaseError(f"Échec de l'enregistrement du dataset: {str(e)}")

    def create_brainstorming_session(self, name, ai_platforms, context):
        """
        Crée une nouvelle session de brainstorming

        Args:
            name (str): Nom de la session
            ai_platforms (list): Liste des plateformes d'IA participantes
            context (str): Contexte du brainstorming

        Returns:
            int: ID de la session créée
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            # Convertir la liste des plateformes en JSON
            platforms_json = json.dumps(ai_platforms)

            cursor.execute('''
                           INSERT INTO brainstorming_sessions (name, creation_date, ai_platforms, context, status)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (name, now, platforms_json, context, 'in_progress'))

            self.conn.commit()
            session_id = cursor.lastrowid

            logger.debug(f"Session de brainstorming créée, ID: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"Erreur lors de la création de session de brainstorming: {str(e)}")
            raise DatabaseError(f"Échec de la création de session de brainstorming: {str(e)}")

    def record_brainstorming_result(self, session_id, platform_name, solution, evaluations=None, final_score=None):
        """
        Enregistre un résultat de brainstorming

        Args:
            session_id (int): ID de la session
            platform_name (str): Nom de la plateforme d'IA
            solution (str): Solution proposée
            evaluations (dict, optional): Évaluations des autres IA
            final_score (int, optional): Score final

        Returns:
            int: ID du résultat enregistré
        """
        try:
            cursor = self.conn.cursor()

            # Convertir les évaluations en JSON si présentes
            evaluations_json = json.dumps(evaluations) if evaluations else None

            cursor.execute('''
                           INSERT INTO brainstorming_results (session_id, platform_name, solution, evaluations, final_score)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (session_id, platform_name, solution, evaluations_json, final_score))

            self.conn.commit()
            result_id = cursor.lastrowid

            logger.debug(f"Résultat de brainstorming enregistré, ID: {result_id}")
            return result_id

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du résultat: {str(e)}")
            raise DatabaseError(f"Échec de l'enregistrement du résultat: {str(e)}")

    def update_brainstorming_status(self, session_id, status):
        """
        Met à jour le statut d'une session de brainstorming

        Args:
            session_id (int): ID de la session
            status (str): Nouveau statut

        Returns:
            bool: True si la mise à jour est réussie, False sinon
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                           UPDATE brainstorming_sessions
                           SET status = ?
                           WHERE id = ?
                           ''', (status, session_id))

            self.conn.commit()

            logger.debug(f"Statut de la session {session_id} mis à jour: {status}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")
            raise DatabaseError(f"Échec de la mise à jour du statut: {str(e)}")