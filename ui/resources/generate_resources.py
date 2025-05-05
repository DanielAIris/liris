#!/usr/bin/env python
"""
Script pour générer les ressources manquantes de Liris
Usage: python generate_resources.py
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import urllib.request
import shutil
import sys


def create_directories():
    """Crée la structure de dossiers nécessaire"""
    base_path = Path.cwd()  # Utilise le répertoire courant (ui/resources)
    dirs = ["icons", "images", "styles", "fonts"]

    for dir_name in dirs:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Créé: {dir_path}")


def create_simple_icon(name, color, size=128):
    """Crée une icône simple avec PIL"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Formes en fonction du nom
    if name == "app_icon":
        draw.ellipse([10, 10, size - 10, size - 10], fill=color)
        # Note: PIL ne permet pas de spécifier font_size dans draw.text directement
        # Nous allons créer une simple icône sans texte
        draw.ellipse([40, 40, size-40, size-40], fill="white")
    elif name == "refresh":
        draw.arc([10, 10, size - 10, size - 10], 0, 270, fill=color, width=15)
        draw.arc([10, 10, size - 10, size - 10], 45, 315, fill=color, width=15)
    elif name == "export":
        draw.rectangle([30, 20, size - 30, size - 20], outline=color, width=10)
        draw.line([size // 2, 30, size // 2, size - 30], fill=color, width=10)
        draw.line([size // 4, size - 40, size // 2, size - 30], fill=color, width=10)
        draw.line([3 * size // 4, size - 40, size // 2, size - 30], fill=color, width=10)
    elif name == "save":
        draw.rectangle([20, 20, size - 20, size - 20], outline=color, width=10)
        draw.rectangle([40, 20, size - 40, 40], fill=color)
    elif name == "settings":
        center = size // 2
        # Créer un engrenage simplifié
        for i in range(8):
            angle = i * 45
            x_start = center + int(30 * os.cos(os.radians(angle)))
            y_start = center + int(30 * os.sin(os.radians(angle)))
            x_end = center + int(40 * os.cos(os.radians(angle)))
            y_end = center + int(40 * os.sin(os.radians(angle)))
            draw.line([x_start, y_start, x_end, y_end], fill=color, width=8)
        draw.ellipse([center-20, center-20, center+20, center+20], fill=color)
    else:
        # Icône générique
        draw.rectangle([20, 20, size - 20, size - 20], outline=color, width=10)
        draw.ellipse([40, 40, size - 40, size - 40], outline=color, width=8)

    return img


def generate_all_icons():
    """Génère toutes les icônes nécessaires"""
    icons = {
        "app_icon": "#2E7D32", "refresh": "#1976D2", "export": "#F57C00",
        "import": "#455A64", "settings": "#757575", "search": "#00ACC1",
        "delete": "#E53935", "save": "#43A047", "open": "#3949AB",
        "new": "#8E24AA", "copy": "#546E7A", "view": "#607D8B",
        "success": "#2E7D32", "error": "#E53935", "warning": "#F9A825",
        "info": "#0288D1", "running": "#26A69A", "brainstorming": "#AB47BC",
        "annotation": "#5C6BC0", "dataset": "#42A5F5", "history": "#78909C",
        "chatgpt": "#10A37F", "claude": "#C7522A", "ai_platform": "#795548"
    }

    for name, color in icons.items():
        icon = create_simple_icon(name, color)
        icon.save(f"icons/{name}.png")
        print(f"✅ Icône créée: {name}.png")


def create_images():
    """Crée les images nécessaires"""
    # Logo
    logo = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    draw.ellipse([20, 20, 236, 236], fill="#2E7D32")
    # Dessiner un simple "L" au lieu d'utiliser du texte avec une police
    draw.line([80, 200, 80, 100], fill="white", width=30)
    draw.line([80, 200, 140, 200], fill="white", width=30)
    logo.save("images/logo.png")
    print("✅ Logo créé")

    # Welcome
    welcome = Image.new('RGB', (800, 400), "white")
    draw = ImageDraw.Draw(welcome)
    draw.rectangle([0, 0, 800, 100], fill="#2E7D32")
    # Créer une image simple sans texte
    draw.ellipse([350, 150, 450, 250], fill="#2E7D32")
    draw.line([380, 200, 380, 180], fill="white", width=20)
    draw.line([380, 200, 420, 200], fill="white", width=20)
    welcome.save("images/welcome.png")
    print("✅ Image welcome créée")


def create_qss_files():
    """Crée les fichiers de style QSS"""
    dark_theme = """QWidget {
    background-color: #303030;
    color: #FFFFFF;
}

QPushButton {
    background-color: #424242;
    border: 1px solid #555555;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #515151;
}

QLineEdit {
    background-color: #424242;
    border: 1px solid #555555;
    padding: 5px;
    border-radius: 3px;
}

QTableWidget {
    background-color: #424242;
    gridline-color: #555555;
}
"""

    light_theme = """QWidget {
    background-color: #F5F5F5;
    color: #000000;
}

QPushButton {
    background-color: #EEEEEE;
    border: 1px solid #CCCCCC;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #E0E0E0;
}

QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    padding: 5px;
    border-radius: 3px;
}

QTableWidget {
    background-color: #FFFFFF;
    gridline-color: #CCCCCC;
}
"""

    with open("styles/dark_theme.qss", "w") as f:
        f.write(dark_theme)
    print("✅ Dark theme créé")

    with open("styles/light_theme.qss", "w") as f:
        f.write(light_theme)
    print("✅ Light theme créé")


def download_font():
    """Télécharge une police libre de droit"""
    font_url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
    try:
        print("Téléchargement de la police...")
        urllib.request.urlretrieve(font_url, "fonts/custom_font.ttf")
        print("✅ Police téléchargée")
    except Exception as e:
        print(f"❌ Erreur téléchargement police: {e}")
        # Créer un fichier vide comme fallback
        with open("fonts/custom_font.ttf", "wb") as f:
            f.write(b"")
        print("🔄 Fichier vide créé à la place")


def main():
    print("=== Génération des ressources Liris ===\n")

    # Créer les dossiers
    create_directories()
    print()

    # Générer les icônes
    print("Génération des icônes...")
    generate_all_icons()
    print()

    # Créer les images
    print("Génération des images...")
    create_images()
    print()

    # Créer les styles
    print("Génération des styles...")
    create_qss_files()
    print()

    # Télécharger la police
    print("Téléchargement de la police...")
    download_font()
    print()

    print("✨ Toutes les ressources ont été générées avec succès!")
    print("\nVous pouvez maintenant compiler les ressources avec:")
    print("python compile_resources.py")


if __name__ == "__main__":
    main()