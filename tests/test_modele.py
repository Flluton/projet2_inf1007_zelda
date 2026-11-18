"""Tests unitaires pour le module src.modele (entraînement, NumPy, sauvegarde, prédiction)."""

import os
import numpy as np
import pytest
from src.donnees import JeuDeDonnees
from src.exceptions import DonneeInvalideError, FichierIntrouvableError, ModeleNonEntraineError
from src.modele import ModeleRecetteZelda, calculer_rmse_numpy


def test_calculer_rmse_numpy_coincide():
    y_vrai = np.array([2.0, 4.0, 6.0, 8.0])
    y_pred = np.array([2.5, 3.5, 6.5, 7.5])
    assert calculer_rmse_numpy(y_vrai, y_pred) == pytest.approx(0.5)


def test_calculer_rmse_numpy_invalide():
    with pytest.raises(DonneeInvalideError):
        calculer_rmse_numpy(np.array([1.0, 2.0]), np.array([1.0]))


def test_modele_non_entraine_erreurs():
    modele = ModeleRecetteZelda()
    with pytest.raises(ModeleNonEntraineError):
        modele.sauvegarder("m.joblib", "m.json")
    with pytest.raises(FichierIntrouvableError):
        modele.charger("absent.joblib", "absent.json")


def test_entrainement_sauvegarde_et_prediction(tmp_path):
    jeu = JeuDeDonnees(os.path.join("donnees", "recettes_zelda_botw.csv"))
    jeu.charger_et_nettoyer()
    X, y = jeu.obtenir_xy()

    modele = ModeleRecetteZelda(random_state=42)
    metriques = modele.entrainer_et_evaluer(X, y)

    assert metriques["rmse_modele"] == pytest.approx(metriques["rmse_sklearn_verif"])
    assert metriques["rmse_modele"] < metriques["rmse_reference"]
    assert metriques["r2_modele"] > 0.85
    assert modele.temps_entrainement >= 0.0

    chemin_m = tmp_path / "modele.joblib"
    chemin_j = tmp_path / "meta.json"
    modele.sauvegarder(str(chemin_m), str(chemin_j))

    modele_charge = ModeleRecetteZelda()
    modele_charge.charger(str(chemin_m), str(chemin_j))

    entree_valide = {
        "nb_viandes": 2,
        "nb_legumes": 1,
        "nb_champignons": 1,
        "nb_assaisonnements": 1,
        "effet_special": "Attaque",
        "mode_cuisson": "Marmite",
        "lune_de_sang": "Oui",
    }
    coeurs, incertitude = modele_charge.predire(entree_valide)
    assert coeurs > 5.0
    assert incertitude >= 0.0


def test_prediction_depassement_5_ingredients():
    jeu = JeuDeDonnees(os.path.join("donnees", "recettes_zelda_botw.csv"))
    jeu.charger_et_nettoyer()
    X, y = jeu.obtenir_xy()

    modele = ModeleRecetteZelda(random_state=42)
    modele.entrainer_et_evaluer(X, y)

    entree_invalide = {
        "nb_viandes": 2,
        "nb_legumes": 2,
        "nb_champignons": 1,
        "nb_assaisonnements": 1,
        "effet_special": "Aucun",
        "mode_cuisson": "Marmite",
        "lune_de_sang": "Non",
    }
    with pytest.raises(DonneeInvalideError):
        modele.predire(entree_invalide)
