#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

from utils.logger import logger
from utils.exceptions import AnnotationError
from ui.localization.translator import tr


class AnnotationForm(QtWidgets.QWidget):
    """
    Widget pour l'annotation et la validation de données par IA
    """

    # Signaux
    annotation_started = pyqtSignal(int)
    annotation_completed = pyqtSignal(int)
    annotation_failed = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.conductor = None
        self.platforms = []
        self.current_task_id = None
        self.annotator = None

        # Couleurs du thème
        self.primary_color = "#A23B2D"  # Rouge brique
        self.secondary_color = "#D35A4A"  # Rouge brique clair
        self.background_color = "#F5F0EF"  # Beige clair
        self.text_color = "#333333"  # Gris foncé
        self.accent_color = "#E38272"  # Rose pâle

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
            border: 2px solid {self.primary_color};
            border-radius: 8px;
            margin-top: 20px;
            padding: 10px;
            background-color: white;
            font-weight: bold;
            color: {self.primary_color};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
        }}

        QPushButton {{
            background-color: {self.primary_color};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
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

        QComboBox {{
            padding: 8px;
            border: 2px solid {self.accent_color};
            border-radius: 6px;
            background-color: white;
            min-width: 120px;
        }}

        QComboBox:hover {{
            border: 2px solid {self.primary_color};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QTextEdit {{
            border: 2px solid {self.accent_color};
            border-radius: 6px;
            padding: 8px;
            background-color: white;
        }}

        QTextEdit:focus {{
            border: 2px solid {self.primary_color};
        }}

        QLineEdit {{
            border: 2px solid {self.accent_color};
            border-radius: 6px;
            padding: 8px;
            background-color: white;
        }}

        QLineEdit:focus {{
            border: 2px solid {self.primary_color};
        }}

        QTabWidget::pane {{
            border: 2px solid {self.accent_color};
            top: -1px;
            border-radius: 6px;
            background-color: white;
        }}

        QTabBar::tab {{
            background: #E8E0DF;
            border: 1px solid {self.accent_color};
            padding: 8px 20px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}

        QTabBar::tab:selected {{
            background: {self.primary_color};
            color: white;
            border-bottom-color: {self.primary_color};
        }}

        QTabBar::tab:hover {{
            background: {self.secondary_color};
            color: white;
        }}

        QTableWidget {{
            border: 2px solid {self.accent_color};
            border-radius: 6px;
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
            border: 2px solid {self.accent_color};
            border-radius: 6px;
            text-align: center;
            background-color: #F0F0F0;
        }}

        QProgressBar::chunk {{
            background-color: {self.primary_color};
            border-radius: 6px;
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
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # En-tête avec logo
        header_layout = QtWidgets.QHBoxLayout()

        # Logo
        logo_label = QtWidgets.QLabel()
        logo_path = os.path.join("ui", "resources", "icons", "logo")
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(logo_label)

        # Titre
        self.title_label = QtWidgets.QLabel(tr("annotation.title"))
        self.title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {self.primary_color};
            margin-left: 10px;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Splitter horizontal pour la configuration et les résultats
        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.accent_color}; }}")
        main_layout.addWidget(splitter)

        # Panneau de gauche : configuration
        config_widget = QtWidgets.QWidget()
        config_widget.setStyleSheet("background-color: transparent;")
        config_layout = QtWidgets.QVBoxLayout(config_widget)
        config_layout.setSpacing(15)

        # Groupe de configuration
        self.config_group = QtWidgets.QGroupBox(tr("annotation.configuration"))
        config_form = QtWidgets.QFormLayout(self.config_group)
        config_form.setSpacing(10)

        # Sélection du type d'annotation
        self.annotation_type = QtWidgets.QComboBox()
        self.annotation_type.addItem(tr("annotation.classification"), "classification")
        self.annotation_type.addItem(tr("annotation.entity_labeling"), "entity")
        self.annotation_type.addItem(tr("annotation.sentiment"), "sentiment")
        self.annotation_type.addItem(tr("annotation.summary"), "summary")
        self.annotation_type.addItem(tr("annotation.keyword_extraction"), "keywords")
        self.annotation_type.addItem(tr("annotation.custom"), "custom")
        config_form.addRow(tr("annotation.type"), self.annotation_type)

        # Sélection de la plateforme
        self.platform_combo = QtWidgets.QComboBox()
        self.platform_combo.setToolTip(tr("annotation.platform_tooltip"))
        config_form.addRow(tr("annotation.platform"), self.platform_combo)

        # Directives d'annotation
        self.label_directives = QtWidgets.QLabel(tr("annotation.guidelines"))
        self.label_directives.setStyleSheet("margin-top: 10px;")
        config_form.addRow(self.label_directives)

        self.guidelines_edit = QtWidgets.QTextEdit()
        self.guidelines_edit.setPlaceholderText(tr("annotation.guidelines_placeholder"))
        self.guidelines_edit.setMaximumHeight(100)
        config_form.addWidget(self.guidelines_edit)

        config_layout.addWidget(self.config_group)

        # Groupe de données
        self.data_group = QtWidgets.QGroupBox(tr("annotation.data_to_annotate"))
        data_layout = QtWidgets.QVBoxLayout(self.data_group)
        data_layout.setSpacing(10)

        # Options d'entrée
        input_layout = QtWidgets.QHBoxLayout()

        self.data_source = QtWidgets.QComboBox()
        self.data_source.addItem(tr("annotation.direct_text"), "direct")
        self.data_source.addItem(tr("annotation.text_file"), "file")
        self.data_source.addItem(tr("annotation.json_file"), "json")
        self.data_source.addItem(tr("annotation.csv_file"), "csv")
        self.data_source.currentIndexChanged.connect(self._on_data_source_changed)
        input_layout.addWidget(self.data_source)

        self.load_button = QtWidgets.QPushButton(tr("annotation.load"))
        self.load_button.clicked.connect(self._on_load_data)
        input_layout.addWidget(self.load_button)

        data_layout.addLayout(input_layout)

        # Zone de texte pour les données
        self.data_edit = QtWidgets.QTextEdit()
        self.data_edit.setPlaceholderText(tr("annotation.data_placeholder"))
        data_layout.addWidget(self.data_edit)

        config_layout.addWidget(self.data_group)

        # Boutons d'action
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(10)

        self.annotate_button = QtWidgets.QPushButton(tr("annotation.annotate"))
        self.annotate_button.setIcon(QtGui.QIcon())  # Ajouter une icône si disponible
        self.annotate_button.clicked.connect(self._on_annotate)
        actions_layout.addWidget(self.annotate_button)

        self.stop_button = QtWidgets.QPushButton(tr("annotation.stop"))
        self.stop_button.clicked.connect(self._on_stop)
        self.stop_button.setEnabled(False)
        actions_layout.addWidget(self.stop_button)

        self.export_button = QtWidgets.QPushButton(tr("annotation.export"))
        self.export_button.clicked.connect(self._on_export)
        self.export_button.setEnabled(False)
        actions_layout.addWidget(self.export_button)

        config_layout.addLayout(actions_layout)

        # Panneau de droite : résultats
        results_widget = QtWidgets.QWidget()
        results_widget.setStyleSheet("background-color: transparent;")
        results_layout = QtWidgets.QVBoxLayout(results_widget)
        results_layout.setSpacing(15)

        # Titre des résultats
        self.results_title = QtWidgets.QLabel(tr("annotation.results"))
        self.results_title.setAlignment(Qt.AlignCenter)
        self.results_title.setStyleSheet(f"""
            font-weight: bold;
            font-size: 16px;
            color: {self.primary_color};
            margin-bottom: 10px;
        """)
        results_layout.addWidget(self.results_title)

        # Onglets de résultats
        self.results_tabs = QtWidgets.QTabWidget()
        results_layout.addWidget(self.results_tabs)

        # Onglet texte
        text_tab = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text_tab)

        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setReadOnly(True)
        text_layout.addWidget(self.results_text)

        self.results_tabs.addTab(text_tab, tr("annotation.text"))

        # Onglet tableau
        table_tab = QtWidgets.QWidget()
        table_layout = QtWidgets.QVBoxLayout(table_tab)

        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels([
            tr("annotation.type"),
            tr("annotation.text"),
            tr("annotation.annotation")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        table_layout.addWidget(self.results_table)

        self.results_tabs.addTab(table_tab, tr("annotation.table"))

        # Onglet JSON
        json_tab = QtWidgets.QWidget()
        json_layout = QtWidgets.QVBoxLayout(json_tab)

        self.results_json = QtWidgets.QTextEdit()
        self.results_json.setReadOnly(True)
        self.results_json.setFont(QtGui.QFont("Courier New", 10))
        json_layout.addWidget(self.results_json)

        self.results_tabs.addTab(json_tab, tr("annotation.json"))

        # Statut
        status_layout = QtWidgets.QHBoxLayout()

        self.status_label = QtWidgets.QLabel(tr("annotation.status_ready"))
        self.status_label.setStyleSheet(f"color: {self.primary_color}; font-weight: bold;")
        status_layout.addWidget(self.status_label, 1)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar, 2)

        results_layout.addLayout(status_layout)

        # Ajouter les widgets au splitter
        splitter.addWidget(config_widget)
        splitter.addWidget(results_widget)

        # Définir les tailles initiales
        splitter.setSizes([300, 500])

        # Initialiser les états
        self._on_data_source_changed(0)

    def set_conductor(self, conductor):
        """
        Définit le chef d'orchestre

        Args:
            conductor: Instance du chef d'orchestre
        """
        self.conductor = conductor

        # Initialiser l'annotateur si disponible
        if hasattr(conductor, 'modules') and hasattr(conductor.modules, 'dataset_annotator'):
            self.annotator = conductor.modules.dataset_annotator
        else:
            # Tenter d'importer et d'initialiser manuellement
            try:
                from modules.dataset_annotation.annotator import DatasetAnnotator
                self.annotator = DatasetAnnotator(conductor, conductor.database)
                logger.info("Annotateur initialisé manuellement")
            except Exception as e:
                logger.error(f"Impossible d'initialiser l'annotateur: {str(e)}")

    def set_platforms(self, platforms):
        """
        Définit la liste des plateformes disponibles

        Args:
            platforms (list): Liste des plateformes
        """
        self.platforms = platforms

        # Mettre à jour le combo des plateformes
        self.platform_combo.clear()

        for platform in platforms:
            self.platform_combo.addItem(platform)

    def update_status(self, message, progress=None):
        """
        Met à jour le statut

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

    def new_annotation_task(self):
        """Initialise une nouvelle tâche d'annotation"""
        # Réinitialiser les champs
        self.guidelines_edit.clear()
        self.data_edit.clear()
        self.results_text.clear()
        self.results_json.clear()
        self.results_table.setRowCount(0)

        # Réinitialiser la tâche actuelle
        self.current_task_id = None

        # Mettre à jour le statut
        self.update_status(tr("annotation.new_task_created"))

        # Mettre à jour les boutons
        self.annotate_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.export_button.setEnabled(False)

    def load_file(self, file_path):
        """
        Charge un fichier pour annotation

        Args:
            file_path (str): Chemin du fichier
        """
        try:
            # Vérifier l'existence du fichier
            if not os.path.exists(file_path):
                QtWidgets.QMessageBox.warning(
                    self,
                    tr("annotation.file_not_found"),
                    tr("annotation.file_not_found_message", file=file_path)
                )
                return

            # Déterminer le type de fichier
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            # Charger selon le type
            if ext == '.json':
                # Fichier JSON
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Définir le texte et la source
                self.data_source.setCurrentIndex(2)  # JSON
                self.data_edit.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))

            elif ext == '.csv':
                # Fichier CSV
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Définir le texte et la source
                self.data_source.setCurrentIndex(3)  # CSV
                self.data_edit.setPlainText(content)

            else:
                # Fichier texte par défaut
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Définir le texte et la source
                self.data_source.setCurrentIndex(1)  # Fichier texte
                self.data_edit.setPlainText(content)

            # Mettre à jour le statut
            self.update_status(tr("annotation.file_loaded", file=os.path.basename(file_path)))

        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("annotation.load_error"),
                tr("annotation.load_error_message", error=str(e))
            )

    def save_annotations(self):
        """Enregistre les annotations actuelles"""
        # Vérifier si des annotations sont disponibles
        if self.results_text.toPlainText().strip() == "":
            QtWidgets.QMessageBox.warning(
                self,
                tr("annotation.no_annotation"),
                tr("annotation.no_annotation_message")
            )
            return

        # Ouvrir un sélecteur de fichier
        file_path, file_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            tr("annotation.save_annotations"),
            os.path.expanduser("~/annotations.json"),
            tr("annotation.save_dialog_filter")
        )

        if not file_path:
            return

        try:
            # Déterminer le format
            format_json = file_path.lower().endswith('.json')

            if format_json:
                # Récupérer le JSON des résultats
                json_content = self.results_json.toPlainText()

                # Vérifier si le JSON est valide
                try:
                    import json
                    json_data = json.loads(json_content)

                    # Sauvegarder le JSON formaté
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                except:
                    # Si le JSON n'est pas valide, sauvegarder le texte brut
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(json_content)
            else:
                # Sauvegarder le texte des résultats
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.toPlainText())

            # Mettre à jour le statut
            self.update_status(tr("annotation.saved", file=os.path.basename(file_path)))

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des annotations: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("annotation.save_error"),
                tr("annotation.save_error_message", error=str(e))
            )

    def export_annotations(self):
        """Exporte les annotations actuelles"""
        # Vérifier si des annotations sont disponibles
        if self.results_text.toPlainText().strip() == "":
            QtWidgets.QMessageBox.warning(
                self,
                tr("annotation.no_annotation"),
                tr("annotation.no_annotation_message")
            )
            return

        # Ouvrir un sélecteur de fichier
        file_path, file_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            tr("annotation.export_annotations"),
            os.path.expanduser("~/annotations_export.json"),
            tr("annotation.export_dialog_filter")
        )

        if not file_path:
            return

        try:
            # Déterminer le format
            if file_path.lower().endswith('.json'):
                # Exporter en JSON
                # Récupérer le JSON des résultats
                json_content = self.results_json.toPlainText()

                # Vérifier si le JSON est valide
                try:
                    import json
                    json_data = json.loads(json_content)

                    # Enrichir les métadonnées
                    export_data = {
                        'metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'annotation_type': self.annotation_type.currentData(),
                            'platform': self.platform_combo.currentText(),
                            'guidelines': self.guidelines_edit.toPlainText()
                        },
                        'annotations': json_data
                    }

                    # Sauvegarder le JSON enrichi
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                except:
                    # Si le JSON n'est pas valide, sauvegarder le texte brut
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(json_content)

            elif file_path.lower().endswith('.csv'):
                # Exporter en CSV
                import csv

                # Préparer les données du tableau
                rows = []
                headers = [tr("annotation.type"), tr("annotation.text"), tr("annotation.annotation")]

                # Ajouter les en-têtes
                rows.append(headers)

                # Ajouter les lignes
                for row in range(self.results_table.rowCount()):
                    row_data = []
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    rows.append(row_data)

                # Écrire le fichier CSV
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)

            else:
                # Exporter en texte
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Métadonnées
                    f.write(f"{tr('annotation.type')}: {self.annotation_type.currentText()}\n")
                    f.write(f"{tr('annotation.platform')}: {self.platform_combo.currentText()}\n")
                    f.write(f"{tr('annotation.date')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    # Directives
                    guidelines = self.guidelines_edit.toPlainText()
                    if guidelines:
                        f.write(f"{tr('annotation.guidelines')}:\n{guidelines}\n\n")

                    # Résultats
                    f.write(f"{tr('annotation.results')}:\n")
                    f.write(self.results_text.toPlainText())

            # Mettre à jour le statut
            self.update_status(tr("annotation.exported", file=os.path.basename(file_path)))

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des annotations: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("annotation.export_error"),
                tr("annotation.export_error_message", error=str(e))
            )

    def _on_data_source_changed(self, index):
        """
        Gère le changement de source de données

        Args:
            index (int): Index de la nouvelle source
        """
        # Mettre à jour l'interface selon la source
        source = self.data_source.currentData()

        if source == "direct":
            # Texte direct
            self.data_edit.setReadOnly(False)
            self.data_edit.setPlaceholderText(tr("annotation.data_placeholder"))
            self.load_button.setEnabled(False)
        elif source == "file":
            # Fichier texte
            self.data_edit.setReadOnly(True)
            self.data_edit.setPlaceholderText(tr("annotation.file_content_placeholder"))
            self.load_button.setEnabled(True)
        elif source == "json":
            # Fichier JSON
            self.data_edit.setReadOnly(True)
            self.data_edit.setPlaceholderText(tr("annotation.json_content_placeholder"))
            self.load_button.setEnabled(True)
        elif source == "csv":
            # Fichier CSV
            self.data_edit.setReadOnly(True)
            self.data_edit.setPlaceholderText(tr("annotation.csv_content_placeholder"))
            self.load_button.setEnabled(True)

    def _on_load_data(self):
        """Gère le chargement des données"""
        # Déterminer l'extension selon la source
        source = self.data_source.currentData()

        if source == "file":
            file_filter = tr("annotation.text_file_filter")
        elif source == "json":
            file_filter = tr("annotation.json_file_filter")
        elif source == "csv":
            file_filter = tr("annotation.csv_file_filter")
        else:
            return

        # Ouvrir un sélecteur de fichier
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            tr("annotation.load_file"),
            os.path.expanduser("~"),
            file_filter
        )

        if file_path:
            self.load_file(file_path)

    def _on_annotate(self):
        """Gère le démarrage de l'annotation"""
        # Vérifier la disponibilité du système
        if not self.conductor:
            QtWidgets.QMessageBox.warning(
                self,
                tr("annotation.system_unavailable"),
                tr("annotation.system_init_error")
            )
            return

        # Récupérer les paramètres
        annotation_type = self.annotation_type.currentData()
        platform = self.platform_combo.currentText()
        guidelines = self.guidelines_edit.toPlainText()
        data = self.data_edit.toPlainText()

        # Vérifier les données
        if not data:
            QtWidgets.QMessageBox.warning(
                self,
                tr("annotation.missing_data"),
                tr("annotation.data_required")
            )
            return

        # Confirmation
        reply = QtWidgets.QMessageBox.question(
            self,
            tr("annotation.start_annotation"),
            tr("annotation.start_confirmation", platform=platform),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return

        try:
            # Mettre à jour l'interface
            self.update_status(tr("annotation.in_progress"), 10)
            self.annotate_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            # Générer un ID de tâche
            self.current_task_id = int(datetime.now().timestamp())

            # Émettre le signal de démarrage
            self.annotation_started.emit(self.current_task_id)

            # Démarrer l'annotation en arrière-plan
            QtCore.QTimer.singleShot(100, lambda: self._execute_annotation(
                self.current_task_id, annotation_type, platform, guidelines, data
            ))

        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'annotation: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("annotation.start_error"),
                tr("annotation.start_error_message", error=str(e))
            )

            # Réinitialiser l'interface
            self.update_status(tr("annotation.error", error=str(e)))
            self.annotate_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def _execute_annotation(self, task_id, annotation_type, platform, guidelines, data):
        """
        Exécute une tâche d'annotation

        Args:
            task_id (int): ID de la tâche
            annotation_type (str): Type d'annotation
            platform (str): Plateforme à utiliser
            guidelines (str): Directives d'annotation
            data (str): Données à annoter
        """
        try:
            # Mise à jour du statut
            self.update_status(tr("annotation.running", platform=platform), 30)

            # Déterminer le mode d'annotation
            source_type = self.data_source.currentData()

            # Si l'annotateur est disponible, l'utiliser
            if self.annotator:
                # Déterminer la méthode d'annotation
                if source_type == "json" and self._is_json(data):
                    import json
                    result = self.annotator.annotate_structured(
                        json.loads(data),
                        annotation_type,
                        guidelines,
                        platform=platform
                    )
                elif source_type == "csv":
                    result = self.annotator.annotate_csv(
                        data,
                        annotation_type,
                        guidelines,
                        platform=platform
                    )
                else:
                    result = self.annotator.annotate_text(
                        data,
                        annotation_type,
                        guidelines,
                        platform=platform
                    )
            else:
                # Utiliser directement le chef d'orchestre
                # Construire un prompt d'annotation
                prompt = self._build_annotation_prompt(annotation_type, guidelines, data)

                # Envoyer le prompt
                result = self.conductor.send_prompt(
                    platform,
                    prompt,
                    mode="analyze",
                    sync=True,
                    timeout=60
                )

            # Vérifier si la tâche est toujours la même
            if task_id != self.current_task_id:
                logger.warning(f"Tâche {task_id} annulée ou remplacée")
                return

            # Mettre à jour l'interface
            self.update_status(tr("annotation.processing_results"), 70)

            # Traiter et afficher les résultats
            self._display_results(result)

            # Terminer
            self.update_status(tr("annotation.completed"), 100)
            QtCore.QTimer.singleShot(1000, lambda: self.update_status(tr("annotation.completed")))

            # Réactiver les contrôles
            self.annotate_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.export_button.setEnabled(True)

            # Émettre le signal de fin
            self.annotation_completed.emit(task_id)

        except Exception as e:
            logger.error(f"Erreur lors de l'annotation: {str(e)}")

            # Vérifier si la tâche est toujours la même
            if task_id != self.current_task_id:
                return

            # Mettre à jour le statut
            self.update_status(tr("annotation.error", error=str(e)))

            # Réactiver les contrôles
            self.annotate_button.setEnabled(True)
            self.stop_button.setEnabled(False)

            # Émettre le signal d'échec
            self.annotation_failed.emit(task_id, str(e))

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                tr("annotation.annotation_error"),
                tr("annotation.annotation_error_message", error=str(e))
            )

    def _build_annotation_prompt(self, annotation_type, guidelines, data):
        """
        Construit un prompt d'annotation

        Args:
            annotation_type (str): Type d'annotation
            guidelines (str): Directives d'annotation
            data (str): Données à annoter

        Returns:
            str: Prompt formaté
        """
        prompt = f"{tr('annotation.task')}: {annotation_type}\n\n"

        if guidelines:
            prompt += f"{tr('annotation.guidelines')}:\n{guidelines}\n\n"

        # Instructions selon le type
        if annotation_type == "classification":
            prompt += tr("annotation.classification_instructions") + "\n\n"
        elif annotation_type == "entity":
            prompt += tr("annotation.entity_instructions") + "\n\n"
        elif annotation_type == "sentiment":
            prompt += tr("annotation.sentiment_instructions") + "\n\n"
        elif annotation_type == "summary":
            prompt += tr("annotation.summary_instructions") + "\n\n"
        elif annotation_type == "keywords":
            prompt += tr("annotation.keywords_instructions") + "\n\n"
        else:
            prompt += tr("annotation.custom_instructions") + "\n\n"

        # Format de sortie demandé
        prompt += tr("annotation.output_format") + "\n\n"

        # Données à annoter
        prompt += tr("annotation.data_header") + "\n"
        prompt += data

        return prompt

    def _display_results(self, result):
        """
        Affiche les résultats d'annotation

        Args:
            result: Résultat de l'annotation
        """
        # Extraire la réponse
        response = None

        if isinstance(result, dict):
            if 'result' in result and 'response' in result['result']:
                response = result['result']['response']
            elif 'response' in result:
                response = result['response']
            elif 'annotations' in result:
                response = result

        if not response:
            raise AnnotationError(tr("annotation.no_valid_result"))

        # Mettre à jour l'onglet texte
        if isinstance(response, str):
            self.results_text.setPlainText(response)
        elif isinstance(response, dict):
            import json
            self.results_text.setPlainText(json.dumps(response, indent=2, ensure_ascii=False))

        # Mettre à jour l'onglet JSON
        try:
            # Convertir en JSON si c'est une chaîne
            json_data = response
            if isinstance(response, str):
                import json
                # Tenter de parser comme JSON
                json_data = json.loads(response)

            # Formater le JSON
            if isinstance(json_data, dict):
                import json
                json_text = json.dumps(json_data, indent=2, ensure_ascii=False)
                self.results_json.setPlainText(json_text)

                # Mettre à jour le tableau
                self._update_table_from_json(json_data)
            else:
                self.results_json.setPlainText(str(json_data))
        except:
            # Si ce n'est pas du JSON valide, afficher le texte brut
            self.results_json.setPlainText(str(response))

        # Mettre l'onglet JSON en avant
        self.results_tabs.setCurrentIndex(2)

    def _update_table_from_json(self, json_data):
        """
        Met à jour le tableau à partir des données JSON

        Args:
            json_data (dict): Données JSON
        """
        # Vider le tableau
        self.results_table.setRowCount(0)

        try:
            # Récupérer les annotations
            annotations = None

            if 'annotations' in json_data:
                annotations = json_data['annotations']
            elif 'results' in json_data:
                annotations = json_data['results']
            elif 'entities' in json_data:
                annotations = json_data['entities']
            elif isinstance(json_data, list):
                annotations = json_data

            if not annotations:
                return

            # Déterminer le type d'annotations
            if isinstance(annotations, list):
                # Liste d'annotations
                for annotation in annotations:
                    # Ajouter une ligne
                    row = self.results_table.rowCount()
                    self.results_table.insertRow(row)

                    # Type d'entité
                    entity_type = ""
                    if isinstance(annotation, dict):
                        entity_type = annotation.get('type', annotation.get('label', annotation.get('category', '')))

                    type_item = QtWidgets.QTableWidgetItem(str(entity_type))
                    self.results_table.setItem(row, 0, type_item)

                    # Texte
                    text = ""
                    if isinstance(annotation, dict):
                        text = annotation.get('text', annotation.get('content', annotation.get('value', '')))
                    elif isinstance(annotation, str):
                        text = annotation

                    text_item = QtWidgets.QTableWidgetItem(str(text))
                    self.results_table.setItem(row, 1, text_item)

                    # Annotation complète
                    annotation_text = str(annotation)
                    if isinstance(annotation, dict):
                        import json
                        annotation_text = json.dumps(annotation, ensure_ascii=False)

                    annotation_item = QtWidgets.QTableWidgetItem(annotation_text)
                    self.results_table.setItem(row, 2, annotation_item)

            elif isinstance(annotations, dict):
                # Dictionnaire d'annotations
                for key, value in annotations.items():
                    # Ajouter une ligne
                    row = self.results_table.rowCount()
                    self.results_table.insertRow(row)

                    # Type
                    type_item = QtWidgets.QTableWidgetItem(str(key))
                    self.results_table.setItem(row, 0, type_item)

                    # Texte (vide pour le dictionnaire)
                    text_item = QtWidgets.QTableWidgetItem("")
                    self.results_table.setItem(row, 1, text_item)

                    # Valeur
                    value_text = str(value)
                    if isinstance(value, (dict, list)):
                        import json
                        value_text = json.dumps(value, ensure_ascii=False)

                    value_item = QtWidgets.QTableWidgetItem(value_text)
                    self.results_table.setItem(row, 2, value_item)

            # Ajuster les colonnes
            self.results_table.resizeColumnsToContents()
            self.results_table.resizeRowsToContents()

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du tableau: {str(e)}")

    def _on_stop(self):
        """Arrête l'annotation en cours"""
        # Réinitialiser la tâche actuelle
        self.current_task_id = None

        # Mettre à jour l'interface
        self.update_status(tr("annotation.cancelled"))
        self.annotate_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _on_export(self):
        """Exporte les résultats"""
        self.export_annotations()

    def _is_json(self, text):
        """
        Vérifie si une chaîne est du JSON valide

        Args:
            text (str): Texte à vérifier

        Returns:
            bool: True si c'est du JSON valide
        """
        try:
            import json
            json.loads(text)
            return True
        except:
            return False

    def update_language(self):
        """Met à jour tous les textes après un changement de langue"""
        # Mettre à jour le titre
        self.title_label.setText(tr("annotation.title"))

        # Mettre à jour les GroupBox
        self.config_group.setTitle(tr("annotation.configuration"))
        self.data_group.setTitle(tr("annotation.data_to_annotate"))

        # Mettre à jour les boutons
        self.annotate_button.setText(tr("annotation.annotate"))
        self.stop_button.setText(tr("annotation.stop"))
        self.export_button.setText(tr("annotation.export"))
        self.load_button.setText(tr("annotation.load"))

        # Mettre à jour les labels
        self.label_directives.setText(tr("annotation.guidelines"))
        self.results_title.setText(tr("annotation.results"))

        # Mettre à jour les placeholders
        self.guidelines_edit.setPlaceholderText(tr("annotation.guidelines_placeholder"))
        self._on_data_source_changed(self.data_source.currentIndex())

        # Mettre à jour les onglets
        self.results_tabs.setTabText(0, tr("annotation.text"))
        self.results_tabs.setTabText(1, tr("annotation.table"))
        self.results_tabs.setTabText(2, tr("annotation.json"))

        # Mettre à jour le statut
        self.status_label.setText(tr("annotation.status_ready"))

        # Mettre à jour les en-têtes du tableau
        self.results_table.setHorizontalHeaderLabels([
            tr("annotation.type"),
            tr("annotation.text"),
            tr("annotation.annotation")
        ])

        # Mettre à jour le combo des types d'annotation
        current_index = self.annotation_type.currentIndex()
        self.annotation_type.setItemText(0, tr("annotation.classification"))
        self.annotation_type.setItemText(1, tr("annotation.entity_labeling"))
        self.annotation_type.setItemText(2, tr("annotation.sentiment"))
        self.annotation_type.setItemText(3, tr("annotation.summary"))
        self.annotation_type.setItemText(4, tr("annotation.keyword_extraction"))
        self.annotation_type.setItemText(5, tr("annotation.custom"))

        # Mettre à jour le combo des sources de données
        current_source_index = self.data_source.currentIndex()
        self.data_source.setItemText(0, tr("annotation.direct_text"))
        self.data_source.setItemText(1, tr("annotation.text_file"))
        self.data_source.setItemText(2, tr("annotation.json_file"))
        self.data_source.setItemText(3, tr("annotation.csv_file"))

        # Mettre à jour le tooltip de la plateforme
        self.platform_combo.setToolTip(tr("annotation.platform_tooltip"))