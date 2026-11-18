"""Tests unitaires pour le module src.donnees et les exceptions."""

import os
import pytest
from src.donnees import (
    JeuDeDonnees,
    VariableCategorielle,
    VariableNumerique,
    lire_csv_par_blocs,
    valider_recette_globale,
)
from src.exceptions import DonneeInvalideError, FichierIntrouvableError


def test_variable_numerique_valide():
    var = VariableNumerique("nb_assaisonnements", "Assaisonnements", 0, 5, entier=True)
    assert var.valider("3") == 3
    assert var.valider(0) == 0
    assert var.valider(5) == 5


def test_variable_numerique_erreurs():
    var = VariableNumerique("nb_viandes", "Viandes", 0, 5, entier=True)
    with pytest.raises(DonneeInvalideError):
        var.valider("")
    with pytest.raises(DonneeInvalideError):
        var.valider("abc")
    with pytest.raises(DonneeInvalideError):
        var.valider(6)
    with pytest.raises(DonneeInvalideError):
        var.valider(-1)
    with pytest.raises(DonneeInvalideError):
        var.valider(2.5)


def test_variable_categorielle_valide_et_erreur():
    var = VariableCategorielle("mode_cuisson", "Cuisson", ["Marmite", "Feu_de_camp", "Gele"])
    assert var.valider("Marmite") == "Marmite"
    with pytest.raises(DonneeInvalideError):
        var.valider("Micro_ondes")
    with pytest.raises(DonneeInvalideError):
        var.valider("")


def test_valider_recette_globale_limites():
    assert valider_recette_globale(2, 1, 1, 1) == 5
    assert valider_recette_globale(0, 0, 0, 1) == 1
    with pytest.raises(DonneeInvalideError):
        valider_recette_globale(0, 0, 0, 0)
    with pytest.raises(DonneeInvalideError):
        valider_recette_globale(2, 2, 1, 1)


def test_chargement_csv_et_fichier_absent(tmp_path):
    with pytest.raises(FichierIntrouvableError):
        list(lire_csv_par_blocs("fichier_inexistant.csv"))

    chemin_csv = os.path.join("donnees", "recettes_zelda_botw.csv")
    jeu = JeuDeDonnees(chemin_csv)
    df = jeu.charger_et_nettoyer()
    assert len(df) >= 500
    assert "nb_assaisonnements" in df.columns
    assert "coeurs_regeneres" in df.columns

    img_path = tmp_path / "explo.png"
    jeu.generer_graphique_exploration(str(img_path))
    assert img_path.exists()
