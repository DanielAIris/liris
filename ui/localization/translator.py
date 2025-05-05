# ui/localization/translator.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from PyQt5 import QtCore


class Translator:
    """Gestionnaire de traductions pour l'application"""

    DEFAULT_LANGUAGE = "fr"
    TRANSLATIONS_DIR = os.path.join("ui", "localization", "translations")

    def __init__(self):
        self.current_language = self.DEFAULT_LANGUAGE
        self.translations = {}
        self.available_languages = {}
        self._load_languages()
        self._load_translation(self.DEFAULT_LANGUAGE)

    def _load_languages(self):
        """Charge la liste des langues disponibles"""
        # Scanner le dossier translations
        if os.path.exists(self.TRANSLATIONS_DIR):
            for file in os.listdir(self.TRANSLATIONS_DIR):
                if file.endswith('.json'):
                    lang_code = file.replace('.json', '')
                    # Essayer de charger le nom de la langue depuis le fichier
                    try:
                        with open(os.path.join(self.TRANSLATIONS_DIR, file), 'r',
                                  encoding='utf-8') as f:
                            data = json.load(f)
                            self.available_languages[lang_code] = data.get('_language_name', lang_code)
                    except:
                        self.available_languages[lang_code] = lang_code

    def _load_translation(self, language_code):
        """Charge un fichier de traduction"""
        file_path = os.path.join(self.TRANSLATIONS_DIR, f"{language_code}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                    self.current_language = language_code
                    return True
            except Exception as e:
                print(f"Erreur lors du chargement de {language_code}: {e}")
                return False
        return False

    def set_language(self, language_code):
        """Change la langue courante"""
        if language_code in self.available_languages:
            if self._load_translation(language_code):
                return True
        return False

    def translate(self, key, **kwargs):
        """Traduit une clé avec des paramètres optionnels"""
        parts = key.split('.')
        text = self.translations

        # Navigation dans les objets imbriqués
        for part in parts:
            if isinstance(text, dict):
                text = text.get(part, key)
            else:
                return key

        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text

    def get_available_languages(self):
        """Retourne la liste des langues disponibles"""
        return self.available_languages


# Instance globale du traducteur
translator = Translator()


# Fonction raccourci pour les traductions
def tr(key, **kwargs):
    return translator.translate(key, **kwargs)