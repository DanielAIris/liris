import os
import json
import csv
import pandas as pd
from datetime import datetime
from utils.logger import logger
from utils.exceptions import ExportError


class DataExporter:
    """
    Classe pour exporter les données dans différents formats
    """

    def __init__(self, config_provider):
        """
        Initialise l'exportateur

        Args:
            config_provider: Fournisseur de configuration
        """
        self.config_provider = config_provider
        self.export_config = config_provider.get_export_config()
        self.export_dir = self.export_config['export_dir']

        # Créer le répertoire d'exportation s'il n'existe pas
        os.makedirs(self.export_dir, exist_ok=True)

        logger.info(f"Exportateur initialisé: {self.export_dir}")

    def export_brainstorming_results(self, session_data, solutions, format='json'):
        """
        Exporte les résultats d'une session de brainstorming

        Args:
            session_data (dict): Données de la session
            solutions (list): Liste des solutions
            format (str): Format d'exportation

        Returns:
            str: Chemin du fichier exporté
        """
        try:
            session_id = session_data.get('id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if format == 'json':
                filename = f"brainstorming_{session_id}_{timestamp}.json"
                filepath = os.path.join(self.export_dir, filename)

                export_data = {
                    'session': session_data,
                    'solutions': solutions,
                    'exported_at': datetime.now().isoformat()
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            elif format == 'csv':
                filename = f"brainstorming_{session_id}_{timestamp}.csv"
                filepath = os.path.join(self.export_dir, filename)

                # Créer un DataFrame pour l'exportation CSV
                rows = []
                for solution in solutions:
                    row = {
                        'platform': solution.get('platform'),
                        'content': solution.get('content', '').replace('\n', ' '),
                        'score': solution.get('score', ''),
                        'evaluations': json.dumps(solution.get('evaluations', {}))
                    }
                    rows.append(row)

                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')

            elif format == 'xlsx':
                filename = f"brainstorming_{session_id}_{timestamp}.xlsx"
                filepath = os.path.join(self.export_dir, filename)

                # Créer un DataFrame pour l'exportation Excel
                rows = []
                for solution in solutions:
                    row = {
                        'Platform': solution.get('platform'),
                        'Solution': solution.get('content', ''),
                        'Score': solution.get('score', ''),
                    }

                    # Ajouter les évaluations comme colonnes séparées
                    for evaluator, evaluation in solution.get('evaluations', {}).items():
                        row[f'Evaluation_{evaluator}'] = evaluation

                    rows.append(row)

                df = pd.DataFrame(rows)
                with pd.ExcelWriter(filepath) as writer:
                    df.to_excel(writer, sheet_name='Brainstorming', index=False)

                    # Ajouter une feuille avec les métadonnées
                    metadata_df = pd.DataFrame([session_data])
                    metadata_df.to_excel(writer, sheet_name='Session_Info', index=False)

            else:
                raise ExportError(f"Format non supporté: {format}")

            logger.info(f"Brainstorming exporté: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation du brainstorming: {str(e)}")
            raise ExportError(f"Échec de l'exportation: {str(e)}")

    def export_dataset(self, dataset_id, content, format='json'):
        """
        Exporte un dataset

        Args:
            dataset_id (int): ID du dataset
            content (dict): Contenu du dataset
            format (str): Format d'exportation

        Returns:
            str: Chemin du fichier exporté
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if format == 'json':
                filename = f"dataset_{dataset_id}_{timestamp}.json"
                filepath = os.path.join(self.export_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)

            elif format == 'csv':
                filename = f"dataset_{dataset_id}_{timestamp}.csv"
                filepath = os.path.join(self.export_dir, filename)

                if isinstance(content, list):
                    df = pd.DataFrame(content)
                    df.to_csv(filepath, index=False, encoding='utf-8')
                else:
                    raise ExportError("Le contenu doit être une liste pour l'exportation CSV")

            else:
                raise ExportError(f"Format non supporté: {format}")

            logger.info(f"Dataset {dataset_id} exporté: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation du dataset: {str(e)}")
            raise ExportError(f"Échec de l'exportation: {str(e)}")

    def export_prompt_history(self, prompts, format='json'):
        """
        Exporte l'historique des prompts

        Args:
            prompts (list): Liste des prompts
            format (str): Format d'exportation

        Returns:
            str: Chemin du fichier exporté
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if format == 'json':
                filename = f"prompt_history_{timestamp}.json"
                filepath = os.path.join(self.export_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(prompts, f, indent=2, ensure_ascii=False)

            elif format == 'csv':
                filename = f"prompt_history_{timestamp}.csv"
                filepath = os.path.join(self.export_dir, filename)

                df = pd.DataFrame(prompts)
                df.to_csv(filepath, index=False, encoding='utf-8')

            else:
                raise ExportError(f"Format non supporté: {format}")

            logger.info(f"Historique des prompts exporté: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation de l'historique: {str(e)}")
            raise ExportError(f"Échec de l'exportation: {str(e)}")