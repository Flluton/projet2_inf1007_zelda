"""Module d'entraînement : prépare les données, entraîne, évalue et sauvegarde le modèle.

Lancement : ``python -m src.entrainer``
"""

from __future__ import annotations

import os
from typing import Dict

from src.donnees import JeuDeDonnees
from src.modele import ModeleRecetteZelda

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_CSV = os.path.join(RACINE, "donnees", "recettes_zelda_botw.csv")
CHEMIN_MODELE = os.path.join(RACINE, "modeles", "modele_recettes.joblib")
CHEMIN_META = os.path.join(RACINE, "modeles", "metadonnees.json")
CHEMIN_FIGURE = os.path.join(RACINE, "figures", "exploration.png")
CHEMIN_HISTORIQUE = os.path.join(RACINE, "historique", "historique_predictions.csv")


def entrainer_et_sauvegarder(
    chemin_csv: str = CHEMIN_CSV,
    chemin_modele: str = CHEMIN_MODELE,
    chemin_meta: str = CHEMIN_META,
    chemin_figure: str = CHEMIN_FIGURE,
) -> Dict[str, float]:
    """Charge le CSV, produit le graphique d'exploration, entraîne et sauvegarde le modèle.

    Args:
        chemin_csv: Chemin du jeu de données.
        chemin_modele: Où écrire le modèle (joblib).
        chemin_meta: Où écrire les métadonnées (JSON).
        chemin_figure: Où écrire le graphique d'exploration (PNG).

    Returns:
        Le dictionnaire des métriques (référence et modèle).

    Raises:
        FichierIntrouvableError: Si le CSV est absent.
        DonneeInvalideError: Si le CSV ne contient pas les colonnes attendues.
    """
    jeu = JeuDeDonnees(chemin_csv)
    jeu.charger_et_nettoyer()
    jeu.generer_graphique_exploration(chemin_figure)
    X, y = jeu.obtenir_xy()

    modele = ModeleRecetteZelda()
    metriques = modele.entrainer_et_evaluer(X, y)
    modele.sauvegarder(chemin_modele, chemin_meta)
    return metriques


if __name__ == "__main__":
    resultats = entrainer_et_sauvegarder()
    print("Modèle entraîné et sauvegardé.")
    for nom, valeur in resultats.items():
        print(f"  {nom} : {valeur}")
