"""Point d'entrée de l'application : ``python -m src.main``."""

from __future__ import annotations

import os
import sys

from src.entrainer import (
    CHEMIN_HISTORIQUE,
    CHEMIN_META,
    CHEMIN_MODELE,
    entrainer_et_sauvegarder,
)
from src.exceptions import DonneeInvalideError, FichierIntrouvableError
from src.interface import ApplicationZelda
from src.modele import ModeleRecetteZelda


def charger_ou_entrainer_modele() -> ModeleRecetteZelda:
    """Charge le modèle sauvegardé ; l'entraîne une première fois s'il est absent.

    Returns:
        Un modèle prêt à prédire.

    Raises:
        FichierIntrouvableError: Si le CSV de données est absent.
    """
    if not (os.path.exists(CHEMIN_MODELE) and os.path.exists(CHEMIN_META)):
        print("Aucun modèle sauvegardé : entraînement initial...")
        entrainer_et_sauvegarder()
    modele = ModeleRecetteZelda()
    modele.charger(CHEMIN_MODELE, CHEMIN_META)
    return modele


def main() -> int:
    """Démarre l'application graphique et renvoie un code de sortie."""
    try:
        modele = charger_ou_entrainer_modele()
        application = ApplicationZelda(modele, CHEMIN_HISTORIQUE)
    except (FichierIntrouvableError, DonneeInvalideError) as exc:
        print(f"Erreur au démarrage : {exc}", file=sys.stderr)
        return 1
    application.lancer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
