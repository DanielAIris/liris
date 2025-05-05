#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Liris/ui/widgets/brainstorming_panel.py
"""

import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

from utils.logger import logger
from utils.exceptions import BrainstormingError
from ui.localization.translator import tr


class BrainstormingPanel(QtWidgets.QWidget):
    """
    Widget pour les sessions de brainstorming multi-IA
    """

    # Signaux
    session_started = pyqtSignal(int)
    session_completed = pyqtSignal(int)
    session_failed = pyqtSignal(int, str)
    export_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.conductor = None
        self.platforms = []
        self.current_session_id = None
        self.orchestrator = None

        # Couleurs du thème (harmonisées avec MainWindow)
        self.primary_color = "#A23B2D"  # Rouge brique
        self.secondary_color = "#D35A4A"  # Rouge brique clair
        self.background_color = "#F9F6F6"  # Beige très clair
        self.text_color = "#333333"  # Gris foncé
        self.accent_color = "#E8E0DF"  # Gris clair pour les accents

        self._init_style()
        self._init_ui()

    def _init_style(self):
        """Configure le style global du widget"""
        stylesheet = f"""
        QWidget {{
            background-color: {self.background_color};
            color: {self.text_color};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}

        QGroupBox {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            margin-top: 1em;
            padding: 10px;
            background-color: white;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}

        QPushButton {{
            background-color: {self.primary_color};
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            font-weight: bold;
            min-width: 120px;
        }}

        QPushButton:hover {{
            background-color: {self.secondary_color};
        }}

        QPushButton:pressed {{
            background-color: #922E23;
        }}

        QPushButton:disabled {{
            background-color: #CCCCCC;
        }}

        QLineEdit {{
            padding: 8px;
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            background-color: white;
        }}

        QLineEdit:focus {{
            border: 2px solid {self.primary_color};
        }}

        QTextEdit {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }}

        QTextEdit:focus {{
            border: 2px solid {self.primary_color};
        }}

        QListWidget {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            background-color: white;
            selection-background-color: {self.primary_color};
            outline: none;
        }}

        QListWidget::item {{
            padding: 5px;
        }}

        QListWidget::item:selected {{
            background-color: {self.primary_color};
            color: white;
        }}

        QListWidget::item:hover {{
            background-color: {self.secondary_color};
            color: white;
        }}

        QListWidget::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid {self.accent_color};
        }}

        QListWidget::indicator:checked {{
            background-color: {self.primary_color};
            border: 1px solid {self.primary_color};
        }}

        QTabWidget::pane {{
            border: 1px solid {self.accent_color};
            top: -2px;
            border-radius: 4px;
            background-color: white;
        }}

        QTabBar::tab {{
            background: {self.accent_color};
            color: {self.text_color};
            border: 1px solid #C0C0C0;
            padding: 10px 25px;  
            margin-right: 2px;
            border-top-left-radius: 2px;
            border-top-right-radius: 2px;
            font-weight: bold;
            min-width: 150px;  
            font-size: 16px;
            min-height: 30px;
        }}

        QTabBar::tab:selected {{
            background: {self.primary_color};
            color: white;
            border-bottom: 1px solid white;
        }}

        QTabBar::tab:hover {{
            background: {self.secondary_color};
            color: white;
        }}

        QTableWidget {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            background-color: white;
            gridline-color: #E0E0E0;
        }}

        QTableWidget::item:selected {{
            background-color: {self.accent_color};
            color: white;
        }}

        QHeaderView::section {{
            background-color: {self.primary_color};
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}

        QProgressBar {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            text-align: center;
            background-color: #F0F0F0;
        }}

        QProgressBar::chunk {{
            background-color: {self.primary_color};
            border-radius: 4px;
        }}

        QLabel {{
            color: {self.text_color};
        }}
        """
        self.setStyleSheet(stylesheet)

    def _init_ui(self):
        """Configure l'interface utilisateur"""
        # Disposition principale
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # En-tête avec titre
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QtWidgets.QLabel(tr("brainstorming.title"))
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {self.primary_color};
            margin: 0;
            padding: 0;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Groupe pour les paramètres de session
        session_group = QtWidgets.QGroupBox(tr("brainstorming.session_params"))
        session_layout = QtWidgets.QFormLayout(session_group)
        session_layout.setSpacing(10)
        session_layout.setContentsMargins(10, 10, 10, 10)

        # Champ pour le nom de la session
        self.session_name_edit = QtWidgets.QLineEdit()
        self.session_name_edit.setPlaceholderText(tr("brainstorming.session_name_placeholder"))
        self.session_name_edit.setMaximumWidth(300)
        session_layout.addRow(tr("brainstorming.name"), self.session_name_edit)

        # Sélection des plateformes
        platform_label = QtWidgets.QLabel(tr("brainstorming.platforms"))
        session_layout.addRow(platform_label)

        self.platforms_list = QtWidgets.QListWidget()
        self.platforms_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.platforms_list.setMaximumHeight(120)
        session_layout.addWidget(self.platforms_list)

        # Champ pour le contexte/problème
        context_label = QtWidgets.QLabel(tr("brainstorming.context"))
        session_layout.addRow(context_label)

        self.context_edit = QtWidgets.QTextEdit()
        self.context_edit.setPlaceholderText(tr("brainstorming.context_placeholder"))
        self.context_edit.setMinimumHeight(100)
        session_layout.addWidget(self.context_edit)

        # Boutons d'action
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.start_button = QtWidgets.QPushButton(tr("brainstorming.start_session"))
        self.start_button.clicked.connect(self._on_start_session)
        buttons_layout.addWidget(self.start_button)

        self.view_results_button = QtWidgets.QPushButton(tr("brainstorming.view_results"))
        self.view_results_button.clicked.connect(self._on_view_results)
        self.view_results_button.setEnabled(False)
        buttons_layout.addWidget(self.view_results_button)

        self.export_button = QtWidgets.QPushButton(tr("brainstorming.export"))
        self.export_button.clicked.connect(self._on_export_results)
        self.export_button.setEnabled(False)
        buttons_layout.addWidget(self.export_button)

        session_layout.addRow("", buttons_layout)
        main_layout.addWidget(session_group)

        # Zone de résultats
        results_group = QtWidgets.QGroupBox(tr("brainstorming.results"))
        results_layout = QtWidgets.QVBoxLayout(results_group)
        results_layout.setSpacing(10)
        results_layout.setContentsMargins(10, 10, 10, 10)

        # Onglets pour les résultats
        self.results_tabs = QtWidgets.QTabWidget()
        results_layout.addWidget(self.results_tabs)

        # Tableau des solutions
        solutions_tab = QtWidgets.QWidget()
        solutions_layout = QtWidgets.QVBoxLayout(solutions_tab)
        solutions_layout.setContentsMargins(0, 0, 0, 0)

        self.solutions_table = QtWidgets.QTableWidget()
        self.solutions_table.setColumnCount(4)
        self.solutions_table.setHorizontalHeaderLabels([
            tr("brainstorming.platform"),
            tr("brainstorming.score"),
            tr("brainstorming.evaluations"),
            tr("brainstorming.solution")
        ])
        self.solutions_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.solutions_table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.solutions_table.verticalHeader().setVisible(False)
        solutions_layout.addWidget(self.solutions_table)

        # Connexion du double-clic
        self.solutions_table.cellDoubleClicked.connect(self._on_solution_double_clicked)

        self.results_tabs.addTab(solutions_tab, tr("brainstorming.solutions"))

        # Onglet de comparaison
        comparison_tab = QtWidgets.QWidget()
        comparison_layout = QtWidgets.QVBoxLayout(comparison_tab)
        comparison_layout.setContentsMargins(0, 0, 0, 0)

        self.comparison_view = QtWidgets.QTextEdit()
        self.comparison_view.setReadOnly(True)
        comparison_layout.addWidget(self.comparison_view)

        self.results_tabs.addTab(comparison_tab, tr("brainstorming.comparison"))

        # Onglet de visualisation
        viz_tab = QtWidgets.QWidget()
        viz_layout = QtWidgets.QVBoxLayout(viz_tab)
        viz_layout.setContentsMargins(0, 0, 0, 0)

        self.viz_view = QtWidgets.QLabel(tr("brainstorming.visualization"))
        self.viz_view.setAlignment(Qt.AlignCenter)
        self.viz_view.setStyleSheet(f"""
            color: {self.primary_color};
            font-size: 14px;
            font-weight: bold;
            padding: 20px;
        """)
        viz_layout.addWidget(self.viz_view)

        self.results_tabs.addTab(viz_tab, tr("brainstorming.visualization"))

        # Statut de la session
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QtWidgets.QLabel(tr("brainstorming.status_ready"))
        self.status_label.setStyleSheet(f"color: {self.primary_color}; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        results_layout.addLayout(status_layout)
        main_layout.addWidget(results_group)

    def set_conductor(self, conductor):
        """
        Définit le chef d'orchestre

        Args:
            conductor: Instance du chef d'orchestre
        """
        self.conductor = conductor

        # Initialiser l'orchestrateur de brainstorming si disponible
        if hasattr(conductor, 'modules') and hasattr(conductor.modules, 'brainstorming_orchestrator'):
            self.orchestrator = conductor.modules.brainstorming_orchestrator
        else:
            # Tenter d'importer et d'initialiser manuellement
            try:
                from modules.brainstorming.orchestrator import BrainstormingOrchestrator
                self.orchestrator = BrainstormingOrchestrator(conductor, conductor.database)
                logger.info("Orchestrateur de brainstorming initialisé manuellement")
            except Exception as e:
                logger.error(f"Impossible d'initialiser l'orchestrateur de brainstorming: {str(e)}")

    def set_platforms(self, platforms):
        """
        Définit la liste des plateformes disponibles

        Args:
            platforms (list): Liste des plateformes
        """
        self.platforms = platforms

        # Mettre à jour la liste des plateformes
        self.platforms_list.clear()

        for platform in platforms:
            item = QtWidgets.QListWidgetItem(platform)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.platforms_list.addItem(item)

    def update_status(self, message, progress=None):
        """
        Met à jour le statut de la session

        Args:
            message (str): Message de statut
            progress (int, optional): Valeur de progression
        """
        self.status_label.setText(message)

        if progress is not None:
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(False)

    def new_session(self):
        """Crée une nouvelle session"""
        # Réinitialiser les champs
        self.session_name_edit.clear()
        self.context_edit.clear()

        # Sélectionner toutes les plateformes
        for i in range(self.platforms_list.count()):
            item = self.platforms_list.item(i)
            item.setCheckState(Qt.Checked)

        # Réinitialiser les résultats
        self.clear_results()
        self.current_session_id = None

        # Mettre à jour les boutons
        self.view_results_button.setEnabled(False)
        self.export_button.setEnabled(False)

        # Mettre à jour le statut
        self.update_status(tr("brainstorming.new_session_created"))

    def clear_results(self):
        """Efface les résultats"""
        # Effacer le tableau des solutions
        self.solutions_table.setRowCount(0)

        # Effacer la comparaison
        self.comparison_view.clear()

        # Réinitialiser la visualisation
        self.viz_view.setText(tr("brainstorming.visualization"))

    def load_file(self, file_path):
        """
        Charge une session depuis un fichier

        Args:
            file_path (str): Chemin du fichier
        """
        try:
            # Vérifier l'extension
            if not file_path.lower().endswith(('.json', '.txt')):
                QtWidgets.QMessageBox.warning(
                    self,
                    tr("brainstorming.unsupported_format"),
                    tr("brainstorming.file_format_error")
                )
                return

            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Importer simplement le contenu dans le contexte
            self.context_edit.setPlainText(content)

            # Mettre à jour le nom de session
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            self.session_name_edit.setText(tr("brainstorming.session_from_file", file=file_name_without_ext))

            # Mettre à jour le statut
            self.update_status(tr("brainstorming.file_loaded", file=file_name))

        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("brainstorming.load_error"),
                tr("brainstorming.load_error_message", error=str(e))
            )

    def save_session(self):
        """Enregistre la session actuelle"""
        # Vérifier si une session est en cours
        if not self.current_session_id:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.no_session"),
                tr("brainstorming.no_session_active")
            )
            return

        # Ouvrir un sélecteur de fichier
        file_path, file_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            tr("brainstorming.save_session"),
            os.path.expanduser(f"~/session_{self.current_session_id}.json"),
            tr("brainstorming.save_dialog_filter")
        )

        if not file_path:
            return

        try:
            # Si l'orchestrateur est disponible, utiliser sa méthode d'exportation
            if self.orchestrator:
                # Créer un exportateur temporaire si nécessaire
                if not hasattr(self, 'exporter'):
                    from core.data.exporter import DataExporter
                    self.exporter = DataExporter(None)

                # Exporter les résultats
                format_type = 'json' if file_path.lower().endswith('.json') else 'text'
                self.orchestrator.export_results(self.current_session_id, self.exporter, format_type)

                # Message de confirmation
                QtWidgets.QMessageBox.information(
                    self,
                    tr("brainstorming.save_success"),
                    tr("brainstorming.save_success_message", file=file_path)
                )
            else:
                # Sauvegarde basique
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.context_edit.toPlainText())

                # Message de confirmation
                QtWidgets.QMessageBox.information(
                    self,
                    tr("brainstorming.save_success"),
                    tr("brainstorming.save_success_message", file=file_path)
                )

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la session: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("brainstorming.save_error"),
                tr("brainstorming.save_error_message", error=str(e))
            )

    def _on_start_session(self):
        """Démarre une session de brainstorming"""
        # Vérifier la disponibilité du système
        if not self.conductor or not self.orchestrator:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.system_unavailable"),
                tr("brainstorming.system_init_error")
            )
            return

        # Récupérer les paramètres
        session_name = self.session_name_edit.text().strip()
        if not session_name:
            session_name = tr("brainstorming.default_session_name", date=datetime.now().strftime('%Y-%m-%d %H:%M'))

        context = self.context_edit.toPlainText().strip()
        if not context:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.missing_context"),
                tr("brainstorming.context_required")
            )
            return

        # Récupérer les plateformes sélectionnées
        selected_platforms = []
        for i in range(self.platforms_list.count()):
            item = self.platforms_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_platforms.append(item.text())

        if not selected_platforms:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.missing_platforms"),
                tr("brainstorming.platforms_required")
            )
            return

        # Confirmation
        reply = QtWidgets.QMessageBox.question(
            self,
            tr("brainstorming.start_session"),
            tr("brainstorming.start_confirmation", count=len(selected_platforms)),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return

        try:
            # Créer la session
            session_id = self.orchestrator.create_session(
                session_name, context, selected_platforms
            )

            # Mettre à jour l'interface
            self.update_status(tr("brainstorming.session_created", id=session_id), 10)
            self.current_session_id = session_id

            # Désactiver les contrôles
            self.session_name_edit.setEnabled(False)
            self.context_edit.setEnabled(False)
            self.platforms_list.setEnabled(False)
            self.start_button.setEnabled(False)

            # Émettre le signal de démarrage
            self.session_started.emit(session_id)

            # Démarrer la session en arrière-plan
            QtCore.QTimer.singleShot(100, lambda: self._execute_session(session_id))

        except Exception as e:
            logger.error(f"Erreur lors de la création de la session: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("brainstorming.start_error"),
                tr("brainstorming.start_error_message", error=str(e))
            )

    def _execute_session(self, session_id):
        """
        Exécute une session de brainstorming

        Args:
            session_id (int): ID de la session
        """
        try:
            # Mettre à jour le statut
            self.update_status(tr("brainstorming.session_running", id=session_id), 20)

            # Démarrer la session
            self.orchestrator.start_session(session_id, sync=True, timeout=300)

            # Récupérer les résultats
            results = self.orchestrator.get_session_results(session_id)

            # Mettre à jour l'interface
            self.update_status(tr("brainstorming.session_completed", id=session_id), 100)

            # Réactiver les contrôles
            self.session_name_edit.setEnabled(True)
            self.context_edit.setEnabled(True)
            self.platforms_list.setEnabled(True)
            self.start_button.setEnabled(True)

            # Activer les boutons de résultat
            self.view_results_button.setEnabled(True)
            self.export_button.setEnabled(True)

            # Mettre à jour les résultats
            self._update_results(results)

            # Émettre le signal de fin
            self.session_completed.emit(session_id)

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la session: {str(e)}")

            # Mettre à jour le statut
            self.update_status(tr("brainstorming.error", error=str(e)))

            # Réactiver les contrôles
            self.session_name_edit.setEnabled(True)
            self.context_edit.setEnabled(True)
            self.platforms_list.setEnabled(True)
            self.start_button.setEnabled(True)

            # Émettre le signal d'échec
            self.session_failed.emit(session_id, str(e))

    def _update_results(self, results):
        """
        Met à jour l'interface avec les résultats

        Args:
            results (dict): Résultats de la session
        """
        # Vérifier les résultats
        if not results or 'solutions' not in results:
            self.update_status(tr("brainstorming.no_results"))
            return

        # Initialisation du modèle
        self.solutions_table.setRowCount(0)
        solutions = results.get('solutions', {})
        scores = results.get('final_scores', {})
        evaluations = results.get('evaluations', {})

        # Trier les solutions par score (si disponible)
        sorted_platforms = sorted(
            solutions.keys(),
            key=lambda p: scores.get(p, 0) if scores else 0,
            reverse=True
        )

        # Ajouter les solutions au tableau
        for i, platform in enumerate(sorted_platforms):
            solution_data = solutions[platform]

            # Vérifier si la solution est valide
            if not isinstance(solution_data, dict) or 'content' not in solution_data:
                continue

            # Récupérer le contenu
            content = solution_data.get('content', '')
            if not content:
                continue

            # Ajouter une ligne
            row = self.solutions_table.rowCount()
            self.solutions_table.insertRow(row)

            # Plateforme
            platform_item = QtWidgets.QTableWidgetItem(platform)
            platform_item.setFlags(platform_item.flags() & ~Qt.ItemIsEditable)
            self.solutions_table.setItem(row, 0, platform_item)

            # Score
            score = scores.get(platform, None)
            score_item = QtWidgets.QTableWidgetItem(str(score) if score is not None else "-")
            score_item.setTextAlignment(Qt.AlignCenter)
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)

            # Colorer en fonction du score
            if score is not None:
                if score >= 80:
                    score_item.setBackground(QtGui.QColor(200, 255, 200))  # Vert clair
                elif score >= 60:
                    score_item.setBackground(QtGui.QColor(255, 255, 200))  # Jaune clair
                elif score >= 40:
                    score_item.setBackground(QtGui.QColor(255, 235, 200))  # Orange clair
                else:
                    score_item.setBackground(QtGui.QColor(255, 200, 200))  # Rouge clair

            self.solutions_table.setItem(row, 1, score_item)

            # Évaluations
            eval_count = 0
            for eval_platform, evals in evaluations.items():
                if platform in evals:
                    eval_count += 1

            eval_item = QtWidgets.QTableWidgetItem(str(eval_count))
            eval_item.setTextAlignment(Qt.AlignCenter)
            eval_item.setFlags(eval_item.flags() & ~Qt.ItemIsEditable)
            self.solutions_table.setItem(row, 2, eval_item)

            # Solution (aperçu)
            preview = content[:100] + "..." if len(content) > 100 else content
            preview = preview.replace("\n", " ")

            solution_item = QtWidgets.QTableWidgetItem(preview)
            solution_item.setFlags(solution_item.flags() & ~Qt.ItemIsEditable)
            solution_item.setToolTip(content[:500] + "..." if len(content) > 500 else content)
            self.solutions_table.setItem(row, 3, solution_item)

        # Ajuster la hauteur des lignes
        self.solutions_table.resizeRowsToContents()

        # Mettre à jour la comparaison
        self._update_comparison(results)

        # Mettre à jour la visualisation
        self._update_visualization(results)

    def _update_comparison(self, results):
        """
        Met à jour la vue de comparaison

        Args:
            results (dict): Résultats de la session
        """
        # Vérifier les résultats
        if not results or 'solutions' not in results:
            self.comparison_view.clear()
            return

        # Préparer le texte de comparaison
        html = "<html><head><style>"
        html += "body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }"
        html += f"h2 {{ color: {self.primary_color}; font-size: 20px; margin-bottom: 15px; }}"
        html += f"h3 {{ color: {self.secondary_color}; font-size: 16px; margin-top: 20px; }}"
        html += "table { border-collapse: collapse; width: 100%; margin-top: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }"
        html += "th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }"
        html += f"th {{ background-color: {self.primary_color}; color: white; font-weight: bold; }}"
        html += "tr:hover { background-color: #f5f5f5; }"
        html += ".score-high { background-color: #d4edda; color: #155724; font-weight: bold; }"
        html += ".score-medium { background-color: #fff3cd; color: #856404; }"
        html += ".score-low { background-color: #f8d7da; color: #721c24; }"
        html += "p { line-height: 1.5; }"
        html += "</style></head><body>"

        # Titre
        session_name = results.get('name', f"Session {results.get('id', '')}")
        html += f"<h2>{session_name}</h2>"

        # Contexte
        context = results.get('context', '')
        if context:
            html += f"<h3>{tr('brainstorming.problem_context')}</h3>"
            html += f"<p>{context}</p>"

        # Tableau des scores
        solutions = results.get('solutions', {})
        scores = results.get('final_scores', {})

        if solutions:
            html += f"<h3>{tr('brainstorming.results')}</h3>"
            html += "<table>"
            html += f"<tr><th>{tr('brainstorming.platform')}</th><th>{tr('brainstorming.score')}</th><th>{tr('brainstorming.submission_date')}</th></tr>"

            # Trier par score
            sorted_platforms = sorted(
                solutions.keys(),
                key=lambda p: scores.get(p, 0) if scores else 0,
                reverse=True
            )

            for platform in sorted_platforms:
                solution_data = solutions[platform]

                # Vérifier si la solution est valide
                if not isinstance(solution_data, dict) or 'content' not in solution_data:
                    continue

                score = scores.get(platform, None)
                timestamp = solution_data.get('timestamp', '')

                # Formater la date
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass

                # Déterminer la classe CSS pour le score
                score_class = ""
                if score is not None:
                    if score >= 80:
                        score_class = "score-high"
                    elif score >= 60:
                        score_class = "score-medium"
                    else:
                        score_class = "score-low"

                html += f"<tr>"
                html += f"<td><b>{platform}</b></td>"
                html += f"<td class='{score_class}'>{score if score is not None else '-'}</td>"
                html += f"<td>{timestamp}</td>"
                html += f"</tr>"

            html += "</table>"

        # Résumé des évaluations
        evaluations = results.get('evaluations', {})

        if evaluations:
            html += f"<h3>{tr('brainstorming.evaluation_matrix')}</h3>"
            html += "<table>"

            # En-tête du tableau
            html += f"<tr><th>{tr('brainstorming.evaluator')} \\ {tr('brainstorming.solution')}</th>"
            for platform in sorted_platforms:
                html += f"<th>{platform}</th>"
            html += "</tr>"

            # Lignes du tableau (une par évaluateur)
            for evaluator in sorted(evaluations.keys()):
                html += f"<tr><td><b>{evaluator}</b></td>"

                eval_data = evaluations[evaluator]

                for platform in sorted_platforms:
                    if platform == evaluator:
                        html += "<td>-</td>"  # Pas d'auto-évaluation
                    elif platform in eval_data:
                        # Extraire le score de l'évaluation
                        eval_text = eval_data[platform]
                        score_match = QtCore.QRegExp(r"SCORE:\s*(\d+)/100").indexIn(eval_text)

                        if score_match >= 0:
                            captured_text = QtCore.QRegExp.capturedTexts()
                            if captured_text and len(captured_text) > 1:
                                eval_score = captured_text[1]
                                html += f"<td>{eval_score}/100</td>"
                            else:
                                html += f"<td>{tr('brainstorming.score_not_found')}</td>"
                        else:
                            html += f"<td>{tr('brainstorming.evaluation_present')}</td>"
                    else:
                        html += "<td>-</td>"

                html += "</tr>"

            html += "</table>"

        html += "</body></html>"

        # Mettre à jour la vue
        self.comparison_view.setHtml(html)

    def _update_visualization(self, results):
        """
        Met à jour la visualisation

        Args:
            results (dict): Résultats de la session
        """
        # À implémenter : graphiques de visualisation des résultats
        # Pour l'instant, afficher un message
        self.viz_view.setText(tr("brainstorming.visualization_coming_soon"))

    def _on_view_results(self):
        """Affiche les résultats détaillés"""
        # Vérifier si une session est active
        if not self.current_session_id:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.no_session"),
                tr("brainstorming.no_session_active")
            )
            return

        # Afficher l'onglet des résultats
        self.results_tabs.setCurrentIndex(0)

    def _on_export_results(self):
        """Exporte les résultats"""
        # Vérifier si une session est active
        if not self.current_session_id:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.no_session"),
                tr("brainstorming.no_session_active")
            )
            return

        # Émettre le signal d'exportation
        self.export_requested.emit(str(self.current_session_id))

        # Appeler la méthode d'exportation
        self.export_session()

    def export_session(self):
        """Exporte la session actuelle"""
        # Vérifier si une session est active
        if not self.current_session_id:
            QtWidgets.QMessageBox.warning(
                self,
                tr("brainstorming.no_session"),
                tr("brainstorming.no_session_active")
            )
            return

        # Ouvrir un sélecteur de fichier
        file_path, file_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            tr("brainstorming.export_results"),
            os.path.expanduser(f"~/brainstorming_{self.current_session_id}.json"),
            tr("brainstorming.export_dialog_filter")
        )

        if not file_path:
            return

        try:
            # Si l'orchestrateur est disponible, utiliser sa méthode d'exportation
            if self.orchestrator:
                # Créer un exportateur temporaire si nécessaire
                if not hasattr(self, 'exporter'):
                    from core.data.exporter import DataExporter
                    self.exporter = DataExporter(None)

                # Déterminer le format
                format_type = 'json'
                if file_path.lower().endswith('.txt'):
                    format_type = 'text'
                elif file_path.lower().endswith('.html'):
                    format_type = 'html'

                # Exporter les résultats
                export_path = self.orchestrator.export_results(
                    self.current_session_id,
                    self.exporter,
                    format_type
                )

                # Si le chemin d'exportation est différent, copier le fichier
                if export_path != file_path:
                    import shutil
                    shutil.copy2(export_path, file_path)

                # Message de confirmation
                QtWidgets.QMessageBox.information(
                    self,
                    tr("brainstorming.export_success"),
                    tr("brainstorming.export_success_message", file=file_path)
                )
            else:
                # Exportation basique
                session_results = None

                # Récupérer les résultats directement auprès du chef d'orchestre
                if self.conductor:
                    try:
                        # Tenter de récupérer les résultats via les méthodes disponibles
                        if hasattr(self.conductor, 'get_brainstorming_results'):
                            session_results = self.conductor.get_brainstorming_results(self.current_session_id)
                    except:
                        pass

                # Si aucun résultat, créer un objet simple
                if not session_results:
                    session_results = {
                        'id': self.current_session_id,
                        'name': self.session_name_edit.text(),
                        'context': self.context_edit.toPlainText(),
                        'timestamp': datetime.now().isoformat()
                    }

                # Enregistrer selon le format
                if file_path.lower().endswith('.json'):
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(session_results, f, ensure_ascii=False, indent=2)
                elif file_path.lower().endswith('.html'):
                    # Créer un HTML stylisé
                    html_content = f"""
                    <html>
                    <head>
                        <title>{tr('brainstorming.export_title')}</title>
                        <style>
                            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: {self.background_color}; }}
                            .container {{ max-width: 1000px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                            h1 {{ color: {self.primary_color}; font-size: 24px; margin-bottom: 15px; }}
                            h2 {{ color: {self.secondary_color}; font-size: 18px; margin-top: 20px; }}
                            pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>{tr('brainstorming.session_title', id=self.current_session_id)}</h1>
                            <h2>{self.session_name_edit.text()}</h2>
                            <h3>{tr('brainstorming.context')}</h3>
                            <pre>{self.context_edit.toPlainText()}</pre>
                        </div>
                    </body>
                    </html>
                    """
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    # Format texte par défaut
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(tr('brainstorming.session_title', id=self.current_session_id) + "\n")
                        f.write(tr('brainstorming.name') + ": " + self.session_name_edit.text() + "\n")
                        f.write(tr('brainstorming.date') + ": " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
                        f.write(tr('brainstorming.context') + ":\n")
                        f.write(f"{'=' * 80}\n")
                        f.write(self.context_edit.toPlainText())
                        f.write(f"\n{'=' * 80}\n")

                # Message de confirmation
                QtWidgets.QMessageBox.information(
                    self,
                    tr("brainstorming.export_success"),
                    tr("brainstorming.export_info_message", file=file_path)
                )

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("brainstorming.export_error"),
                tr("brainstorming.export_error_message", error=str(e))
            )

    def _on_solution_double_clicked(self, row, column):
        """
        Affiche la solution complète lors d'un double-clic

        Args:
            row (int): Index de ligne
            column (int): Index de colonne
        """
        # Vérifier si une session est active
        if not self.current_session_id or row < 0 or row >= self.solutions_table.rowCount():
            return

        # Récupérer la plateforme
        platform_item = self.solutions_table.item(row, 0)
        if not platform_item:
            return

        platform = platform_item.text()

        try:
            # Récupérer les résultats complets
            results = self.orchestrator.get_session_results(self.current_session_id)

            # Vérifier les solutions
            if not results or 'solutions' not in results:
                return

            solutions = results.get('solutions', {})
            evaluations = results.get('evaluations', {})

            # Vérifier si la solution existe
            if platform not in solutions:
                return

            solution_data = solutions[platform]

            # Vérifier si la solution est valide
            if not isinstance(solution_data, dict) or 'content' not in solution_data:
                return

            # Récupérer le contenu
            content = solution_data.get('content', '')

            # Construire le HTML pour afficher la solution
            html = "<html><head><style>"
            html += "body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: #F9F6F6; }"
            html += ".container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }"
            html += f"h1 {{ color: {self.primary_color}; font-size: 20px; margin-bottom: 15px; }}"
            html += f"h2 {{ color: {self.secondary_color}; font-size: 16px; margin-top: 20px; }}"
            html += "pre { background-color: #f5f5f5; padding: 10px; border-radius: 4px; white-space: pre-wrap; }"
            html += "blockquote { margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 5px solid #ccc; }"
            html += f".score-box {{ padding: 8px; border-radius: 4px; background-color: {self.accent_color}; color: white; font-weight: bold; display: inline-block; }}"
            html += "</style></head><body><div class='container'>"

            # Titre
            html += f"<h1>{tr('brainstorming.solution_from', platform=platform)}</h1>"

            # Score
            scores = results.get('final_scores', {})
            score = scores.get(platform, None)

            if score is not None:
                html += f"<div class='score-box'>{tr('brainstorming.final_score', score=score)}</div>"
                html += "<br><br>"

            # Solution
            html += f"<h2>{tr('brainstorming.proposed_solution')}</h2>"
            html += f"<pre>{content}</pre>"

            # Évaluations
            html += f"<h2>{tr('brainstorming.received_evaluations')}</h2>"

            eval_count = 0
            for evaluator, evals in evaluations.items():
                if platform in evals:
                    eval_text = evals[platform]
                    html += f"<h3>{tr('brainstorming.evaluation_by', evaluator=evaluator)}</h3>"
                    html += f"<blockquote>{eval_text}</blockquote>"
                    eval_count += 1

            if eval_count == 0:
                html += f"<p>{tr('brainstorming.no_evaluation')}</p>"

            html += "</div></body></html>"

            # Afficher la boîte de dialogue
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(tr('brainstorming.solution_from', platform=platform))
            dialog.setMinimumSize(600, 400)

            # Disposition
            layout = QtWidgets.QVBoxLayout(dialog)

            # Navigateur pour afficher le HTML
            browser = QtWidgets.QTextBrowser()
            browser.setHtml(html)
            layout.addWidget(browser)

            # Boutons
            button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Close
            )
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            # Afficher
            dialog.exec_()

        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la solution: {str(e)}")

    def update_language(self):
        """Met à jour tous les textes après un changement de langue"""
        # Mettre à jour le titre
        title_label = self.findChild(QtWidgets.QLabel)
        if title_label:
            title_label.setText(tr("brainstorming.title"))

        # Mettre à jour les GroupBox
        for group_box in self.findChildren(QtWidgets.QGroupBox):
            if "session_params" in group_box.objectName():
                group_box.setTitle(tr("brainstorming.session_params"))
            elif "results" in group_box.objectName():
                group_box.setTitle(tr("brainstorming.results"))

        # Mettre à jour les boutons
        self.start_button.setText(tr("brainstorming.start_session"))
        self.view_results_button.setText(tr("brainstorming.view_results"))
        self.export_button.setText(tr("brainstorming.export"))

        # Mettre à jour les onglets
        self.results_tabs.setTabText(0, tr("brainstorming.solutions"))
        self.results_tabs.setTabText(1, tr("brainstorming.comparison"))
        self.results_tabs.setTabText(2, tr("brainstorming.visualization"))

        # Mettre à jour les placeholders
        self.session_name_edit.setPlaceholderText(tr("brainstorming.session_name_placeholder"))
        self.context_edit.setPlaceholderText(tr("brainstorming.context_placeholder"))

        # Mettre à jour le statut
        self.status_label.setText(tr("brainstorming.status_ready"))

        # Mettre à jour la visualisation
        self.viz_view.setText(tr("brainstorming.visualization"))

        # Mettre à jour les headers du tableau
        self.solutions_table.setHorizontalHeaderLabels([
            tr("brainstorming.platform"),
            tr("brainstorming.score"),
            tr("brainstorming.evaluations"),
            tr("brainstorming.solution")
        ])