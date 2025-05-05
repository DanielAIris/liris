#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Liris/scripts/debug_translation.py
Script de debug pour comprendre le problème de traduction
"""

import sys
import os
import json
from PyQt5.QtCore import QSettings

# Ajouter le dossier racine au PYTHONPATH
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_dir)

from ui.localization.translator import translator, tr


def debug_translations():
    print("\n===== DÉBUGAGE DU SYSTÈME DE TRADUCTION =====")
    print(f"Répertoire de travail: {os.getcwd()}")

    # 1. Vérifier les chemins
    print("\n1. Vérification des chemins:")
    translations_dir = translator.TRANSLATIONS_DIR
    print(f"   Dossier traductions: {translations_dir}")
    print(f"   Existe?: {os.path.exists(translations_dir)}")

    # 2. Vérifier les fichiers JSON
    print("\n2. Vérification des fichiers JSON:")
    fr_file = os.path.join(translations_dir, "fr.json")
    en_file = os.path.join(translations_dir, "en.json")

    for lang, filepath in [("Français", fr_file), ("Anglais", en_file)]:
        print(f"   {lang}: {filepath}")
        if os.path.exists(filepath):
            print(f"      ✓ Existe")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"      ✓ JSON valide avec {len(data)} clés")
                print(f"      ✓ Premières clés: {list(data.keys())[:10]}")
            except Exception as e:
                print(f"      ✗ Erreur JSON: {e}")
        else:
            print(f"      ✗ N'existe pas")

    # 3. État actuel du translator
    print("\n3. État du translator:")
    print(f"   Langue actuelle: {translator.current_language}")
    print(f"   Nombre de traductions chargées: {len(translator.translations)}")
    print(f"   Langues disponibles: {translator.get_available_languages()}")

    # 4. Settings
    print("\n4. Settings:")
    settings = QSettings("Liris", "IACollaborative")
    print(f"   Langue sauvegardée: {settings.value('language', 'AUCUNE')}")

    # 5. Test de traduction avec différentes langues
    print("\n5. Test de traduction:")
    test_keys = [
        "app_title",
        "file",
        "status.ready",
        "messages.no_platforms"
    ]

    for lang in ["fr", "en"]:
        print(f"\n   === Test avec langue: {lang} ===")
        if translator.set_language(lang):
            print(f"   ✓ Langue définie sur: {translator.current_language}")
            for key in test_keys:
                translated = tr(key)
                print(f"   '{key}' -> '{translated}'")
        else:
            print(f"   ✗ Impossible de définir la langue sur: {lang}")

    # 6. Vérifier le contenu actuel des traductions
    print("\n6. Contenu des traductions actuelles:")
    if translator.translations:
        print("   Clés principales:")
        for key in sorted(translator.translations.keys())[:15]:
            value = translator.translations[key]
            if isinstance(value, dict):
                print(f"   '{key}': {len(value)} sous-clés")
            else:
                print(f"   '{key}': '{value}'")
    else:
        print("   Aucune traduction chargée!")


if __name__ == "__main__":
    debug_translations()