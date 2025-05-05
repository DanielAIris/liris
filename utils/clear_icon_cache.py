#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilitaire pour nettoyer le cache des icônes Windows et réinitialiser l'application
"""

import os
import time
import sys
import shutil
import sqlite3
import winreg
from pathlib import Path
from glob import glob


def clear_windows_icon_cache():
    """Nettoie le cache des icônes Windows sans arrêter explorer.exe"""
    print("\n=== Nettoyage du cache des icônes Windows ===")

    try:
        # Supprimer les fichiers de cache d'icônes accessibles
        user_folder = Path.home()
        cache_files = [
            user_folder / "AppData" / "Local" / "IconCache.db",
            *(user_folder / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer").glob("iconcache_*.db")
        ]

        for cache_file in cache_files:
            try:
                if cache_file.exists():
                    cache_file.unlink()
                    print(f"✓ Supprimé: {cache_file}")
            except PermissionError:
                print(f"✗ Permission refusée pour {cache_file}. Essayez avec des droits administrateur.")
            except Exception as e:
                print(f"✗ Erreur lors de la suppression de {cache_file}: {e}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du nettoyage du cache: {e}")
        return False


def clear_application_database():
    """Nettoie la base de données SQLite de l'application"""
    print("\n=== Nettoyage de la base de données ===")

    app_dir = Path(__file__).parent.parent
    db_path = app_dir / "data" / "liris.db"

    if db_path.exists():
        try:
            # Sauvegarder d'abord
            backup_path = db_path.with_name(f'liris_{time.strftime("%Y%m%d_%H%M%S")}.db.backup')
            shutil.copy2(db_path, backup_path)
            print(f"✓ Sauvegarde créée: {backup_path}")

            # Supprimer la base de données
            db_path.unlink()
            print(f"✓ Base de données supprimée")

            # Créer une nouvelle base de données vide
            conn = sqlite3.connect(db_path)
            conn.close()
            print(f"✓ Nouvelle base de données vide créée")

        except Exception as e:
            print(f"✗ Erreur lors du nettoyage de la DB: {e}")
    else:
        print("ℹ Aucune base de données trouvée")


def clear_qsettings():
    """Nettoie les QSettings de l'application pour réinitialiser la langue"""
    print("\n=== Nettoyage des paramètres Qt ===")

    try:
        settings_path = r"Software\Liris\IACollaborative"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, settings_path, 0, winreg.KEY_ALL_ACCESS)
            i = 0
            values = []
            while True:
                try:
                    name, _, _ = winreg.EnumValue(key, i)
                    values.append(name)
                    i += 1
                except WindowsError:
                    break

            for value_name in values:
                try:
                    winreg.DeleteValue(key, value_name)
                    print(f"✓ Supprimé: {value_name}")
                except:
                    pass

            winreg.CloseKey(key)
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, settings_path)
                print("✓ Clé de registre supprimée")
            except:
                print("ℹ Clé de registre déjà supprimée")
        except FileNotFoundError:
            print("ℹ Aucun paramètre Qt trouvé dans le registre")
        except Exception as e:
            print(f"✗ Erreur lors de l'accès au registre: {e}")

    except Exception as e:
        print(f"✗ Erreur lors du nettoyage des QSettings: {e}")


def set_default_language():
    """Force la langue française par défaut en modifiant QSettings"""
    print("\n=== Configuration de la langue par défaut ===")

    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings("Liris", "IACollaborative")
        settings.setValue("language", "fr")
        print("✓ Langue par défaut définie: Français")
    except Exception as e:
        print(f"✗ Erreur lors de la configuration de la langue: {e}")


def restart_explorer():
    """Redémarre l'Explorateur Windows pour appliquer les modifications du cache des icônes"""
    print("\n=== Redémarrage de l'Explorateur Windows ===")
    try:
        confirm = input("Voulez-vous redémarrer l'Explorateur Windows maintenant ? (o/n) : ").strip().lower()
        if confirm != 'o':
            print("ℹ Redémarrage annulé. Veuillez redémarrer l'Explorateur manuellement ou redémarrer votre PC.")
            return

        # Arrêter l'Explorateur
        os.system("taskkill /IM explorer.exe /F")
        print("✓ Explorateur Windows arrêté")

        # Attendre un court instant
        time.sleep(1)

        # Redémarrer l'Explorateur
        os.system("start explorer.exe")
        print("✓ Explorateur Windows redémarré")
    except Exception as e:
        print(f"❌ Erreur lors du redémarrage de l'Explorateur: {e}")


def main():
    """Fonction principale"""
    print("=== NETTOYAGE ET RÉINITIALISATION LIRIS ===")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"OS: {sys.platform}")

    if sys.platform != "win32":
        print("❌ Ce script est uniquement pour Windows")
        return

    print("\n🔄 Début de la réinitialisation...")

    # 1. Nettoyer le cache des icônes Windows
    clear_windows_icon_cache()

    # 2. Nettoyer la base de données
    clear_application_database()

    # 3. Nettoyer les QSettings
    clear_qsettings()

    # 4. Définir le français comme langue par défaut
    set_default_language()

    # 5. Redémarrer l'Explorateur Windows (facultatif)
    restart_explorer()

    print("\n✨ NETTOYAGE TERMINÉ ✨")
    print("\nL'application a été réinitialisée avec succès.")
    print("La langue sera maintenant en français par défaut.")
    print("Vous pouvez redémarrer l'application.\n")


if __name__ == "__main__":
    main()