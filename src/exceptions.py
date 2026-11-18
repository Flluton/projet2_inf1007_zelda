"""Module définissant les exceptions personnalisées de l'application."""


class ProjetZeldaError(Exception):
    """Classe de base pour toutes les exceptions liées au projet."""


class DonneeInvalideError(ProjetZeldaError):
    """Levée lorsqu'une donnée saisie ou lue est invalide ou hors limites."""


class FichierIntrouvableError(ProjetZeldaError):
    """Levée lorsqu'un fichier requis (CSV, modèle, métadonnées) est absent."""


class ModeleNonEntraineError(ProjetZeldaError):
    """Levée lorsqu'on tente d'utiliser ou sauvegarder un modèle non entraîné."""
