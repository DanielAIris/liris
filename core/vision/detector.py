import cv2
import numpy as np
from utils.logger import logger
from utils.exceptions import InterfaceDetectionError


class InterfaceDetector:
    """
    Classe pour détecter les éléments d'interface utilisateur à l'aide d'OpenCV
    """

    def __init__(self):
        """Initialise le détecteur d'interface"""
        logger.info("Initialisation du détecteur d'interface")

    def detect_elements(self, image, element_config):
        """
        Détecte les éléments d'interface selon la configuration donnée

        Args:
            image (numpy.ndarray): Image capturée de l'écran
            element_config (dict): Configuration de l'élément à détecter

        Returns:
            list: Liste des contours détectés
        """
        try:
            detection_method = element_config.get('detection', {}).get('method')

            if detection_method == 'findContour':
                return self._detect_by_contour(image, element_config)
            else:
                logger.warning(f"Méthode de détection inconnue: {detection_method}")
                return []

        except Exception as e:
            logger.error(f"Erreur lors de la détection des éléments: {str(e)}")
            raise InterfaceDetectionError(f"Échec de la détection: {str(e)}")

    def _detect_by_contour(self, image, element_config):
        """
        Détecte les éléments en utilisant la méthode findContour d'OpenCV

        Args:
            image (numpy.ndarray): Image capturée
            element_config (dict): Configuration de l'élément

        Returns:
            list: Liste des contours détectés avec leurs coordonnées
        """
        try:
            # Conversion de l'image en HSV pour une meilleure détection des couleurs
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Récupération des plages de couleurs de la configuration
            color_range = element_config.get('detection', {}).get('color_range', {})
            lower_color = np.array(color_range.get('lower', [0, 0, 0]))
            upper_color = np.array(color_range.get('upper', [255, 255, 255]))

            # Création du masque basé sur la plage de couleurs
            mask = cv2.inRange(hsv, lower_color, upper_color)

            # Trouver les contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filtrer les contours par taille
            min_area = element_config.get('detection', {}).get('min_area', 100)
            filtered_contours = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    filtered_contours.append({
                        'contour': contour,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'area': area
                    })

            logger.debug(f"Détecté {len(filtered_contours)} contours pour l'élément {element_config.get('type')}")
            return filtered_contours

        except Exception as e:
            logger.error(f"Erreur dans la détection par contour: {str(e)}")
            raise InterfaceDetectionError(f"Échec de la détection par contour: {str(e)}")

    def get_best_match(self, contours, target_type=None):
        """
        Retourne le meilleur contour correspondant au type d'élément cible

        Args:
            contours (list): Liste des contours détectés
            target_type (str, optional): Type d'élément recherché

        Returns:
            dict: Le meilleur contour correspondant
        """
        if not contours:
            return None

        # Tri des contours par taille
        sorted_contours = sorted(contours, key=lambda x: x['area'], reverse=True)

        if target_type == 'button':
            # Pour les boutons, privilégier les formes plus carrées
            for contour in sorted_contours:
                ratio = contour['width'] / contour['height'] if contour['height'] != 0 else 0
                if 0.5 <= ratio <= 2.0:  # Ratio largeur/hauteur entre 0.5 et 2.0
                    return contour

        # Par défaut, retourner le plus grand contour
        return sorted_contours[0]