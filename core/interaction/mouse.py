import time
import pyautogui
import random
from utils.logger import logger
from utils.exceptions import InteractionError


class MouseController:
    """
    Classe pour contrôler la souris à l'aide de PyAutoGUI
    """

    def __init__(self, movement_style='direct'):
        """
        Initialise le contrôleur de souris

        Args:
            movement_style (str): Style de mouvement ('direct', 'human', 'eased')
        """
        logger.info("Initialisation du contrôleur de souris")

        self.movement_style = movement_style

        # Désactiver le failsafe de PyAutoGUI (optionnel, mais peut causer des problèmes)
        pyautogui.FAILSAFE = True

    def move_to(self, x, y, duration=0.5):
        """
        Déplace le curseur vers les coordonnées spécifiées

        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
            duration (float): Durée du mouvement en secondes

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            if self.movement_style == 'human':
                # Mouvement qui imite un humain (légèrement aléatoire)
                self._human_like_movement(x, y, duration)
            else:
                # Mouvement direct ou avec easing
                pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)

            logger.debug(f"Curseur déplacé vers: ({x}, {y})")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du déplacement du curseur: {str(e)}")
            raise InteractionError(f"Échec du déplacement de la souris: {str(e)}")

    def _human_like_movement(self, target_x, target_y, duration):
        """
        Effectue un mouvement de souris imitant un humain

        Args:
            target_x (int): Coordonnée X cible
            target_y (int): Coordonnée Y cible
            duration (float): Durée du mouvement
        """
        # Position actuelle
        start_x, start_y = pyautogui.position()

        # Calcul du nombre d'étapes
        steps = int(duration * 100)
        steps = max(steps, 10)

        for i in range(1, steps + 1):
            # Calcul de la position linéaire
            ratio = i / steps
            x = start_x + (target_x - start_x) * ratio
            y = start_y + (target_y - start_y) * ratio

            # Ajout d'un peu d'aléatoire pour un mouvement plus naturel
            if i > 1 and i < steps:
                deviation = (steps - i) / steps * 5  # Diminue avec l'approche
                x += random.uniform(-deviation, deviation)
                y += random.uniform(-deviation, deviation)

            # Déplacement
            pyautogui.moveTo(x, y, duration=duration / steps)

    def click(self, x=None, y=None, button='left', clicks=1, interval=0.1):
        """
        Clique à la position actuelle ou spécifiée

        Args:
            x (int, optional): Coordonnée X
            y (int, optional): Coordonnée Y
            button (str): Bouton de souris ('left', 'right', 'middle')
            clicks (int): Nombre de clics
            interval (float): Intervalle entre les clics

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            if x is not None and y is not None:
                # Déplacement puis clic
                self.move_to(x, y)
                time.sleep(0.1)  # Pause courte avant le clic

            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)

            pos_str = f"({x}, {y})" if x is not None and y is not None else "position actuelle"
            logger.debug(f"Clic ({button}, {clicks} fois) à {pos_str}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du clic: {str(e)}")
            raise InteractionError(f"Échec du clic: {str(e)}")

    def right_click(self, x=None, y=None):
        """
        Effectue un clic droit

        Args:
            x (int, optional): Coordonnée X
            y (int, optional): Coordonnée Y

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.click(x, y, button='right')

    def double_click(self, x=None, y=None):
        """
        Effectue un double-clic

        Args:
            x (int, optional): Coordonnée X
            y (int, optional): Coordonnée Y

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.click(x, y, clicks=2)

    def drag_to(self, start_x, start_y, end_x, end_y, duration=0.5, button='left'):
        """
        Effectue un glisser-déposer

        Args:
            start_x (int): Coordonnée X de départ
            start_y (int): Coordonnée Y de départ
            end_x (int): Coordonnée X d'arrivée
            end_y (int): Coordonnée Y d'arrivée
            duration (float): Durée du mouvement
            button (str): Bouton de souris à utiliser

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            # Déplacement vers le point de départ
            self.move_to(start_x, start_y)
            time.sleep(0.2)

            # Drag and drop
            pyautogui.dragTo(end_x, end_y, duration=duration, button=button)

            logger.debug(f"Glisser-déposer de ({start_x}, {start_y}) à ({end_x}, {end_y})")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du glisser-déposer: {str(e)}")
            raise InteractionError(f"Échec du glisser-déposer: {str(e)}")

    def scroll(self, amount):
        """
        Effectue un défilement vertical

        Args:
            amount (int): Quantité de défilement (positif = bas, négatif = haut)

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            pyautogui.scroll(amount)

            direction = "bas" if amount < 0 else "haut"
            logger.debug(f"Défilement vers le {direction} ({abs(amount)})")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du défilement: {str(e)}")
            raise InteractionError(f"Échec du défilement: {str(e)}")

    def get_current_position(self):
        """
        Récupère la position actuelle du curseur

        Returns:
            tuple: Coordonnées (x, y) du curseur
        """
        try:
            return pyautogui.position()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la position: {str(e)}")
            raise InteractionError(f"Échec de la récupération de position: {str(e)}")