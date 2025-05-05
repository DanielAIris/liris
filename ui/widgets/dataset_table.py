import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

from utils.logger import logger


class DatasetTable(QtWidgets.QWidget):
    """
    Widget pour la gestion des datasets
    """

    # Signaux
    dataset_selected = pyqtSignal(int)
    dataset_created = pyqtSignal(int)
    dataset_deleted = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.database = None
        self.exporter = None
        self.current_dataset_id = None

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

        QLineEdit {{
            padding: 8px;
            border: 2px solid {self.accent_color};
            border-radius: 6px;
            background-color: white;
        }}

        QLineEdit:focus {{
            border: 2px solid {self.primary_color};
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

        QTableWidget {{
            border: 2px solid {self.accent_color};
            border-radius: 6px;
            background-color: white;
            gridline-color: #E0E0E0;
            alternate-background-color: #FAF7F6;
        }}

        QTableWidget::item {{
            padding: 5px;
        }}

        QTableWidget::item:selected {{
            background-color: {self.accent_color};
            color: white;
        }}

        QTableWidget::item:hover {{
            background-color: #F2E3E1;
        }}

        QHeaderView::section {{
            background-color: {self.primary_color};
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}

        QFrame[frameShape="4"] {{
            color: {self.accent_color};
        }}

        QLabel {{
            color: {self.text_color};
        }}

        QFormLayout QLabel {{
            font-weight: bold;
            color: {self.primary_color};
        }}

        QSplitter::handle {{
            background: {self.accent_color};
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
        title_label = QtWidgets.QLabel("Gestion des Datasets")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {self.primary_color};
            margin-left: 10px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Barre d'outils
        toolbar_layout = QtWidgets.QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.refresh_button = QtWidgets.QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.refresh_list)
        toolbar_layout.addWidget(self.refresh_button)

        self.new_button = QtWidgets.QPushButton("Nouveau dataset")
        self.new_button.clicked.connect(self.new_dataset)
        toolbar_layout.addWidget(self.new_button)

        self.import_button = QtWidgets.QPushButton("Importer")
        self.import_button.clicked.connect(self._on_import)
        toolbar_layout.addWidget(self.import_button)

        self.export_button = QtWidgets.QPushButton("Exporter")
        self.export_button.clicked.connect(self._on_export)
        self.export_button.setEnabled(False)
        toolbar_layout.addWidget(self.export_button)

        self.delete_button = QtWidgets.QPushButton("Supprimer")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()
        # Ajouter la barre d'outils
        main_layout.addLayout(toolbar_layout)

        # Séparateur
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)

        # Splitter principal
        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        main_layout.addWidget(splitter)

        # Panneau de gauche: liste des datasets
        list_widget = QtWidgets.QWidget()
        list_widget.setStyleSheet("background-color: transparent;")
        list_layout = QtWidgets.QVBoxLayout(list_widget)
        list_layout.setSpacing(15)

        # Titre
        list_title = QtWidgets.QLabel("Datasets disponibles")
        list_title.setAlignment(Qt.AlignCenter)
        list_title.setStyleSheet(f"""
            font-weight: bold;
            font-size: 16px;
            color: {self.primary_color};
            margin-bottom: 10px;
        """)
        list_layout.addWidget(list_title)

        # Filtre de recherche
        search_layout = QtWidgets.QHBoxLayout()

        search_label = QtWidgets.QLabel("Rechercher:")
        search_label.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(search_label)

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Filtrer par nom...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_edit)

        list_layout.addLayout(search_layout)

        # Tableau des datasets
        self.datasets_table = QtWidgets.QTableWidget()
        self.datasets_table.setColumnCount(3)
        self.datasets_table.setHorizontalHeaderLabels(["ID", "Nom", "Date"])
        self.datasets_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.datasets_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.datasets_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.datasets_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.datasets_table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.datasets_table.verticalHeader().setVisible(False)
        self.datasets_table.setAlternatingRowColors(True)

        # Connexion de la sélection
        self.datasets_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.datasets_table.cellDoubleClicked.connect(self._on_dataset_double_clicked)

        list_layout.addWidget(self.datasets_table)

        # Panneau de droite: détails du dataset
        details_widget = QtWidgets.QWidget()
        details_widget.setStyleSheet("background-color: transparent;")
        details_layout = QtWidgets.QVBoxLayout(details_widget)
        details_layout.setSpacing(15)

        # Titre
        details_title = QtWidgets.QLabel("Détails du dataset")
        details_title.setAlignment(Qt.AlignCenter)
        details_title.setStyleSheet(f"""
            font-weight: bold;
            font-size: 16px;
            color: {self.primary_color};
            margin-bottom: 10px;
        """)
        details_layout.addWidget(details_title)

        # Formulaire de détails
        details_form = QtWidgets.QFormLayout()
        details_form.setSpacing(10)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setReadOnly(True)
        details_form.addRow("Nom:", self.name_edit)

        self.date_edit = QtWidgets.QLineEdit()
        self.date_edit.setReadOnly(True)
        details_form.addRow("Date:", self.date_edit)

        self.size_edit = QtWidgets.QLineEdit()
        self.size_edit.setReadOnly(True)
        details_form.addRow("Taille:", self.size_edit)

        self.format_edit = QtWidgets.QLineEdit()
        self.format_edit.setReadOnly(True)
        details_form.addRow("Format:", self.format_edit)

        description_label = QtWidgets.QLabel("Description:")
        description_label.setStyleSheet("margin-top: 10px;")
        details_form.addRow(description_label)

        self.description_edit = QtWidgets.QTextEdit()
        self.description_edit.setReadOnly(True)
        self.description_edit.setMaximumHeight(100)
        details_form.addWidget(self.description_edit)

        details_layout.addLayout(details_form)

        # Aperçu des données
        preview_label = QtWidgets.QLabel("Aperçu des données")
        preview_label.setStyleSheet(f"""
            font-weight: bold;
            color: {self.primary_color};
            margin-top: 15px;
        """)
        details_layout.addWidget(preview_label)

        self.preview_edit = QtWidgets.QTextEdit()
        self.preview_edit.setReadOnly(True)
        details_layout.addWidget(self.preview_edit)

        # Boutons d'action
        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.setSpacing(10)

        self.view_button = QtWidgets.QPushButton("Voir les données")
        self.view_button.clicked.connect(self._on_view_data)
        self.view_button.setEnabled(False)
        actions_layout.addWidget(self.view_button)

        self.edit_button = QtWidgets.QPushButton("Modifier")
        self.edit_button.clicked.connect(self._on_edit_dataset)
        self.edit_button.setEnabled(False)
        actions_layout.addWidget(self.edit_button)

        details_layout.addLayout(actions_layout)

        # Ajouter les widgets au splitter
        splitter.addWidget(list_widget)
        splitter.addWidget(details_widget)

        # Définir les tailles initiales
        splitter.setSizes([300, 500])

        # Statut
        status_layout = QtWidgets.QHBoxLayout()

        self.status_label = QtWidgets.QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {self.primary_color}; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        main_layout.addLayout(status_layout)

    def set_database(self, database):
        """
        Définit la connexion à la base de données

        Args:
            database: Instance de la base de données
        """
        self.database = database

    def set_exporter(self, exporter):
        """
        Définit l'exportateur de données

        Args:
            exporter: Instance de l'exportateur
        """
        self.exporter = exporter

    def update_status(self, message):
        """
        Met à jour le statut

        Args:
            message (str): Message de statut
        """
        self.status_label.setText(message)

    def refresh_list(self):
        """Actualise la liste des datasets"""
        # Vérifier la disponibilité de la base de données
        if not self.database:
            self.update_status("Base de données non disponible")
            return

        try:
            # Effacer la sélection actuelle
            self.current_dataset_id = None
            self.datasets_table.clearSelection()

            # Effacer le tableau
            self.datasets_table.setRowCount(0)

            # Récupérer la liste des datasets
            datasets = self.database.get_all_datasets()

            if not datasets:
                self.update_status("Aucun dataset disponible")
                return

            # Filtre de recherche
            search_text = self.search_edit.text().lower()

            # Remplir le tableau
            for dataset in datasets:
                # Filtrer selon la recherche
                if search_text and search_text not in dataset.get('name', '').lower():
                    continue

                # Ajouter une ligne
                row = self.datasets_table.rowCount()
                self.datasets_table.insertRow(row)

                # ID
                id_item = QtWidgets.QTableWidgetItem(str(dataset.get('id', '')))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.datasets_table.setItem(row, 0, id_item)

                # Nom
                name_item = QtWidgets.QTableWidgetItem(dataset.get('name', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.datasets_table.setItem(row, 1, name_item)

                # Date
                date_str = dataset.get('created_at', '')
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str)
                        date_str = date.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass

                date_item = QtWidgets.QTableWidgetItem(date_str)
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.datasets_table.setItem(row, 2, date_item)

            # Mettre à jour le statut
            self.update_status(f"{self.datasets_table.rowCount()} datasets affichés")

        except Exception as e:
            logger.error(f"Erreur lors de l'actualisation de la liste: {str(e)}")
            self.update_status(f"Erreur: {str(e)}")

    def _on_search_changed(self, text):
        """
        Gère le changement du filtre de recherche

        Args:
            text (str): Texte de recherche
        """
        self.refresh_list()

    def _on_selection_changed(self):
        """Gère le changement de sélection"""
        # Récupérer les indices sélectionnés
        selected_rows = self.datasets_table.selectionModel().selectedRows()

        if not selected_rows:
            # Aucune sélection
            self.current_dataset_id = None
            self._clear_details()
            self.export_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.view_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            return

        # Récupérer l'ID du dataset sélectionné
        row = selected_rows[0].row()
        id_item = self.datasets_table.item(row, 0)

        if not id_item:
            return

        dataset_id = int(id_item.text())
        self.current_dataset_id = dataset_id

        # Activer les boutons
        self.export_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.view_button.setEnabled(True)
        self.edit_button.setEnabled(True)

        # Charger les détails
        self._load_dataset_details(dataset_id)

        # Émettre le signal
        self.dataset_selected.emit(dataset_id)

    def _clear_details(self):
        """Efface les détails affichés"""
        self.name_edit.clear()
        self.date_edit.clear()
        self.size_edit.clear()
        self.format_edit.clear()
        self.description_edit.clear()
        self.preview_edit.clear()

    def _load_dataset_details(self, dataset_id):
        """
        Charge les détails d'un dataset

        Args:
            dataset_id (int): ID du dataset
        """
        # Vérifier la disponibilité de la base de données
        if not self.database:
            return

        try:
            # Récupérer les informations
            dataset = self.database.get_dataset(dataset_id)

            if not dataset:
                self._clear_details()
                return

            # Mettre à jour les champs
            self.name_edit.setText(dataset.get('name', ''))

            # Date
            date_str = dataset.get('created_at', '')
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str)
                    date_str = date.strftime('%d/%m/%Y %H:%M')
                except:
                    pass

            self.date_edit.setText(date_str)

            # Taille
            size = dataset.get('size', 0)
            if size:
                if size < 1024:
                    size_str = f"{size} octets"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} Ko"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} Mo"
            else:
                size_str = "Inconnu"

            self.size_edit.setText(size_str)

            # Format
            self.format_edit.setText(dataset.get('format', ''))

            # Description
            self.description_edit.setPlainText(dataset.get('description', ''))

            # Aperçu des données
            preview = dataset.get('preview', '')
            if not preview:
                # Tenter de générer un aperçu
                data = dataset.get('data', '')
                if data:
                    if isinstance(data, str):
                        preview = data[:1000] + "..." if len(data) > 1000 else data
                    elif isinstance(data, dict):
                        import json
                        preview = json.dumps(data, indent=2, ensure_ascii=False)
                        preview = preview[:1000] + "..." if len(preview) > 1000 else preview
                    elif isinstance(data, list):
                        import json
                        preview = json.dumps(data[:10], indent=2, ensure_ascii=False)
                        if len(data) > 10:
                            preview += f"\n\n... ({len(data) - 10} éléments de plus)"

            self.preview_edit.setPlainText(preview)

        except Exception as e:
            logger.error(f"Erreur lors du chargement des détails: {str(e)}")
            self.update_status(f"Erreur: {str(e)}")

    def new_dataset(self):
        """Crée un nouveau dataset"""
        # Vérifier la disponibilité de la base de données
        if not self.database:
            QtWidgets.QMessageBox.warning(
                self,
                "Base de données non disponible",
                "La base de données n'est pas disponible."
            )
            return

        # Boîte de dialogue pour les informations du dataset
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Nouveau dataset")
        dialog.setMinimumWidth(400)

        # Style pour la dialog
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.background_color};
            }}
            QLabel {{
                color: {self.text_color};
            }}
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.secondary_color};
            }}
        """)

        # Disposition
        layout = QtWidgets.QVBoxLayout(dialog)

        # Formulaire
        form = QtWidgets.QFormLayout()

        # Nom
        name_edit = QtWidgets.QLineEdit()
        form.addRow("Nom:", name_edit)

        # Description
        description_edit = QtWidgets.QTextEdit()
        description_edit.setMaximumHeight(100)
        form.addRow("Description:", description_edit)

        # Format
        format_combo = QtWidgets.QComboBox()
        format_combo.addItem("JSON", "json")
        format_combo.addItem("CSV", "csv")
        format_combo.addItem("Texte", "text")
        form.addRow("Format:", format_combo)

        # Données
        data_label = QtWidgets.QLabel("Données:")
        form.addRow(data_label)

        data_edit = QtWidgets.QTextEdit()
        data_edit.setPlaceholderText("Entrez les données ou laissez vide pour créer un dataset vide")
        form.addWidget(data_edit)

        layout.addLayout(form)

        # Boutons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Exécuter la boîte de dialogue
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return

        # Récupérer les valeurs
        name = name_edit.text().strip()
        description = description_edit.toPlainText().strip()
        format_type = format_combo.currentData()
        data = data_edit.toPlainText()

        # Valider
        if not name:
            QtWidgets.QMessageBox.warning(
                self,
                "Nom manquant",
                "Veuillez entrer un nom pour le dataset."
            )
            return

        try:
            # Créer le dataset
            dataset_id = self.database.create_dataset(
                name=name,
                description=description,
                format=format_type,
                data=data
            )

            if not dataset_id:
                raise Exception("Échec de la création du dataset")

            # Mettre à jour la liste
            self.refresh_list()

            # Sélectionner le nouveau dataset
            self._select_dataset_by_id(dataset_id)

            # Mettre à jour le statut
            self.update_status(f"Dataset {name} créé (ID: {dataset_id})")

            # Émettre le signal
            self.dataset_created.emit(dataset_id)

        except Exception as e:
            logger.error(f"Erreur lors de la création du dataset: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur de création",
                f"Impossible de créer le dataset:\n\n{str(e)}"
            )

    def _select_dataset_by_id(self, dataset_id):
        """
        Sélectionne un dataset par son ID

        Args:
            dataset_id (int): ID du dataset
        """
        # Parcourir le tableau
        for row in range(self.datasets_table.rowCount()):
            id_item = self.datasets_table.item(row, 0)

            if id_item and int(id_item.text()) == dataset_id:
                # Sélectionner la ligne
                self.datasets_table.selectRow(row)
                break

    def import_dataset(self, file_path=None):
        """
        Importe un dataset depuis un fichier

        Args:
            file_path (str, optional): Chemin du fichier à importer
        """
        # Vérifier la disponibilité de la base de données
        if not self.database:
            QtWidgets.QMessageBox.warning(
                self,
                "Base de données non disponible",
                "La base de données n'est pas disponible."
            )
            return

        # Si aucun chemin n'est fourni, ouvrir un sélecteur de fichier
        if not file_path:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Importer un dataset",
                os.path.expanduser("~"),
                "Tous les fichiers (*.*);;Fichiers JSON (*.json);;Fichiers CSV (*.csv);;Fichiers texte (*.txt)"
            )

            if not file_path:
                return

        # Vérifier l'existence du fichier
        if not os.path.exists(file_path):
            QtWidgets.QMessageBox.warning(
                self,
                "Fichier introuvable",
                f"Le fichier {file_path} n'existe pas."
            )
            return

        # Déterminer le format
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        format_type = "text"
        if ext == '.json':
            format_type = "json"
        elif ext == '.csv':
            format_type = "csv"

        # Lire le fichier
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()

            # Boîte de dialogue pour les informations supplémentaires
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Importer un dataset")
            dialog.setMinimumWidth(400)

            # Style pour la dialog
            dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {self.background_color};
                }}
                QLabel {{
                    color: {self.text_color};
                }}
                QPushButton {{
                    background-color: {self.primary_color};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.secondary_color};
                }}
            """)

            # Disposition
            layout = QtWidgets.QVBoxLayout(dialog)

            # Formulaire
            form = QtWidgets.QFormLayout()

            # Nom
            filename = os.path.basename(file_path)
            name_edit = QtWidgets.QLineEdit(os.path.splitext(filename)[0])
            form.addRow("Nom:", name_edit)

            # Description
            description_edit = QtWidgets.QTextEdit()
            description_edit.setMaximumHeight(100)
            description_edit.setPlaceholderText(f"Dataset importé depuis {filename}")
            form.addRow("Description:", description_edit)

            # Format
            format_combo = QtWidgets.QComboBox()
            format_combo.addItem("JSON", "json")
            format_combo.addItem("CSV", "csv")
            format_combo.addItem("Texte", "text")

            # Sélectionner le format détecté
            if format_type == "json":
                format_combo.setCurrentIndex(0)
            elif format_type == "csv":
                format_combo.setCurrentIndex(1)
            else:
                format_combo.setCurrentIndex(2)

            form.addRow("Format:", format_combo)

            layout.addLayout(form)

            # Boutons
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Exécuter la boîte de dialogue
            if dialog.exec_() != QtWidgets.QDialog.Accepted:
                return

            # Récupérer les valeurs
            name = name_edit.text().strip()
            description = description_edit.toPlainText().strip()
            format_type = format_combo.currentData()

            # Valider
            if not name:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Nom manquant",
                    "Veuillez entrer un nom pour le dataset."
                )
                return

            # Créer le dataset
            dataset_id = self.database.create_dataset(
                name=name,
                description=description,
                format=format_type,
                data=data,
                source=file_path
            )

            if not dataset_id:
                raise Exception("Échec de l'importation du dataset")

            # Mettre à jour la liste
            self.refresh_list()

            # Sélectionner le nouveau dataset
            self._select_dataset_by_id(dataset_id)

            # Mettre à jour le statut
            self.update_status(f"Dataset {name} importé (ID: {dataset_id})")

            # Émettre le signal
            self.dataset_created.emit(dataset_id)

        except Exception as e:
            logger.error(f"Erreur lors de l'importation du dataset: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur d'importation",
                f"Impossible d'importer le dataset:\n\n{str(e)}"
            )

    def export_dataset(self, dataset_id=None):
        """
        Exporte un dataset

        Args:
            dataset_id (int, optional): ID du dataset à exporter
        """
        # Si aucun ID n'est fourni, utiliser le dataset sélectionné
        if dataset_id is None:
            dataset_id = self.current_dataset_id

        if not dataset_id:
            QtWidgets.QMessageBox.warning(
                self,
                "Aucun dataset sélectionné",
                "Veuillez sélectionner un dataset à exporter."
            )
            return

        # Vérifier la disponibilité de la base de données
        if not self.database:
            QtWidgets.QMessageBox.warning(
                self,
                "Base de données non disponible",
                "La base de données n'est pas disponible."
            )
            return

        try:
            # Récupérer les informations
            dataset = self.database.get_dataset(dataset_id)

            if not dataset:
                raise Exception(f"Dataset {dataset_id} introuvable")

            # Déterminer le format par défaut
            format_type = dataset.get('format', 'text')
            default_ext = '.txt'

            if format_type == 'json':
                default_ext = '.json'
            elif format_type == 'csv':
                default_ext = '.csv'

            # Ouvrir un sélecteur de fichier
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Exporter le dataset",
                os.path.expanduser(f"~/{dataset.get('name', 'dataset')}{default_ext}"),
                "Tous les fichiers (*.*);;Fichiers JSON (*.json);;Fichiers CSV (*.csv);;Fichiers texte (*.txt)"
            )

            if not file_path:
                return

            # Déterminer le format d'exportation
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            export_format = "text"
            if ext == '.json':
                export_format = "json"
            elif ext == '.csv':
                export_format = "csv"

            # Récupérer les données
            data = dataset.get('data', '')

            # Si l'exportateur est disponible, l'utiliser
            if self.exporter:
                exported_path = self.exporter.export_dataset(
                    dataset_id,
                    file_path,
                    format=export_format
                )

                # Vérifier si l'exportation a réussi
                if exported_path and os.path.exists(exported_path):
                    # Mettre à jour le statut
                    self.update_status(f"Dataset {dataset.get('name')} exporté vers {os.path.basename(exported_path)}")

                    # Message de confirmation
                    QtWidgets.QMessageBox.information(
                        self,
                        "Exportation réussie",
                        f"Le dataset a été exporté avec succès vers:\n{exported_path}"
                    )

                    return

            # Si l'exportateur n'est pas disponible ou a échoué, exportation manuelle
            with open(file_path, 'w', encoding='utf-8') as f:
                if export_format == 'json' and isinstance(data, str):
                    # Tenter de convertir en JSON
                    try:
                        import json
                        json_data = json.loads(data)
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    except:
                        # Si la conversion échoue, écrire le texte brut
                        f.write(data)
                else:
                    # Écrire le texte brut
                    f.write(data)

            # Mettre à jour le statut
            self.update_status(f"Dataset {dataset.get('name')} exporté vers {os.path.basename(file_path)}")

            # Message de confirmation
            QtWidgets.QMessageBox.information(
                self,
                "Exportation réussie",
                f"Le dataset a été exporté avec succès vers:\n{file_path}"
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'exportation du dataset: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur d'exportation",
                f"Impossible d'exporter le dataset:\n\n{str(e)}"
            )

    def export_current(self):
        """Exporte le dataset sélectionné"""
        self.export_dataset(self.current_dataset_id)

    def _on_import(self):
        """Gère l'action d'importation"""
        self.import_dataset()

    def _on_export(self):
        """Gère l'action d'exportation"""
        self.export_current()

    def _on_delete(self):
        """Gère l'action de suppression"""
        # Vérifier si un dataset est sélectionné
        if not self.current_dataset_id:
            return

        # Confirmation
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le dataset '{self.name_edit.text()}' ?\n\n"
            "Cette action est irréversible.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return

        try:
            # Supprimer le dataset
            success = self.database.delete_dataset(self.current_dataset_id)

            if not success:
                raise Exception(f"Échec de la suppression du dataset {self.current_dataset_id}")

            # Émettre le signal
            dataset_id = self.current_dataset_id
            self.dataset_deleted.emit(dataset_id)

            # Mettre à jour la liste
            self.refresh_list()

            # Mettre à jour le statut
            self.update_status(f"Dataset {self.name_edit.text()} supprimé")

            # Effacer les détails
            self._clear_details()

            # Désactiver les boutons
            self.export_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.view_button.setEnabled(False)
            self.edit_button.setEnabled(False)

        except Exception as e:
            logger.error(f"Erreur lors de la suppression du dataset: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur de suppression",
                f"Impossible de supprimer le dataset:\n\n{str(e)}"
            )

    def _on_view_data(self):
        """Affiche les données complètes du dataset"""
        # Vérifier si un dataset est sélectionné
        if not self.current_dataset_id:
            return

        try:
            # Récupérer les données
            dataset = self.database.get_dataset(self.current_dataset_id)

            if not dataset:
                raise Exception(f"Dataset {self.current_dataset_id} introuvable")

            data = dataset.get('data', '')
            format_type = dataset.get('format', 'text')

            # Formater les données
            formatted_data = data
            if format_type == 'json' and isinstance(data, str):
                try:
                    import json
                    json_data = json.loads(data)
                    formatted_data = json.dumps(json_data, indent=2, ensure_ascii=False)
                except:
                    pass

            # Créer une boîte de dialogue pour afficher les données
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Données de {dataset.get('name', 'dataset')}")
            dialog.resize(800, 600)

            # Style pour la dialog
            dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {self.background_color};
                }}
                QLabel {{
                    color: {self.text_color};
                }}
                QPushButton {{
                    background-color: {self.primary_color};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.secondary_color};
                }}
            """)

            # Disposition
            layout = QtWidgets.QVBoxLayout(dialog)

            # Zone de texte
            text_edit = QtWidgets.QTextEdit()
            text_edit.setPlainText(formatted_data)
            text_edit.setReadOnly(True)

            # Police à chasse fixe pour JSON et CSV
            if format_type in ['json', 'csv']:
                font = QtGui.QFont("Courier New", 10)
                text_edit.setFont(font)

            layout.addWidget(text_edit)

            # Boutons
            buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Afficher la boîte de dialogue
            dialog.exec_()

        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des données: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur d'affichage",
                f"Impossible d'afficher les données du dataset:\n\n{str(e)}"
            )

    def _on_edit_dataset(self):
        """Modifie le dataset sélectionné"""
        # Vérifier si un dataset est sélectionné
        if not self.current_dataset_id:
            return

        try:
            # Récupérer les informations
            dataset = self.database.get_dataset(self.current_dataset_id)

            if not dataset:
                raise Exception(f"Dataset {self.current_dataset_id} introuvable")

            # Boîte de dialogue pour l'édition
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Modifier {dataset.get('name', 'dataset')}")
            dialog.setMinimumWidth(500)
            dialog.resize(800, 600)

            # Style pour la dialog
            dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {self.background_color};
                }}
                QLabel {{
                    color: {self.text_color};
                }}
                QPushButton {{
                    background-color: {self.primary_color};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.secondary_color};
                }}
            """)

            # Disposition
            layout = QtWidgets.QVBoxLayout(dialog)

            # Formulaire
            form = QtWidgets.QFormLayout()

            # Nom
            name_edit = QtWidgets.QLineEdit(dataset.get('name', ''))
            form.addRow("Nom:", name_edit)

            # Description
            description_edit = QtWidgets.QTextEdit()
            description_edit.setPlainText(dataset.get('description', ''))
            description_edit.setMaximumHeight(100)
            form.addRow("Description:", description_edit)

            layout.addLayout(form)

            # Données
            data_label = QtWidgets.QLabel("Données:")
            layout.addWidget(data_label)

            data_edit = QtWidgets.QTextEdit()
            data_edit.setPlainText(dataset.get('data', ''))

            # Police à chasse fixe pour JSON et CSV
            if dataset.get('format') in ['json', 'csv']:
                font = QtGui.QFont("Courier New", 10)
                data_edit.setFont(font)

            layout.addWidget(data_edit)

            # Boutons
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Exécuter la boîte de dialogue
            if dialog.exec_() != QtWidgets.QDialog.Accepted:
                return

            # Récupérer les valeurs
            name = name_edit.text().strip()
            description = description_edit.toPlainText().strip()
            data = data_edit.toPlainText()

            # Valider
            if not name:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Nom manquant",
                    "Veuillez entrer un nom pour le dataset."
                )
                return

            # Mettre à jour le dataset
            success = self.database.update_dataset(
                self.current_dataset_id,
                name=name,
                description=description,
                data=data
            )

            if not success:
                raise Exception(f"Échec de la mise à jour du dataset {self.current_dataset_id}")

            # Mettre à jour l'interface
            self.refresh_list()
            self._select_dataset_by_id(self.current_dataset_id)

            # Mettre à jour le statut
            self.update_status(f"Dataset {name} mis à jour")

        except Exception as e:
            logger.error(f"Erreur lors de la modification du dataset: {str(e)}")

            # Message d'erreur
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur de modification",
                f"Impossible de modifier le dataset:\n\n{str(e)}"
            )

    def _on_dataset_double_clicked(self, row, column):
        """
        Gère le double-clic sur un dataset

        Args:
            row (int): Index de ligne
            column (int): Index de colonne
        """
        # Simplement afficher les données complètes
        self._on_view_data()