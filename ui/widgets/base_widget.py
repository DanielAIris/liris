#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Liris/ui/widgets/base_widget.py
"""

from PyQt5 import QtWidgets, QtCore
from ui.styles.theme import Theme


class BaseWidget(QtWidgets.QWidget):
    """Widget de base pour tous les widgets de l'application"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = Theme()
        self._init_base_style()

    def _init_base_style(self):
        """Applique le style de base du thème"""
        self.setStyleSheet(Theme.get_global_stylesheet())

    def create_group_box(self, title):
        """
        Crée un QGroupBox standardisé

        Args:
            title (str): Titre du groupe

        Returns:
            QGroupBox: Le groupe créé
        """
        group = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(Theme.SPACING_NORMAL)
        layout.setContentsMargins(
            Theme.PADDING_NORMAL, Theme.PADDING_NORMAL,
            Theme.PADDING_NORMAL, Theme.PADDING_NORMAL
        )
        return group

    def create_title_label(self, text, font_size=None):
        """
        Crée un label de titre standardisé

        Args:
            text (str): Texte du titre
            font_size (int, optional): Taille de police

        Returns:
            QLabel: Le label créé
        """
        label = QtWidgets.QLabel(text)
        font_size = font_size or Theme.FONT_SIZE_TITLE
        label.setStyleSheet(f"""
            font-size: {font_size}px;
            font-weight: bold;
            color: {Theme.PRIMARY_COLOR};
            margin: 0;
            padding: 0;
        """)
        return label

    def create_button(self, text, callback=None, color=None):
        """
        Crée un bouton standardisé

        Args:
            text (str): Texte du bouton
            callback (callable, optional): Fonction à connecter
            color (str, optional): Couleur personnalisée

        Returns:
            QPushButton: Le bouton créé
        """
        button = QtWidgets.QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return button