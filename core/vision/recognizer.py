# core/vision/recognizer.py
import pytesseract
import cv2
import numpy as np
import os
import platform
import subprocess
from utils.logger import logger
from utils.exceptions import OCRError


class TextRecognizer:
    """
    Classe pour la reconnaissance de texte dans les images
    avec Tesseract OCR
    """

    def __init__(self, tesseract_path=None):
        """
        Initialise le reconnaisseur de texte

        Args:
            tesseract_path (str, optional): Chemin vers l'exécutable Tesseract
        """
        # Configuration du chemin Tesseract
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Essayer de détecter automatiquement Tesseract
            self._setup_tesseract_path()

        logger.info("Initialisation du reconnaisseur de texte (Tesseract OCR)")

        # Vérifier que Tesseract est bien configuré
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Version de Tesseract: {version}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Tesseract OCR: {str(e)}")
            logger.warning("La reconnaissance OCR pourrait ne pas fonctionner correctement")
            logger.warning("Assurez-vous que Tesseract est installé et accessible dans le PATH")

    def _setup_tesseract_path(self):
        """
        Configure automatiquement le chemin vers Tesseract OCR
        """
        # Chemins courants pour Tesseract
        possible_paths = []

        system = platform.system().lower()

        if system == 'windows':
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\danie\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
            ]
        elif system == 'darwin':  # macOS
            possible_paths = [
                '/usr/local/bin/tesseract',
                '/opt/homebrew/bin/tesseract'
            ]
        else:  # Linux/Unix
            possible_paths = [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract'
            ]

        # Essayer de trouver Tesseract dans le PATH d'abord
        try:
            subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
            logger.info("Tesseract trouvé dans le PATH")
            return
        except:
            pass

        # Essayer les chemins possibles
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract trouvé à: {path}")
                return

        logger.warning("Tesseract non trouvé automatiquement. Assurez-vous qu'il est installé.")

    def recognize_text(self, image, roi=None):
        """
        Reconnaît le texte dans l'image donnée

        Args:
            image (numpy.ndarray): Image à analyser
            roi (tuple, optional): Région d'intérêt (x, y, width, height)

        Returns:
            str: Texte reconnu
        """
        try:
            # Si une région d'intérêt est spécifiée, extraire cette partie de l'image
            if roi:
                x, y, width, height = roi
                image = image[y:y + height, x:x + width]

            # Prétraitement de l'image pour améliorer la reconnaissance
            preprocessed = self._preprocess_image(image)

            # Configuration pour Tesseract
            config = '--oem 3 --psm 11'  # Mode de segmentation automatique

            # Reconnaissance du texte
            text = pytesseract.image_to_string(preprocessed, lang='fra+eng', config=config)

            # Nettoyage du texte
            text = text.strip()

            logger.debug(f"Texte reconnu: {text[:100]}..." if len(text) > 100 else f"Texte reconnu: {text}")
            return text

        except Exception as e:
            logger.error(f"Erreur lors de la reconnaissance de texte: {str(e)}")
            raise OCRError(f"Échec de la reconnaissance OCR: {str(e)}")

    def _preprocess_image(self, image):
        """
        Prétraite l'image pour améliorer la reconnaissance OCR

        Args:
            image (numpy.ndarray): Image à prétraiter

        Returns:
            numpy.ndarray: Image prétraitée
        """
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Redimensionnement (facultatif, mais peut améliorer la précision)
        scale_factor = 2
        resized = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

        # Réduction du bruit
        denoised = cv2.GaussianBlur(resized, (5, 5), 0)

        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        return binary

    def validate_placeholder(self, image, expected_placeholder, roi=None):
        """
        Vérifie si le placeholder reconnu correspond à celui attendu

        Args:
            image (numpy.ndarray): Image à analyser
            expected_placeholder (str): Texte du placeholder attendu
            roi (tuple, optional): Région d'intérêt (x, y, width, height)

        Returns:
            bool: True si le placeholder est validé, False sinon
        """
        try:
            recognized_text = self.recognize_text(image, roi)

            # Vérification de similarité (pas nécessairement une correspondance exacte)
            return self._text_similarity(recognized_text, expected_placeholder) > 0.7

        except Exception as e:
            logger.error(f"Erreur lors de la validation du placeholder: {str(e)}")
            return False

    def _text_similarity(self, text1, text2):
        """
        Calcule la similarité entre deux textes (mesure simple)

        Args:
            text1 (str): Premier texte
            text2 (str): Second texte

        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Normalisation des textes
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # Si l'un des textes est vide, renvoyer 0
        if not text1 or not text2:
            return 0

        # Si un texte est contenu dans l'autre
        if text1 in text2 or text2 in text1:
            return 0.9

        # Calcul de la distance de Levenshtein (mesure simple de similarité)
        # Note: Dans un projet réel, une implémentation plus robuste serait nécessaire
        distance = 0
        max_len = max(len(text1), len(text2))

        for i in range(min(len(text1), len(text2))):
            if text1[i] == text2[i]:
                distance += 1

        return distance / max_len if max_len > 0 else 0