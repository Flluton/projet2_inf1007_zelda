"""Tests du module src.entrainer (entraînement complet et sauvegarde)."""

import os

import pytest

from src.entrainer import CHEMIN_CSV, entrainer_et_sauvegarder
from src.exceptions import FichierIntrouvableError


def test_entrainer_et_sauvegarder_cree_les_fichiers(tmp_path):
    chemin_modele = tmp_path / "modele.joblib"
    chemin_meta = tmp_path / "meta.json"
    chemin_figure = tmp_path / "figures" / "exploration.png"

    metriques = entrainer_et_sauvegarder(
        chemin_csv=CHEMIN_CSV,
        chemin_modele=str(chemin_modele),
        chemin_meta=str(chemin_meta),
        chemin_figure=str(chemin_figure),
    )

    assert os.path.exists(chemin_modele)
    assert os.path.exists(chemin_meta)
    assert os.path.exists(chemin_figure)
    assert metriques["rmse_modele"] < metriques["rmse_reference"]


def test_entrainer_csv_absent(tmp_path):
    with pytest.raises(FichierIntrouvableError):
        entrainer_et_sauvegarder(
            chemin_csv=str(tmp_path / "absent.csv"),
            chemin_modele=str(tmp_path / "m.joblib"),
            chemin_meta=str(tmp_path / "m.json"),
            chemin_figure=str(tmp_path / "f.png"),
        )
