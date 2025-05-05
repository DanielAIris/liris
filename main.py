#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Liris/main.py
"""

import sys
import os
import traceback
import json
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QSettings, QTimer

from ui.widgets.brainstorming_panel import BrainstormingPanel
from ui.widgets.annotation_form import AnnotationForm
from ui.widgets.dataset_table import DatasetTable
from ui.widgets.prompt_list import PromptList

from core.orchestration.conductor import AIConductor
from core.data.database import Database
from core.data.exporter import DataExporter
from core.scheduling.scheduler import AIScheduler
from config.settings import ConfigProvider

from utils.logger import logger


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application d'IA collaborative
    """

    def __init__(self):
        print("=== DÉBUT - Initialisation de MainWindow ===")
        super().__init__()

        self.setWindowTitle("Liris - Plateforme d'IA Collaborative")
        self.setMinimumSize(1024, 768)

        # Définir le favicon (logo)
        logo_path = os.path.join("ui", "resources", "icons", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QtGui.QIcon(logo_path))

        # Couleurs du thème
        self.primary_color = "#A23B2D"  # Rouge brique
        self.secondary_color = "#D35A4A"  # Rouge brique clair
        self.background_color = "#F9F6F6"  # Beige très clair
        self.light_background = "#FFFFFF"  # Blanc pour la fenêtre principale
        self.text_color = "#333333"  # Gris foncé
        self.accent_color = "#E8E0DF"  # Gris clair pour les accents

        # Appliquer le style global
        self._init_style()

        # Initialiser les composants
        self._init_components()
        self._init_ui()
        self._init_menu()
        self._init_statusbar()
        self._init_connections()

        # Restaurer les paramètres
        self._restore_settings()

        # État initial
        self.conductor = None
        self.database = None
        self.exporter = None
        self.config_provider = None

        # Initialiser le système au démarrage
        QTimer.singleShot(100, self._init_system)

        # Journaliser le démarrage
        logger.info("Application démarrée")
        print("=== FIN - Initialisation de MainWindow ===")

    def _init_style(self):
        """Configure le style global de l'application"""
        stylesheet = f"""
        QMainWindow {{
            background-color: {self.light_background};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}

        QMenuBar {{
            background-color: {self.primary_color};
            color: white;
            padding: 5px;
            border: none;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 5px 15px;
            color: white;
        }}

        QMenuBar::item:selected {{
            background-color: {self.secondary_color};
        }}

        QMenu {{
            background-color: white;
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            color: {self.text_color};
        }}

        QMenu::item {{
            padding: 8px 30px;
        }}

        QMenu::item:selected {{
            background-color: {self.accent_color};
            color: {self.text_color};
        }}

        QMenu::separator {{
            height: 1px;
            background: {self.accent_color};
            margin: 5px 0;
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
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-weight: bold;
            min-width: 80px;
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

        QFrame {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            padding: 10px;
            background-color: white;
        }}

        QGroupBox {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            margin-top: 1em;
            padding-top: 10px;
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

        QLineEdit, QTextEdit, QComboBox {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            padding: 8px;
            background-color: white;
            selection-background-color: {self.primary_color};
            selection-color: white;
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {self.primary_color};
        }}

        QLabel {{
            color: {self.text_color};
        }}

        QStatusBar {{
            background-color: {self.background_color};
            border-top: 1px solid {self.accent_color};
            color: {self.text_color};
        }}

        QStatusBar QLabel {{
            color: {self.text_color};
            font-weight: bold;
            padding: 0 10px;
        }}

        QProgressBar {{
            border: 1px solid {self.accent_color};
            border-radius: 4px;
            text-align: center;
            background-color: #F0F0F0;
            font-weight: bold;
        }}

        QProgressBar::chunk {{
            background-color: {self.primary_color};
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(stylesheet)

    def _init_components(self):
        """Initialise les composants principaux"""
        print("   - Création des widgets principaux...")
        self.brainstorming_panel = BrainstormingPanel()
        self.annotation_form = AnnotationForm()
        self.dataset_table = DatasetTable()
        self.prompt_list = PromptList()

        # Barres de progression
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Widgets d'état
        self.status_label = QtWidgets.QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {self.primary_color}; font-weight: bold;")

        self.platform_label = QtWidgets.QLabel("Aucune plateforme")
        self.platform_label.setStyleSheet(f"color: {self.primary_color}; font-weight: bold;")

    def _init_ui(self):
        """Configure l'interface utilisateur"""
        # Widget central principal
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # En-tête simplifié
        header_widget = QtWidgets.QWidget()
        header_widget.setStyleSheet(f"""
            background-color: white;
            border-bottom: 2px solid {self.primary_color};
        """)
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 20, 30, 20)

        # Titre et sous-titre seulement (pas de logo dans l'interface)
        title_layout = QtWidgets.QVBoxLayout()

        title_label = QtWidgets.QLabel("Liris")
        title_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.primary_color};
            margin: 0;
            padding: 0;
        """)
        title_layout.addWidget(title_label)

        subtitle_label = QtWidgets.QLabel("Plateforme d'IA Collaborative")
        subtitle_label.setStyleSheet(f"""
            font-size: 16px;
            color: {self.secondary_color};
            margin: 0;
            padding: 0;
        """)
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Indicateur de statut système dans l'en-tête
        system_status_widget = QtWidgets.QWidget()
        system_status_layout = QtWidgets.QHBoxLayout(system_status_widget)
        system_status_layout.setContentsMargins(0, 0, 0, 0)

        self.connection_indicator = QtWidgets.QLabel()
        self.connection_indicator.setFixedSize(12, 12)
        self.connection_indicator.setStyleSheet("""
            background-color: #888888;
            border-radius: 6px;
        """)
        system_status_layout.addWidget(self.connection_indicator)

        self.connection_label = QtWidgets.QLabel("Système en attente")
        self.connection_label.setStyleSheet(f"color: {self.text_color}; margin-left: 5px;")
        system_status_layout.addWidget(self.connection_label)

        header_layout.addWidget(system_status_widget)

        main_layout.addWidget(header_widget)

        # Zone principale avec onglets
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(False)

        # Créer les onglets principaux
        self.tab_widget.addTab(self.brainstorming_panel, "Brainstorming")
        self.tab_widget.addTab(self.annotation_form, "Annotation")
        self.tab_widget.addTab(self.dataset_table, "Datasets")
        self.tab_widget.addTab(self.prompt_list, "Historique")

        # Configuration des onglets
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(False)

        # Changement d'onglet
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        main_layout.addWidget(self.tab_widget)

    def _init_menu(self):
        """Configure les menus"""
        # Menu principal
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")

        # Actions du menu Fichier
        new_action = QtWidgets.QAction("&Nouveau", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_file)
        file_menu.addAction(new_action)

        open_action = QtWidgets.QAction("&Ouvrir", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        save_action = QtWidgets.QAction("&Enregistrer", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_file)
        file_menu.addAction(save_action)

        export_action = QtWidgets.QAction("E&xporter", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QtWidgets.QAction("&Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Édition
        edit_menu = menubar.addMenu("&Édition")

        # Actions du menu Édition
        settings_action = QtWidgets.QAction("&Préférences", self)
        settings_action.triggered.connect(self._on_settings)
        edit_menu.addAction(settings_action)

        refresh_action = QtWidgets.QAction("&Actualiser", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._on_refresh)
        edit_menu.addAction(refresh_action)

        # Menu IA
        ai_menu = menubar.addMenu("&IA")

        # Actions du menu IA
        platforms_action = QtWidgets.QAction("&Plateformes", self)
        platforms_action.triggered.connect(self._on_show_platforms)
        ai_menu.addAction(platforms_action)

        test_action = QtWidgets.QAction("&Tester la connexion", self)
        test_action.triggered.connect(self._on_test_ai)
        ai_menu.addAction(test_action)

        ai_menu.addSeparator()

        compare_action = QtWidgets.QAction("&Comparer les résultats", self)
        compare_action.triggered.connect(self._on_compare_ai)
        ai_menu.addAction(compare_action)

        # Menu Aide
        help_menu = menubar.addMenu("&Aide")

        # Actions du menu Aide
        about_action = QtWidgets.QAction("&À propos", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        docs_action = QtWidgets.QAction("&Documentation", self)
        docs_action.triggered.connect(self._on_documentation)
        help_menu.addAction(docs_action)

    def _init_statusbar(self):
        """Configure la barre d'état"""
        statusbar = self.statusBar()
        statusbar.setStyleSheet(f"""
            QStatusBar {{
                border-top: 1px solid {self.accent_color};
                padding: 5px;
            }}
        """)

        # Ajouter les widgets à la barre d'état
        statusbar.addPermanentWidget(self.progress_bar, 1)
        statusbar.addWidget(self.status_label, 2)
        statusbar.addPermanentWidget(self.platform_label, 1)

        # Barre d'état initiale
        self.update_status("Application prête")

    def _init_connections(self):
        """Configure les connexions signal-slot entre widgets"""
        # Connexions du panel de brainstorming
        self.brainstorming_panel.session_started.connect(self._on_brainstorming_started)
        self.brainstorming_panel.session_completed.connect(self._on_brainstorming_completed)
        self.brainstorming_panel.session_failed.connect(self._on_brainstorming_failed)
        self.brainstorming_panel.export_requested.connect(self._on_export_data)

        # Connexions du formulaire d'annotation
        self.annotation_form.annotation_started.connect(self._on_annotation_started)
        self.annotation_form.annotation_completed.connect(self._on_annotation_completed)
        self.annotation_form.annotation_failed.connect(self._on_annotation_failed)

        # Connexions de la table de datasets
        self.dataset_table.dataset_selected.connect(self._on_dataset_selected)
        self.dataset_table.dataset_created.connect(self._on_dataset_created)
        self.dataset_table.dataset_deleted.connect(self._on_dataset_deleted)

        # Connexions de la liste de prompts
        self.prompt_list.prompt_selected.connect(self._on_prompt_selected)
        self.prompt_list.prompt_deleted.connect(self._on_prompt_deleted)

    def _restore_settings(self):
        """Restaure les paramètres utilisateur"""
        settings = QSettings("Liris", "IACollaborative")

        # Restaurer la géométrie et l'état de la fenêtre
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        if settings.contains("windowState"):
            self.restoreState(settings.value("windowState"))

        # Restaurer l'onglet actif
        if settings.contains("activeTab"):
            tab_index = int(settings.value("activeTab", 0))
            if 0 <= tab_index < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(tab_index)

        # Autres paramètres spécifiques aux widgets
        if settings.contains("lastExportPath"):
            self.last_export_path = settings.value("lastExportPath", os.path.expanduser("~"))
        else:
            self.last_export_path = os.path.expanduser("~")

    def _save_settings(self):
        """Sauvegarde les paramètres utilisateur"""
        settings = QSettings("Liris", "IACollaborative")

        # Sauvegarder la géométrie et l'état de la fenêtre
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        # Sauvegarder l'onglet actif
        settings.setValue("activeTab", self.tab_widget.currentIndex())

        # Autres paramètres spécifiques
        settings.setValue("lastExportPath", self.last_export_path)

    def _init_system(self):
        """Initialise le système d'IA et les composants principaux"""
        try:
            self.update_status("Initialisation du système...")
            self.update_connection_status("connecting")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)

            # Charger la configuration
            self.config_provider = ConfigProvider()
            self.progress_bar.setValue(20)

            # Initialiser la base de données
            db_config = self.config_provider.get_database_config()
            self.database = Database(db_config)
            self.database.connect()  # Remplacé initialize() par connect()
            self.progress_bar.setValue(40)

            # Initialiser l'exportateur
            self.exporter = DataExporter(self.config_provider)
            self.progress_bar.setValue(50)

            # Initialiser le scheduler
            scheduler_config = self.config_provider.get_scheduler_config()
            self.scheduler = AIScheduler(scheduler_config)
            self.progress_bar.setValue(70)

            # Initialiser le chef d'orchestre
            self.conductor = AIConductor(self.config_provider, self.scheduler, self.database)
            self.conductor.initialize()
            self.progress_bar.setValue(90)

            # Mettre à jour les widgets
            self._update_ui_with_system()
            self.progress_bar.setValue(100)

            # Terminer l'initialisation
            QTimer.singleShot(500, lambda: self.progress_bar.setVisible(False))
            self.update_status("Système initialisé")
            self.update_connection_status("connected")

        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système: {str(e)}")
            self.progress_bar.setVisible(False)
            self.update_status("Erreur d'initialisation")
            self.update_connection_status("error")

            # Afficher un message d'erreur
            QMessageBox.critical(
                self,
                "Erreur d'initialisation",
                f"Le système n'a pas pu être initialisé correctement.\n\n"
                f"Erreur: {str(e)}\n\n"
                f"Certaines fonctionnalités pourraient ne pas être disponibles."
            )

    def _update_ui_with_system(self):
        """Met à jour l'interface avec les informations du système"""
        if not self.conductor:
            return

        # Récupérer les plateformes disponibles
        platforms = self.conductor.get_available_platforms()

        # Mettre à jour l'étiquette de plateforme
        if platforms:
            self.platform_label.setText(f"{len(platforms)} plateformes disponibles")
        else:
            self.platform_label.setText("Aucune plateforme disponible")

        # Mettre à jour les widgets
        self.brainstorming_panel.set_conductor(self.conductor)
        self.brainstorming_panel.set_platforms(platforms)

        self.annotation_form.set_conductor(self.conductor)
        self.annotation_form.set_platforms(platforms)

        self.dataset_table.set_database(self.database)
        self.dataset_table.set_exporter(self.exporter)

        self.prompt_list.set_database(self.database)

        # Charger les données initiales
        self.prompt_list.refresh_list()
        self.dataset_table.refresh_list()

    def update_status(self, message):
        """
        Met à jour le message de la barre d'état

        Args:
            message (str): Nouveau message
        """
        self.status_label.setText(message)
        logger.debug(f"Statut: {message}")

    def update_connection_status(self, status):
        """
        Met à jour l'indicateur de connexion

        Args:
            status (str): 'connected', 'connecting', 'disconnected', 'error'
        """
        color_map = {
            'connected': '#4CAF50',
            'connecting': '#FFC107',
            'disconnected': '#9E9E9E',
            'error': '#F44336'
        }

        text_map = {
            'connected': 'Système connecté',
            'connecting': 'Connexion en cours...',
            'disconnected': 'Système déconnecté',
            'error': 'Erreur de connexion'
        }

        self.connection_indicator.setStyleSheet(f"""
            background-color: {color_map.get(status, '#9E9E9E')};
            border-radius: 6px;
        """)
        self.connection_label.setText(text_map.get(status, 'État inconnu'))

    def show_progress(self, value, max_value=100):
        """
        Affiche une progression dans la barre d'état

        Args:
            value (int): Valeur actuelle
            max_value (int): Valeur maximale
        """
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)

    def hide_progress(self):
        """Cache la barre de progression"""
        self.progress_bar.setVisible(False)

    def _on_tab_changed(self, index):
        """
        Gère le changement d'onglet

        Args:
            index (int): Index du nouvel onglet
        """
        # Mettre à jour le statut en fonction de l'onglet
        tab_name = self.tab_widget.tabText(index)
        self.update_status(f"Section: {tab_name}")

        # Actualiser l'onglet actif
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'refresh_list'):
            current_widget.refresh_list()

    def _on_new_file(self):
        """Gère la création d'un nouveau fichier"""
        # Déterminer l'action en fonction de l'onglet actif
        current_tab = self.tab_widget.currentWidget()

        if current_tab == self.brainstorming_panel:
            self.brainstorming_panel.new_session()
        elif current_tab == self.annotation_form:
            self.annotation_form.new_annotation_task()
        elif current_tab == self.dataset_table:
            self.dataset_table.new_dataset()

    def _on_open_file(self):
        """Gère l'ouverture d'un fichier"""
        # Ouvrir un sélecteur de fichier
        file_path, file_filter = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier",
            self.last_export_path,
            "Tous les fichiers (*.*);;Fichiers JSON (*.json);;Fichiers CSV (*.csv);;Fichiers texte (*.txt)"
        )

        if not file_path:
            return

        # Mettre à jour le chemin d'exportation
        self.last_export_path = os.path.dirname(file_path)

        # Déterminer l'action en fonction de l'onglet actif
        current_tab = self.tab_widget.currentWidget()

        if current_tab == self.brainstorming_panel:
            self.brainstorming_panel.load_file(file_path)
        elif current_tab == self.annotation_form:
            self.annotation_form.load_file(file_path)
        elif current_tab == self.dataset_table:
            self.dataset_table.import_dataset(file_path)

    def _on_save_file(self):
        """Gère l'enregistrement d'un fichier"""
        # Déterminer l'action en fonction de l'onglet actif
        current_tab = self.tab_widget.currentWidget()

        if current_tab == self.brainstorming_panel:
            self.brainstorming_panel.save_session()
        elif current_tab == self.annotation_form:
            self.annotation_form.save_annotations()
        elif current_tab == self.dataset_table:
            self.dataset_table.export_current()

    def _on_export_data(self):
        """Gère l'exportation des données"""
        # Déterminer l'action en fonction de l'onglet actif
        current_tab = self.tab_widget.currentWidget()

        if current_tab == self.brainstorming_panel:
            # Exporter la session de brainstorming actuelle
            if hasattr(self.brainstorming_panel, 'export_session'):
                self.brainstorming_panel.export_session()
        elif current_tab == self.annotation_form:
            # Exporter les annotations
            if hasattr(self.annotation_form, 'export_annotations'):
                self.annotation_form.export_annotations()
        elif current_tab == self.dataset_table:
            # Exporter le dataset sélectionné
            if hasattr(self.dataset_table, 'export_dataset'):
                self.dataset_table.export_dataset()
        elif current_tab == self.prompt_list:
            # Exporter l'historique des prompts
            if hasattr(self.prompt_list, 'export_history'):
                self.prompt_list.export_history()

    def _on_settings(self):
        """Ouvre la boîte de dialogue des préférences"""
        # TODO: Implémenter la boîte de dialogue des préférences
        QMessageBox.information(
            self,
            "Préférences",
            "La boîte de dialogue des préférences sera implémentée dans une prochaine version."
        )

    def _on_refresh(self):
        """Actualise les données"""
        # Actualiser l'onglet actif
        current_tab = self.tab_widget.currentWidget()

        if hasattr(current_tab, 'refresh_list'):
            current_tab.refresh_list()
        elif hasattr(current_tab, 'refresh'):
            current_tab.refresh()

        self.update_status("Données actualisées")

    def _on_show_platforms(self):
        """Affiche les plateformes d'IA disponibles"""
        if not self.conductor:
            QMessageBox.warning(
                self,
                "Plateformes IA",
                "Le système n'est pas encore initialisé."
            )
            return

        # Récupérer les plateformes
        platforms = self.conductor.get_available_platforms()

        if not platforms:
            QMessageBox.information(
                self,
                "Plateformes IA",
                "Aucune plateforme d'IA n'est actuellement disponible."
            )
            return

        # Construire le message
        message = "Plateformes d'IA disponibles:\n\n"

        for platform in platforms:
            message += f"• {platform}\n"

        # Afficher le message
        QMessageBox.information(
            self,
            "Plateformes IA",
            message
        )

    def _on_test_ai(self):
        """Teste la connexion avec les IA"""
        if not self.conductor:
            QMessageBox.warning(
                self,
                "Test de connexion",
                "Le système n'est pas encore initialisé."
            )
            return

        # Récupérer les plateformes
        platforms = self.conductor.get_available_platforms()

        if not platforms:
            QMessageBox.warning(
                self,
                "Test de connexion",
                "Aucune plateforme d'IA n'est actuellement disponible."
            )
            return

        # Afficher une boîte de dialogue de progression
        progress_dialog = QtWidgets.QProgressDialog(
            "Test des plateformes d'IA en cours...",
            "Annuler",
            0,
            len(platforms),
            self
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Test de connexion")
        progress_dialog.setValue(0)
        progress_dialog.show()

        # Tester chaque plateforme
        results = {}

        for i, platform in enumerate(platforms):
            if progress_dialog.wasCanceled():
                break

            progress_dialog.setValue(i)
            progress_dialog.setLabelText(f"Test de {platform} en cours...")

            try:
                # Prompt de test simple
                test_prompt = "Ceci est un test de connexion. Veuillez répondre avec 'OK'."

                # Envoyer le prompt
                result = self.conductor.send_prompt(
                    platform, test_prompt, mode="standard", sync=True, timeout=10
                )

                # Vérifier le résultat
                if result and 'result' in result and 'response' in result['result']:
                    response = result['result']['response']

                    if 'OK' in response:
                        results[platform] = True
                    else:
                        results[platform] = False
                else:
                    results[platform] = False

            except Exception as e:
                logger.error(f"Erreur lors du test de {platform}: {str(e)}")
                results[platform] = False

        # Fermer la boîte de dialogue
        progress_dialog.setValue(len(platforms))

        # Construire le message de résultat
        message = "Résultats des tests de connexion:\n\n"

        all_ok = True
        for platform, success in results.items():
            status = "✓ Succès" if success else "✗ Échec"
            message += f"• {platform}: {status}\n"

            if not success:
                all_ok = False

        # Afficher le message
        if all_ok:
            QMessageBox.information(
                self,
                "Test de connexion",
                message
            )
        else:
            QMessageBox.warning(
                self,
                "Test de connexion",
                message + "\n\nCertaines plateformes n'ont pas répondu correctement."
            )

    def _on_compare_ai(self):
        """Compare les résultats de différentes IA"""
        if not self.conductor:
            QMessageBox.warning(
                self,
                "Comparaison",
                "Le système n'est pas encore initialisé."
            )
            return

        # Récupérer les plateformes
        platforms = self.conductor.get_available_platforms()

        if len(platforms) < 2:
            QMessageBox.warning(
                self,
                "Comparaison",
                "Au moins deux plateformes d'IA sont nécessaires pour effectuer une comparaison."
            )
            return

        # Boîte de dialogue pour le prompt
        prompt, ok = QtWidgets.QInputDialog.getMultiLineText(
            self,
            "Comparaison d'IA",
            "Entrez un prompt à comparer entre les différentes plateformes:",
            ""
        )

        if not ok or not prompt:
            return

        # Afficher une boîte de dialogue de progression
        progress_dialog = QtWidgets.QProgressDialog(
            "Comparaison des plateformes d'IA en cours...",
            "Annuler",
            0,
            100,
            self
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Comparaison")
        progress_dialog.setValue(0)
        progress_dialog.show()

        # Lancer la comparaison
        try:
            # Mettre à jour la progression
            progress_dialog.setValue(10)

            # Exécuter la comparaison
            results = self.conductor.compare_responses(
                prompt,
                platforms=platforms,
                mode="standard",
                timeout=60
            )

            # Mettre à jour la progression
            progress_dialog.setValue(90)

            # Fermer la boîte de dialogue
            progress_dialog.setValue(100)

            # Afficher les résultats
            if not results:
                QMessageBox.warning(
                    self,
                    "Comparaison",
                    "Aucun résultat n'a été obtenu lors de la comparaison."
                )
                return

            # Créer une boîte de dialogue pour afficher les résultats
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Résultats de la comparaison")
            dialog.setMinimumSize(800, 600)

            # Disposition principale
            layout = QtWidgets.QVBoxLayout(dialog)

            # Prompt utilisé
            prompt_label = QtWidgets.QLabel(f"<b>Prompt utilisé:</b>")
            layout.addWidget(prompt_label)

            prompt_text = QtWidgets.QTextEdit()
            prompt_text.setPlainText(prompt)
            prompt_text.setReadOnly(True)
            prompt_text.setMaximumHeight(100)
            layout.addWidget(prompt_text)

            # Widget à onglets pour les résultats
            results_tabs = QtWidgets.QTabWidget()
            layout.addWidget(results_tabs)

            # Ajouter chaque résultat dans un onglet
            for platform, result in results.items():
                # Créer un widget pour le résultat
                result_widget = QtWidgets.QWidget()
                result_layout = QtWidgets.QVBoxLayout(result_widget)

                # État du résultat
                status = result.get('status', 'inconnu')
                status_label = QtWidgets.QLabel(f"<b>État:</b> {status}")
                result_layout.addWidget(status_label)

                # Durée
                duration = result.get('duration', 0)
                duration_label = QtWidgets.QLabel(f"<b>Durée:</b> {duration:.2f} secondes")
                result_layout.addWidget(duration_label)

                # Nombre de jetons
                tokens = result.get('token_count', 0)
                tokens_label = QtWidgets.QLabel(f"<b>Jetons:</b> {tokens}")
                result_layout.addWidget(tokens_label)

                # Réponse
                response_label = QtWidgets.QLabel("<b>Réponse:</b>")
                result_layout.addWidget(response_label)

                response_text = QtWidgets.QTextEdit()

                if status == 'completed' and 'result' in result and 'response' in result['result']:
                    response = result['result']['response']
                    response_text.setPlainText(response)
                else:
                    error = result.get('error', 'Pas de réponse')
                    response_text.setPlainText(f"Erreur: {error}")

                response_text.setReadOnly(True)
                result_layout.addWidget(response_text)

                # Ajouter l'onglet
                results_tabs.addTab(result_widget, platform)

            # Boutons
            button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Close
            )
            layout.addWidget(button_box)

            # Connexions
            button_box.rejected.connect(dialog.reject)
            button_box.accepted.connect(lambda: self._save_comparison_results(prompt, results))

            # Afficher la boîte de dialogue
            dialog.exec_()

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison: {str(e)}")

            # Fermer la boîte de dialogue de progression
            progress_dialog.close()

            # Afficher un message d'erreur
            QMessageBox.critical(
                self,
                "Erreur de comparaison",
                f"Une erreur est survenue lors de la comparaison:\n\n{str(e)}"
            )

    def _save_comparison_results(self, prompt, results):
        """
        Enregistre les résultats d'une comparaison

        Args:
            prompt (str): Prompt utilisé
            results (dict): Résultats par plateforme
        """
        # Ouvrir un sélecteur de fichier
        file_path, file_filter = QFileDialog.getSaveFileName(
            self,
            "Enregistrer les résultats",
            os.path.join(self.last_export_path, f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
            "Fichiers texte (*.txt);;Fichiers JSON (*.json);;Tous les fichiers (*.*)"
        )

        if not file_path:
            return

        # Mettre à jour le chemin d'exportation
        self.last_export_path = os.path.dirname(file_path)

        try:
            # Déterminer le format
            format_json = file_path.lower().endswith('.json')

            if format_json:
                # Format JSON
                export_data = {
                    'prompt': prompt,
                    'timestamp': datetime.now().isoformat(),
                    'results': {}
                }

                for platform, result in results.items():
                    if 'result' in result and 'response' in result['result']:
                        response = result['result']['response']
                    else:
                        response = None

                    export_data['results'][platform] = {
                        'status': result.get('status'),
                        'duration': result.get('duration'),
                        'token_count': result.get('token_count'),
                        'response': response,
                        'error': result.get('error')
                    }

                # Écrire le fichier JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                # Format texte
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"COMPARAISON DES PLATEFORMES D'IA\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    f.write(f"PROMPT UTILISÉ:\n")
                    f.write(f"{'=' * 80}\n")
                    f.write(prompt)
                    f.write(f"\n{'=' * 80}\n\n")

                    for platform, result in results.items():
                        f.write(f"RÉSULTAT DE {platform}:\n")
                        f.write(f"{'-' * 80}\n")

                        # Statut
                        status = result.get('status', 'inconnu')
                        f.write(f"État: {status}\n")

                        # Durée
                        duration = result.get('duration', 0)
                        f.write(f"Durée: {duration:.2f} secondes\n")

                        # Nombre de jetons
                        tokens = result.get('token_count', 0)
                        f.write(f"Jetons: {tokens}\n\n")

                        # Réponse
                        f.write(f"Réponse:\n")

                        if status == 'completed' and 'result' in result and 'response' in result['result']:
                            response = result['result']['response']
                            f.write(response)
                        else:
                            error = result.get('error', 'Pas de réponse')
                            f.write(f"Erreur: {error}")

                        f.write(f"\n{'=' * 80}\n\n")

            # Message de confirmation
            QMessageBox.information(
                self,
                "Sauvegarde réussie",
                f"Les résultats de la comparaison ont été enregistrés dans le fichier:\n{file_path}"
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des résultats: {str(e)}")

            # Message d'erreur
            QMessageBox.critical(
                self,
                "Erreur d'enregistrement",
                f"Une erreur est survenue lors de l'enregistrement des résultats:\n\n{str(e)}"
            )

    def _on_about(self):
        """Affiche la boîte de dialogue À propos"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("À propos de Liris")
        dialog.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Logo utilisé uniquement dans le dialogue "À propos"
        logo_label = QtWidgets.QLabel()
        logo_path = os.path.join("ui", "resources", "icons", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Si le logo n'est pas trouvé, afficher le texte
            logo_label.setText("LIRIS")
            logo_label.setStyleSheet(f"""
                font-size: 32px;
                font-weight: bold;
                color: {self.primary_color};
            """)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Texte
        text = QtWidgets.QLabel(
            "<h2>Liris - Plateforme d'IA Collaborative</h2>"
            "<p>Version 1.0.0</p>"
            "<p>Liris est une plateforme permettant de travailler avec plusieurs modèles "
            "d'intelligence artificielle de manière collaborative et comparative.</p>"
            "<p>© 2023 - Tous droits réservés</p>"
        )
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        layout.addWidget(text)

        # Bouton
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec_()

    def _on_documentation(self):
        """Ouvre la documentation"""
        # TODO: Implémenter l'ouverture de la documentation
        QMessageBox.information(
            self,
            "Documentation",
            "La documentation sera implémentée dans une prochaine version."
        )

    def _on_brainstorming_started(self, session_id):
        """
        Gère le démarrage d'une session de brainstorming

        Args:
            session_id (int): ID de la session
        """
        self.update_status(f"Session de brainstorming {session_id} démarrée")
        self.show_progress(0, 100)

    def _on_brainstorming_completed(self, session_id):
        """
        Gère la fin d'une session de brainstorming

        Args:
            session_id (int): ID de la session
        """
        self.update_status(f"Session de brainstorming {session_id} terminée")
        self.hide_progress()

    def _on_brainstorming_failed(self, session_id, error):
        """
        Gère l'échec d'une session de brainstorming

        Args:
            session_id (int): ID de la session
            error (str): Message d'erreur
        """
        self.update_status(f"Échec de la session de brainstorming {session_id}")
        self.hide_progress()

        # Afficher un message d'erreur
        QMessageBox.critical(
            self,
            "Échec du brainstorming",
            f"La session de brainstorming {session_id} a échoué.\n\n"
            f"Erreur: {error}"
        )

    def _on_annotation_started(self, task_id):
        """
        Gère le démarrage d'une tâche d'annotation

        Args:
            task_id (int): ID de la tâche
        """
        self.update_status(f"Tâche d'annotation {task_id} démarrée")
        self.show_progress(0, 100)

    def _on_annotation_completed(self, task_id):
        """
        Gère la fin d'une tâche d'annotation

        Args:
            task_id (int): ID de la tâche
        """
        self.update_status(f"Tâche d'annotation {task_id} terminée")
        self.hide_progress()

    def _on_annotation_failed(self, task_id, error):
        """
        Gère l'échec d'une tâche d'annotation

        Args:
            task_id (int): ID de la tâche
            error (str): Message d'erreur
        """
        self.update_status(f"Échec de la tâche d'annotation {task_id}")
        self.hide_progress()

        # Afficher un message d'erreur
        QMessageBox.critical(
            self,
            "Échec de l'annotation",
            f"La tâche d'annotation {task_id} a échoué.\n\n"
            f"Erreur: {error}"
        )

    def _on_dataset_selected(self, dataset_id):
        """
        Gère la sélection d'un jeu de données

        Args:
            dataset_id (int): ID du jeu de données
        """
        self.update_status(f"Jeu de données {dataset_id} sélectionné")

    def _on_dataset_created(self, dataset_id):
        """
        Gère la création d'un jeu de données

        Args:
            dataset_id (int): ID du jeu de données
        """
        self.update_status(f"Jeu de données {dataset_id} créé")

    def _on_dataset_deleted(self, dataset_id):
        """
        Gère la suppression d'un jeu de données

        Args:
            dataset_id (int): ID du jeu de données
        """
        self.update_status(f"Jeu de données {dataset_id} supprimé")

    def _on_prompt_selected(self, prompt_id):
        """
        Gère la sélection d'un prompt

        Args:
            prompt_id (int): ID du prompt
        """
        self.update_status(f"Prompt {prompt_id} sélectionné")

    def _on_prompt_deleted(self, prompt_id):
        """
        Gère la suppression d'un prompt

        Args:
            prompt_id (int): ID du prompt
        """
        self.update_status(f"Prompt {prompt_id} supprimé")

    def closeEvent(self, event):
        """
        Gère l'événement de fermeture de la fenêtre

        Args:
            event (QCloseEvent): Événement de fermeture
        """
        # Sauvegarder les paramètres
        self._save_settings()

        # Arrêter proprement le système
        if self.conductor:
            try:
                self.conductor.shutdown()
            except Exception as e:
                logger.error(f"Erreur lors de l'arrêt du système: {str(e)}")

        # Accepter l'événement
        event.accept()


def main():
    print("\n=== DÉMARRAGE DE L'APPLICATION ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Version PyQt5: {QtCore.QT_VERSION_STR}")
    print(f"Répertoire actuel: {os.getcwd()}")

    try:
        # Créer l'application
        print("1. Création de QApplication...")
        app = QApplication(sys.argv)
        print("   ✓ QApplication créée")

        # Créer la fenêtre principale
        print("2. Création de la fenêtre principale...")
        window = MainWindow()
        print("   ✓ Fenêtre principale créée")

        # Afficher la fenêtre
        print("3. Affichage de la fenêtre...")
        window.show()
        print("   ✓ Fenêtre affichée")

        # Démarrer la boucle d'événements
        print("4. Démarrage de la boucle d'événements...")
        print("=== APPLICATION EN COURS D'EXÉCUTION ===")
        sys.exit(app.exec_())

    except Exception as e:
        print(f"\n=== ERREUR CRITIQUE ===")
        print(f"Erreur: {str(e)}")
        traceback.print_exc()
        logger.critical(f"Erreur critique lors du démarrage: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()