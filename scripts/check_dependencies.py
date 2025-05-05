# tests/check_dependencies.py

"""
Script pour vérifier que toutes les dépendances importantes sont installées et configurées correctement
"""

import sys
import platform
import subprocess


def check_python_version():
    """Vérifie la version de Python"""
    print(f"Python: {sys.version}")

    major, minor, _ = sys.version_info[:3]
    if major != 3 or minor < 7:
        print("⚠️ Warning: Python 3.7+ est recommandé")
    else:
        print("✅ Version Python OK")
    print()


def check_module(module_name, package_name=None):
    """Vérifie si un module est installé"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} est installé")
        return True
    except ImportError:
        package = package_name or module_name
        print(f"❌ {module_name} n'est pas installé")
        print(f"   Pour l'installer: pip install {package}")
        return False


def check_pyqt5():
    """Vérifie PyQt5"""
    try:
        from PyQt5 import QtWidgets, QtCore, QtGui
        print("✅ PyQt5 est installé et fonctionnel")
        print(f"   Version Qt: {QtCore.QT_VERSION_STR}")
        return True
    except ImportError:
        print("❌ PyQt5 n'est pas installé ou mal configuré")
        print("   Pour l'installer: pip install PyQt5")
        return False


def check_opencv():
    """Vérifie OpenCV"""
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")

        # Test rapide
        img = cv2.imread("non_existent.jpg")  # Devrait retourner None
        if img is None:
            print("   • Test de lecture d'image: OK")

        return True
    except ImportError:
        print("❌ OpenCV n'est pas installé")
        print("   Pour l'installer: pip install opencv-python")
        return False


def check_tesseract():
    """Vérifie Tesseract OCR"""
    try:
        import pytesseract

        # Essayer d'obtenir la version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}")
            return True
        except pytesseract.TesseractNotFoundError:
            print("⚠️ pytesseract est installé mais Tesseract n'est pas trouvé")
            print("   Pour installer Tesseract:")
            system = platform.system().lower()
            if system == 'windows':
                print("   - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            elif system == 'darwin':
                print("   - macOS: brew install tesseract")
            else:
                print("   - Linux: sudo apt install tesseract-ocr")
            return False
    except ImportError:
        print("❌ pytesseract n'est pas installé")
        print("   Pour l'installer: pip install pytesseract")
        return False


def check_pyautogui():
    """Vérifie PyAutoGUI"""
    try:
        import pyautogui
        print(f"✅ PyAutoGUI est installé")

        # Test de base
        width, height = pyautogui.size()
        print(f"   • Résolution de l'écran: {width}x{height}")

        return True
    except ImportError:
        print("❌ PyAutoGUI n'est pas installé")
        print("   Pour l'installer: pip install pyautogui")
        return False


def check_required_directories():
    """Vérifie les répertoires requis"""
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_dirs = [
        "data",
        "config",
        "logs",
        "ui/resources/icons"
    ]

    all_ok = True
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✅ Répertoire {dir_path} existe")
        else:
            print(f"⚠️ Répertoire {dir_path} manquant - sera créé automatiquement")
            all_ok = False

    return all_ok


def check_all():
    """Vérifie toutes les dépendances"""
    print("=== VÉRIFICATION DES DÉPENDANCES LIRIS ===")
    print()

    print("1. Version Python:")
    check_python_version()

    print("2. Modules Python requis:")
    modules = [
        ("PyQt5", None),
        ("cv2", "opencv-python"),
        ("pyautogui", None),
        ("pytesseract", None),
        ("numpy", None),
        ("sqlite3", "standard library")
    ]

    all_ok = True
    for module, package in modules:
        if not check_module(module, package):
            all_ok = False
    print()

    print("3. Tests spécifiques:")
    if not check_pyqt5():
        all_ok = False
    if not check_opencv():
        all_ok = False
    if not check_tesseract():
        all_ok = False
    if not check_pyautogui():
        all_ok = False
    print()

    print("4. Structure du projet:")
    if not check_required_directories():
        all_ok = False
    print()

    if all_ok:
        print("✅ Toutes les dépendances sont installées et configurées!")
    else:
        print("⚠️ Certaines dépendances nécessitent une attention")

    print()
    print("=== FIN DE LA VÉRIFICATION ===")


if __name__ == "__main__":
    check_all()