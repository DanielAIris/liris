import os
import time
import pyautogui
import cv2
import numpy as np
from datetime import datetime
from utils.logger import logger
from utils.exceptions import InteractionError


class ScreenManager:
    """
    Classe pour gérer les captures d'écran et leur analyse
    """

    def __init__(self, screenshots_dir=None):
        """
        Initialise le gestionnaire d'écran

        Args:
            screenshots_dir (str, optional): Répertoire pour les captures d'écran
        """
        logger.info("Initialisation du gestionnaire d'écran")

        # Définir le répertoire de captures d'écran
        if screenshots_dir:
            self.screenshots_dir = screenshots_dir
        else:
            self.screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                                "screenshots")

        # Créer le répertoire s'il n'existe pas
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def capture_screen(self, region=None, save=False, filename=None):
        """
        Capture l'écran ou une région spécifique

        Args:
            region (tuple, optional): Région à capturer (x, y, width, height)
            save (bool): Sauvegarder la capture
            filename (str, optional): Nom du fichier pour la sauvegarde

        Returns:
            numpy.ndarray: Image capturée au format OpenCV
        """
        try:
            # Capture d'écran avec PyAutoGUI
            screenshot = pyautogui.screenshot(region=region)

            # Conversion de l'image PIL en tableau numpy
            image_np = np.array(screenshot)

            # Conversion des couleurs de RGB à BGR (format OpenCV)
            image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            if save:
                self.save_screenshot(image_cv, filename)

            return image_cv

        except Exception as e:
            logger.error(f"Erreur lors de la capture d'écran: {str(e)}")
            raise InteractionError(f"Échec de la capture d'écran: {str(e)}")

    def save_screenshot(self, image, filename=None):
        """
        Sauvegarde une capture d'écran

        Args:
            image (numpy.ndarray): Image à sauvegarder
            filename (str, optional): Nom du fichier

        Returns:
            str: Chemin du fichier sauvegardé
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            filepath = os.path.join(self.screenshots_dir, filename)
            cv2.imwrite(filepath, image)

            logger.debug(f"Capture d'écran sauvegardée: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la capture: {str(e)}")
            raise InteractionError(f"Échec de la sauvegarde: {str(e)}")

    def monitor_screen_for_changes(self, region=None, timeout=30, interval=1.0, threshold=0.95):
        """
        Surveille l'écran pour détecter des changements

        Args:
            region (tuple, optional): Région à surveiller (x, y, width, height)
            timeout (int): Durée maximale de surveillance (secondes)
            interval (float): Intervalle entre les captures
            threshold (float): Seuil de similarité (0.0-1.0)

        Returns:
            bool: True si des changements sont détectés, False si timeout
        """
        try:
            start_time = time.time()

            # Capture initiale
            previous_image = self.capture_screen(region)

            while time.time() - start_time < timeout:
                time.sleep(interval)

                # Nouvelle capture
                current_image = self.capture_screen(region)

                # Calcul de la similarité
                similarity = self._compare_images(previous_image, current_image)

                # Si les images sont suffisamment différentes
                if similarity < threshold:
                    logger.debug(f"Changement détecté (similarité: {similarity:.2f})")
                    return True

                previous_image = current_image

            logger.debug(f"Aucun changement détecté pendant {timeout} secondes")
            return False

        except Exception as e:
            logger.error(f"Erreur lors de la surveillance de l'écran: {str(e)}")
            raise InteractionError(f"Échec de la surveillance: {str(e)}")

    def _compare_images(self, img1, img2):
        """
        Compare deux images et retourne leur degré de similarité

        Args:
            img1 (numpy.ndarray): Première image
            img2 (numpy.ndarray): Seconde image

        Returns:
            float: Score de similarité (0.0-1.0)
        """
        try:
            # Redimensionner si les dimensions ne correspondent pas
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

            # Conversion en niveaux de gris
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Calcul de la similarité (méthode de corrélation)
            score, _ = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)

            return float(score)

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison des images: {str(e)}")
            return 0.0

    def detect_error_message(self, image, error_templates_dir=None):
        """
        Détecte si une erreur est présente à l'écran

        Args:
            image (numpy.ndarray): Image à analyser
            error_templates_dir (str, optional): Répertoire des templates d'erreur

        Returns:
            tuple: (bool, str) - Erreur détectée et message
        """
        # Cette méthode pourrait être implémentée pour détecter les messages d'erreur
        # communs dans les interfaces d'IA (par ex. "limite atteinte", "erreur")
        # en utilisant soit la reconnaissance de texte, soit la correspondance de motifs

        # Pour l'instant, une implémentation simplifiée
        return False, ""