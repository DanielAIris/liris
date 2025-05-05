import sqlite3
import os
from utils.logger import logger
from utils.exceptions import DatabaseError


class DatabaseMigration:
    """
    Classe pour gérer les migrations de schéma de base de données
    """

    def __init__(self, db_path):
        """
        Initialise le gestionnaire de migrations

        Args:
            db_path (str): Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        logger.info(f"Initialisation du gestionnaire de migrations pour {db_path}")

        # Table des versions pour suivre les migrations
        self._ensure_migrations_table()

    def _connect(self):
        """
        Établit une connexion à la base de données

        Returns:
            sqlite3.Connection: Objet de connexion
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Erreur de connexion pour migration: {str(e)}")
            raise DatabaseError(f"Échec de connexion pour migration: {str(e)}")

    def _ensure_migrations_table(self):
        """
        Crée la table des versions de migration si elle n'existe pas

        Returns:
            bool: True si l'opération est réussie
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS schema_migrations
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               version
                               INTEGER
                               NOT
                               NULL,
                               applied_at
                               TEXT
                               NOT
                               NULL,
                               description
                               TEXT
                           )
                           ''')

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la création de la table de migrations: {str(e)}")
            raise DatabaseError(f"Échec de la table de migrations: {str(e)}")

    def get_current_version(self):
        """
        Récupère la version actuelle du schéma

        Returns:
            int: Numéro de version ou 0 si aucune migration
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(version) as version FROM schema_migrations")
            result = cursor.fetchone()

            conn.close()

            if result and result['version'] is not None:
                return result['version']
            else:
                return 0

        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la version: {str(e)}")
            return 0

    def run_migration(self, version, queries, description=None):
        """
        Exécute une migration de schéma

        Args:
            version (int): Numéro de version
            queries (list): Liste des requêtes SQL à exécuter
            description (str, optional): Description de la migration

        Returns:
            bool: True si la migration est réussie
        """
        try:
            current_version = self.get_current_version()

            if version <= current_version:
                logger.debug(f"Migration {version} déjà appliquée, ignorée")
                return True

            conn = self._connect()
            cursor = conn.cursor()

            # Exécuter les requêtes
            for query in queries:
                cursor.execute(query)

            # Enregistrer la migration
            cursor.execute('''
                           INSERT INTO schema_migrations (version, applied_at, description)
                           VALUES (?, datetime('now'), ?)
                           ''', (version, description))

            conn.commit()
            conn.close()

            logger.info(f"Migration {version} appliquée avec succès")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la migration {version}: {str(e)}")
            raise DatabaseError(f"Échec de la migration {version}: {str(e)}")

    def migrate_to_latest(self, migrations):
        """
        Applique toutes les migrations nécessaires jusqu'à la dernière version

        Args:
            migrations (dict): Dictionnaire de migrations {version: {queries: [], description: ""}}

        Returns:
            int: Nombre de migrations appliquées
        """
        try:
            current_version = self.get_current_version()
            applied_count = 0

            # Trier les migrations par version
            versions = sorted(migrations.keys())

            for version in versions:
                if version > current_version:
                    migration = migrations[version]
                    self.run_migration(
                        version,
                        migration.get('queries', []),
                        migration.get('description', f"Migration vers v{version}")
                    )
                    applied_count += 1

            if applied_count > 0:
                logger.info(f"{applied_count} migration(s) appliquée(s)")
            else:
                logger.info("Base de données déjà à jour")

            return applied_count

        except Exception as e:
            logger.error(f"Erreur lors de la migration vers la dernière version: {str(e)}")
            raise DatabaseError(f"Échec des migrations: {str(e)}")

    def create_backup(self, backup_suffix=None):
        """
        Crée une sauvegarde de la base de données avant migration

        Args:
            backup_suffix (str, optional): Suffixe pour le nom du fichier

        Returns:
            str: Chemin du fichier de sauvegarde
        """
        import shutil
        from datetime import datetime

        try:
            if not os.path.exists(self.db_path):
                logger.warning("Pas de base de données à sauvegarder")
                return None

            # Générer le nom du fichier de sauvegarde
            if backup_suffix is None:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_path = f"{self.db_path}.bak_{backup_suffix}"

            # Copier le fichier
            shutil.copy2(self.db_path, backup_path)

            logger.info(f"Sauvegarde créée: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {str(e)}")
            return None