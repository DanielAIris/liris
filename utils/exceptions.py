# utils/exceptions.py

class AIAutomationError(Exception):
    """Classe de base pour toutes les exceptions de l'application"""
    pass

class ConfigurationError(AIAutomationError):
    """Erreur liée à la configuration de l'application"""
    pass

class InterfaceDetectionError(AIAutomationError):
    """Erreur lors de la détection des éléments d'interface"""
    pass

class OCRError(AIAutomationError):
    """Erreur lors de la reconnaissance de texte par OCR"""
    pass

class InteractionError(AIAutomationError):
    """Erreur lors de l'interaction avec l'interface"""
    pass

class APILimitReachedError(AIAutomationError):
    """Limite d'utilisation de l'API atteinte"""
    pass

class DatabaseError(AIAutomationError):
    """Erreur liée à la base de données"""
    pass

class SchedulingError(AIAutomationError):
    """Erreur dans la planification des tâches"""
    pass

class PromptTemplateError(AIAutomationError):
    """Erreur dans les templates de prompts"""
    pass

class ExportError(AIAutomationError):
    """Erreur lors de l'exportation des données"""
    pass

class BrainstormingError(AIAutomationError):
    """Erreur spécifique au brainstorming multi-IA"""
    pass

class AnnotationError(AIAutomationError):
    """Erreur lors de l'annotation de datasets"""
    pass

class DatasetError(AIAutomationError):
    """Erreur liée aux datasets"""
    pass

class PromptError(AIAutomationError):
    """Erreur liée aux prompts"""
    pass

class ContentAnalysisError(AIAutomationError):
    """Erreur lors de l'analyse de contenu"""
    pass

class ValidationError(AIAutomationError):
    """Erreur de validation des données"""
    pass

class ResourceError(AIAutomationError):
    """Erreur liée aux ressources (images, icônes, etc.)"""
    pass

class OrchestrationError(AIAutomationError):
    """Erreur d'orchestration des IA"""
    pass

class AITimeoutError(AIAutomationError):
    """Timeout lors des requêtes aux IA"""
    pass

class RateLimitExceeded(AIAutomationError):
    """Dépassement des limites de requêtes"""
    pass

class AIConnectionError(AIAutomationError):
    """Erreur de connexion aux IA"""
    pass

class VisionDetectionError(AIAutomationError):
    """Erreur de détection visuelle"""
    pass