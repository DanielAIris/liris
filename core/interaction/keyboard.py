import time
import pyautogui
from utils.logger import logger
from utils.exceptions import InteractionError


class KeyboardController:
    """
    Classe pour contrôler le clavier à l'aide de PyAutoGUI
    """

    def __init__(self, typing_speed='normal'):
        """
        Initialise le contrôleur de clavier

        Args:
            typing_speed (str): Vitesse de frappe ('slow', 'normal', 'fast')
        """
        logger.info("Initialisation du contrôleur de clavier")

        # Configuration de la vitesse de frappe
        self.typing_speeds = {
            'slow': 0.1,
            'normal': 0.05,
            'fast': 0.01
        }

        self.typing_interval = self.typing_speeds.get(typing_speed, 0.05)

        # Désactiver le failsafe de PyAutoGUI (optionnel)
        pyautogui.FAILSAFE = True

    def type_text(self, text, interval=None):
        """
        Tape le texte avec la vitesse configurée

        Args:
            text (str): Texte à saisir
            interval (float, optional): Intervalle entre les frappes (secondes)

        Returns:
            bool: True si la saisie a réussi, False sinon
        """
        try:
            interval = interval if interval is not None else self.typing_interval
            pyautogui.write(text, interval=interval)
            logger.debug(f"Texte saisi: {text[:20]}{'...' if len(text) > 20 else ''}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la saisie de texte: {str(e)}")
            raise InteractionError(f"Échec de la saisie clavier: {str(e)}")

    def press_key(self, key):
        """
        Appuie sur une touche spécifique

        Args:
            key (str): Touche à appuyer (format PyAutoGUI)

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            pyautogui.press(key)
            logger.debug(f"Touche pressée: {key}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'appui sur la touche {key}: {str(e)}")
            raise InteractionError(f"Échec de l'appui sur la touche: {str(e)}")

    def hotkey(self, *keys):
        """
        Utilise une combinaison de touches

        Args:
            *keys: Liste des touches à appuyer simultanément

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            pyautogui.hotkey(*keys)
            logger.debug(f"Combinaison de touches utilisée: {' + '.join(keys)}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'utilisation de la combinaison: {str(e)}")
            raise InteractionError(f"Échec de la combinaison de touches: {str(e)}")

    def clear_field(self):
        """
        Efface le contenu d'un champ (Ctrl+A puis Delete)

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            # Sélectionner tout
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)

            # Supprimer
            pyautogui.press('delete')
            logger.debug("Champ effacé")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'effacement du champ: {str(e)}")
            raise InteractionError(f"Échec de l'effacement: {str(e)}")

    def press_enter(self):
        """
        Appuie sur la touche Entrée

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.press_key('enter')

    def press_tab(self):
        """
        Appuie sur la touche Tab

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.press_key('tab')

    def copy_to_clipboard(self):
        """
        Copie la sélection dans le presse-papiers (Ctrl+C)

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.hotkey('ctrl', 'c')

    def paste_from_clipboard(self):
        """
        Colle le contenu du presse-papiers (Ctrl+V)

        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.hotkey('ctrl', 'v')