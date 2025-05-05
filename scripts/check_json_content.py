#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Liris/scripts/check_json_content.py
Vérifie exactement le contenu des fichiers JSON
"""

import os

# Chemins des fichiers
fr_file = os.path.join("ui", "localization", "translations", "fr.json")
en_file = os.path.join("ui", "localization", "translations", "en.json")

for lang, filepath in [("Français", fr_file), ("Anglais", en_file)]:
    print(f"\n===== {lang} ({filepath}) =====")

    if os.path.exists(filepath):
        try:
            # Lire le contenu brut
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"Taille du fichier: {len(content)} caractères")
            print(f"Premiers 100 caractères:")
            print(repr(content[:100]))

            # Vérifier si c'est bien du JSON
            import json

            data = json.loads(content)
            print(f"\n✓ JSON valide avec {len(data)} clés")

        except json.JSONDecodeError as e:
            print(f"\n✗ Erreur JSON: {e}")
            print(f"Ligne {e.lineno}, colonne {e.colno}")
            print("Contenu dans cette zone:")
            print(repr(content[max(0, e.pos - 20):e.pos + 20]))

        except Exception as e:
            print(f"\n✗ Erreur: {e}")
    else:
        print(f"✗ Fichier n'existe pas")