class VoltaAPIExceptions(Exception):
    """Classe de base pour les erreurs de la lib."""
    pass

class APIError(VoltaAPIExceptions):
    """Levée quand l'API renvoie un code d'erreur HTTP."""
    pass