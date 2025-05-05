#!/usr/bin/env python
"""
Script pour compiler les ressources Qt
"""
import os
import sys
import subprocess
from pathlib import Path


def find_pyrcc5():
    """Trouve l'emplacement de pyrcc5 dans l'environnement"""
    # Pyrcc5 est typiquement dans le dossier Scripts de l'environnement virtuel
    venv_scripts = Path(sys.executable).parent / "pyrcc5.exe"

    if venv_scripts.exists():
        return str(venv_scripts)

    # Fallback : chercher dans plusieurs emplacements
    possible_paths = [
        Path(sys.executable).parent.parent / "Scripts" / "pyrcc5.exe",
        Path(sys.executable).parent / "Scripts" / "pyrcc5.exe",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return None


def compile_resources():
    """Compile le fichier .qrc en module Python"""
    script_dir = Path(__file__).parent
    qrc_file = script_dir / "resources.qrc"
    output_file = script_dir / "resources_rc.py"

    # Trouver pyrcc5
    pyrcc5_path = find_pyrcc5()

    if not pyrcc5_path:
        print("Erreur: pyrcc5 n'a pas été trouvé")
        print("Installation PyQt5 détectée, mais pyrcc5 est manquant")
        return False

    print(f"pyrcc5 trouvé dans: {pyrcc5_path}")

    # Vérifier si le fichier QRC existe
    if not qrc_file.exists():
        print(f"Erreur: {qrc_file} n'existe pas")
        return False

    try:
        # Exécuter la compilation
        print(f"Compilation de {qrc_file} vers {output_file}...")
        result = subprocess.run(
            [pyrcc5_path, str(qrc_file), "-o", str(output_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("Compilation réussie!")
            print(f"Fichier créé: {output_file}")
            return True
        else:
            print("Erreur lors de la compilation:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False


def create_sample_qrc():
    """Crée un exemple de fichier .qrc si absent"""
    script_dir = Path(__file__).parent
    qrc_file = script_dir / "resources.qrc"

    if not qrc_file.exists():
        qrc_content = """<RCC>
  <qresource prefix="/">
    <file>icons/app_icon.png</file>
    <file>icons/refresh.png</file>
    <file>icons/export.png</file>
    <file>icons/import.png</file>
    <file>icons/settings.png</file>
    <file>icons/search.png</file>
    <file>icons/delete.png</file>
    <file>icons/save.png</file>
    <file>icons/open.png</file>
    <file>icons/new.png</file>
  </qresource>
</RCC>
"""
        with open(qrc_file, 'w', encoding='utf-8') as f:
            f.write(qrc_content)

        print(f"Fichier exemple {qrc_file} créé")
        print("Ajoutez vos icônes dans le dossier icons/ avant de compiler")

        # Créer le dossier icons s'il n'existe pas
        icons_dir = script_dir / "icons"
        icons_dir.mkdir(exist_ok=True)
        print(f"Dossier {icons_dir} créé")

        return True


def main():
    """Point d'entrée principal"""
    print("=== Compilation des ressources Qt ===")
    print()

    # Créer un exemple de QRC si nécessaire
    create_sample_qrc()

    # Compiler les ressources
    success = compile_resources()

    if success:
        print("\nPour utiliser les ressources dans votre code:")
        print("  import ui.resources.resources_rc")
        print("  icon = QtGui.QIcon(':/icons/app_icon.png')")
    else:
        print("\nLa compilation a échoué. Vérifiez les erreurs ci-dessus.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())