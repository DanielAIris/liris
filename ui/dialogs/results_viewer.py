from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QTabWidget, QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QLabel
import json


class ResultsViewerDialog(QDialog):
    """
    Dialogue pour visualiser les résultats détaillés
    """

    def __init__(self, results_data, parent=None):
        super().__init__(parent)

        self.results_data = results_data
        self.setWindowTitle("Visualisateur de Résultats")
        self.setMinimumSize(800, 600)

        self._init_ui()
        self._load_results()

    def _init_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)

        # Tabs pour différentes vues
        self.tab_widget = QTabWidget()

        # Tab "Résumé"
        self.summary_tab = self._create_summary_tab()
        self.tab_widget.addTab(self.summary_tab, "Résumé")

        # Tab "Données brutes"
        self.raw_tab = self._create_raw_tab()
        self.tab_widget.addTab(self.raw_tab, "Données brutes")

        # Tab "Visualisation"
        self.viz_tab = self._create_visualization_tab()
        self.tab_widget.addTab(self.viz_tab, "Visualisation")

        layout.addWidget(self.tab_widget)

        # Boutons
        button_layout = QHBoxLayout()

        self.export_button = QPushButton("Exporter")
        self.export_button.clicked.connect(self._on_export)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _create_summary_tab(self):
        """Crée l'onglet résumé"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Statistiques principales
        stats_group = QtWidgets.QGroupBox("Statistiques")
        stats_layout = QtWidgets.QGridLayout()

        self.type_label = QLabel("Type: -")
        self.status_label = QLabel("Statut: -")
        self.start_label = QLabel("Début: -")
        self.end_label = QLabel("Fin: -")
        self.duration_label = QLabel("Durée: -")

        stats_layout.addWidget(QLabel("Type:"), 0, 0)
        stats_layout.addWidget(self.type_label, 0, 1)
        stats_layout.addWidget(QLabel("Statut:"), 1, 0)
        stats_layout.addWidget(self.status_label, 1, 1)
        stats_layout.addWidget(QLabel("Début:"), 2, 0)
        stats_layout.addWidget(self.start_label, 2, 1)
        stats_layout.addWidget(QLabel("Fin:"), 3, 0)
        stats_layout.addWidget(self.end_label, 3, 1)
        stats_layout.addWidget(QLabel("Durée:"), 4, 0)
        stats_layout.addWidget(self.duration_label, 4, 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Résumé textuel
        summary_group = QtWidgets.QGroupBox("Résumé")
        summary_layout = QVBoxLayout()

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        return tab

    def _create_raw_tab(self):
        """Crée l'onglet données brutes"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Options d'affichage
        options_layout = QHBoxLayout()

        self.json_radio = QtWidgets.QRadioButton("JSON")
        self.json_radio.setChecked(True)
        self.json_radio.toggled.connect(self._update_raw_display)
        options_layout.addWidget(self.json_radio)

        self.formatted_radio = QtWidgets.QRadioButton("Format lisible")
        self.formatted_radio.toggled.connect(self._update_raw_display)
        options_layout.addWidget(self.formatted_radio)

        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Zone de données
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setFont(QtGui.QFont("Courier New", 10))
        layout.addWidget(self.raw_text)

        return tab

    def _create_visualization_tab(self):
        """Crée l'onglet visualisation"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Splitter pour vue hiérarchique et détails
        splitter = QSplitter(Qt.Horizontal)

        # Vue arborescente
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Structure des données")
        self.tree_widget.itemClicked.connect(self._on_tree_item_clicked)
        splitter.addWidget(self.tree_widget)

        # Zone de détails
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        splitter.addWidget(self.details_text)

        splitter.setSizes([300, 500])
        layout.addWidget(splitter)

        return tab

    def _load_results(self):
        """Charge les résultats dans la dialogue"""
        # Mettre à jour le résumé
        self._update_summary()

        # Charger les données brutes
        self._update_raw_display()

        # Construire la vue arborescente
        self._build_tree_view()

    def _update_summary(self):
        """Met à jour l'onglet résumé"""
        if isinstance(self.results_data, dict):
            # Type
            if 'type' in self.results_data:
                self.type_label.setText(self.results_data['type'])

            # Statut
            if 'status' in self.results_data:
                self.status_label.setText(self.results_data['status'])

            # Dates
            if 'start_time' in self.results_data:
                self.start_label.setText(self.results_data['start_time'])

            if 'end_time' in self.results_data:
                self.end_label.setText(self.results_data['end_time'])

            # Calculer la durée
            if 'start_time' in self.results_data and 'end_time' in self.results_data:
                try:
                    from datetime import datetime
                    start = datetime.fromisoformat(self.results_data['start_time'])
                    end = datetime.fromisoformat(self.results_data['end_time'])
                    duration = end - start
                    self.duration_label.setText(str(duration))
                except:
                    pass

            # Résumé textuel
            summary = self._generate_summary()
            self.summary_text.setPlainText(summary)

    def _generate_summary(self):
        """Génère un résumé textuel des résultats"""
        summary = ""

        if isinstance(self.results_data, dict):
            # Compter les éléments
            if 'results' in self.results_data and isinstance(self.results_data['results'], list):
                count = len(self.results_data['results'])
                summary += f"Nombre de résultats: {count}\n\n"

            # Ajouter des informations spécifiques selon le type
            if 'type' in self.results_data:
                if self.results_data['type'] == 'brainstorming':
                    platforms = self.results_data.get('platforms', [])
                    summary += f"Plateformes utilisées: {', '.join(platforms)}\n"

                    if 'final_scores' in self.results_data:
                        summary += "\nScores finaux:\n"
                        for platform, score in self.results_data['final_scores'].items():
                            summary += f"- {platform}: {score}/100\n"

                elif self.results_data['type'] == 'annotation':
                    if 'progress' in self.results_data:
                        summary += f"Progression: {self.results_data['progress']}%\n"

            # Ajouter les erreurs si présentes
            if 'error' in self.results_data:
                summary += f"\nErreur: {self.results_data['error']}\n"

        return summary

    def _update_raw_display(self):
        """Met à jour l'affichage des données brutes"""
        if self.json_radio.isChecked():
            # Format JSON indenté
            try:
                json_text = json.dumps(self.results_data, indent=2, ensure_ascii=False)
            except:
                json_text = str(self.results_data)
            self.raw_text.setPlainText(json_text)
        else:
            # Format lisible
            readable_text = self._format_readable(self.results_data)
            self.raw_text.setPlainText(readable_text)

    def _format_readable(self, data, indent=0):
        """Formate les données de manière lisible"""
        result = ""
        indent_str = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result += f"{indent_str}{key}:\n"
                    result += self._format_readable(value, indent + 1)
                else:
                    result += f"{indent_str}{key}: {value}\n"
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    result += f"{indent_str}[{i}]:\n"
                    result += self._format_readable(item, indent + 1)
                else:
                    result += f"{indent_str}[{i}]: {item}\n"
        else:
            result += f"{indent_str}{data}\n"

        return result

    def _build_tree_view(self, parent=None, data=None, name=""):
        """Construit la vue arborescente des données"""
        if parent is None:
            parent = self.tree_widget
            self.tree_widget.clear()

        if data is None:
            data = self.results_data

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    # Créer un nœud pour les structures imbriquées
                    node = QTreeWidgetItem(parent, [key])
                    node.setData(0, Qt.UserRole, value)
                    self._build_tree_view(node, value, key)
                else:
                    # Ajouter directement les valeurs simples
                    item = QTreeWidgetItem(parent, [key, str(value)])

        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    node = QTreeWidgetItem(parent, [f"Élément {i}"])
                    node.setData(0, Qt.UserRole, item)
                    self._build_tree_view(node, item, f"Élément {i}")
                else:
                    QTreeWidgetItem(parent, [f"Élément {i}", str(item)])

        # Développer le premier niveau
        if parent == self.tree_widget:
            self.tree_widget.expandToDepth(0)

    def _on_tree_item_clicked(self, item, column):
        """Gère le clic sur un élément de l'arbre"""
        data = item.data(0, Qt.UserRole)
        if data is not None:
            # Afficher les détails de l'élément sélectionné
            details = json.dumps(data, indent=2, ensure_ascii=False)
            self.details_text.setPlainText(details)

    def _on_export(self):
        """Gère l'exportation des résultats"""
        # Ouvrir un dialogue de sauvegarde
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Exporter les résultats",
            "results.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )

        if filepath:
            try:
                if filepath.endswith('.json'):
                    # Export JSON
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(self.results_data, f, indent=2, ensure_ascii=False)
                else:
                    # Export texte
                    with open(filepath, 'w', encoding='utf-8') as f:
                        if self.formatted_radio.isChecked():
                            f.write(self._format_readable(self.results_data))
                        else:
                            f.write(json.dumps(self.results_data, indent=2, ensure_ascii=False))

                QtWidgets.QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Résultats exportés: {filepath}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Erreur d'export",
                    f"Erreur lors de l'exportation: {str(e)}"
                )