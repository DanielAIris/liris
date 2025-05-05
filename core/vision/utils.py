import cv2
import numpy as np
import pyautogui
from utils.logger import logger


def capture_screen(region=None):
    """
    Capture l'écran ou une région spécifique

    Args:
        region (tuple, optional): Région à capturer (x, y, width, height)

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

        return image_cv

    except Exception as e:
        logger.error(f"Erreur lors de la capture d'écran: {str(e)}")
        return None


def highlight_contours(image, contours, color=(0, 255, 0), thickness=2):
    """
    Surligne les contours détectés dans l'image

    Args:
        image (numpy.ndarray): Image sur laquelle dessiner
        contours (list): Liste des contours à surligner
        color (tuple, optional): Couleur RGB
        thickness (int, optional): Épaisseur du trait

    Returns:
        numpy.ndarray: Image avec les contours surlignés
    """
    # Créer une copie de l'image
    image_copy = image.copy()

    if not contours:
        return image_copy

    for contour_info in contours:
        contour = contour_info.get('contour')
        if contour is not None:
            cv2.drawContours(image_copy, [contour], -1, color, thickness)
        else:
            # Si le format est différent (x, y, w, h)
            x = contour_info.get('x')
            y = contour_info.get('y')
            w = contour_info.get('width')
            h = contour_info.get('height')

            if all(v is not None for v in [x, y, w, h]):
                cv2.rectangle(image_copy, (x, y), (x + w, y + h), color, thickness)

    return image_copy


def crop_roi(image, roi):
    """
    Extrait une région d'intérêt de l'image

    Args:
        image (numpy.ndarray): Image source
        roi (tuple): Coordonnées de la région (x, y, width, height)

    Returns:
        numpy.ndarray: Portion de l'image extraite
    """
    try:
        x, y, width, height = roi
        return image[y:y + height, x:x + width]
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de la région: {str(e)}")
        return None


def save_debug_image(image, filename):
    """
    Sauvegarde une image pour le débogage

    Args:
        image (numpy.ndarray): Image à sauvegarder
        filename (str): Nom du fichier

    Returns:
        bool: True si l'opération a réussi, False sinon
    """
    try:
        cv2.imwrite(filename, image)
        logger.debug(f"Image de débogage sauvegardée: {filename}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de l'image: {str(e)}")
        return False