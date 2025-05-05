#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
auto_test_language_selector.py
Script pour tester avec rechargement automatique des changements
"""

import sys
import importlib
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


def test_language_selector():
    app = QApplication(sys.argv)

    # Fenêtre principale avec bouton pour tester
    main_window = QWidget()
    main_window.setWindowTitle("Test Language Selector")
    main_window.resize(300, 100)

    layout = QVBoxLayout()

    test_button = QPushButton("Tester le sélecteur")

    def on_click():
        # Recharger le module pour récupérer les changements
        import ui.widgets.language_selector
        importlib.reload(ui.widgets.language_selector)

        # Créer une nouvelle instance avec les changements
        from ui.widgets.language_selector import LanguageSelector
        selector = LanguageSelector()

        if selector.exec_():
            selected_language = selector.get_selected_language()
            print(f"Langue sélectionnée : {selected_language}")
        else:
            print("Sélection annulée")

    test_button.clicked.connect(on_click)
    layout.addWidget(test_button)

    main_window.setLayout(layout)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    test_language_selector()