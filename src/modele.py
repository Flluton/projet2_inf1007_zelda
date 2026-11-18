"""Module d'entraînement, d'évaluation, de sauvegarde et de prédiction du modèle ML."""

from __future__ import annotations

import functools
import json
import os
import time
from typing import Any, Callable, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.donnees import JeuDeDonnees, valider_recette_globale
from src.exceptions import DonneeInvalideError, FichierIntrouvableError, ModeleNonEntraineError


def chronometrer(fonction: Callable[..., Any]) -> Callable[..., Any]:
    """Décorateur (Chapitre 7) mesurant le temps d'exécution de l'entraînement."""

    @functools.wraps(fonction)
    def enveloppe(*args: Any, **kwargs: Any) -> Any:
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        fin = time.perf_counter()
        if args and hasattr(args[0], "_dernier_temps_entrainement"):
            args[0]._dernier_temps_entrainement = round(fin - debut, 4)
        return resultat

    return enveloppe


def calculer_rmse_numpy(y_vrai: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcule le RMSE de manière vectorisée avec NumPy (sans boucle Python)."""
    if y_vrai.shape != y_pred.shape or y_vrai.size == 0:
        raise DonneeInvalideError("Les tableaux y_vrai et y_pred doivent avoir la même taille non nulle.")
    return float(np.sqrt(np.mean((y_vrai - y_pred) ** 2)))


class ModeleRecetteZelda:
    """Encapsule le pipeline scikit-learn, l'évaluation et la persistance joblib/JSON."""

    COLONNES_NUMERIQUES = [
        "nb_viandes",
        "nb_legumes",
        "nb_champignons",
        "nb_assaisonnements",
    ]
    COLONNES_CATEGORIELLES = ["effet_special", "mode_cuisson", "lune_de_sang"]

    def __init__(self, random_state: int = 42) -> None:
        self._random_state = random_state
        self._pipeline: Pipeline | None = None
        self._metadonnees: Dict[str, Any] = {}
        self._dernier_temps_entrainement: float = 0.0

    @property
    def metadonnees(self) -> Dict[str, Any]:
        return dict(self._metadonnees)

    @property
    def temps_entrainement(self) -> float:
        return self._dernier_temps_entrainement

    def _construire_pipeline(self) -> Pipeline:
        preprocesseur = ColumnTransformer(
            transformers=[
                ("num", "passthrough", self.COLONNES_NUMERIQUES),
                ("cat", OneHotEncoder(handle_unknown="ignore"), self.COLONNES_CATEGORIELLES),
            ]
        )
        regresseur = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self._random_state,
        )
        return Pipeline(steps=[("preprocesseur", preprocesseur), ("regresseur", regresseur)])

    @chronometrer
    def entrainer_et_evaluer(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, float]:
        """Sépare les données, évalue un modèle de référence et entraîne le modèle final."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self._random_state
        )

        reference = DummyRegressor(strategy="mean")
        reference.fit(X_train, y_train)
        y_pred_ref = reference.predict(X_test)
        rmse_ref = calculer_rmse_numpy(y_test, y_pred_ref)
        r2_ref = float(r2_score(y_test, y_pred_ref))

        self._pipeline = self._construire_pipeline()
        self._pipeline.fit(X_train, y_train)
        y_pred = self._pipeline.predict(X_test)

        rmse_modele = calculer_rmse_numpy(y_test, y_pred)
        rmse_sklearn = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2_modele = float(r2_score(y_test, y_pred))

        self._metadonnees = {
            "modele": "RandomForestRegressor",
            "cible": JeuDeDonnees.COLONNE_CIBLE,
            "colonnes_entree": JeuDeDonnees.COLONNES_ENTREE,
            "variables_numeriques": {
                col: {"min": 0, "max": 5} for col in self.COLONNES_NUMERIQUES
            },
            "variables_categorielles": {
                col: sorted(X[col].unique().tolist()) for col in self.COLONNES_CATEGORIELLES
            },
            "metriques": {
                "rmse_reference": round(rmse_ref, 4),
                "r2_reference": round(r2_ref, 4),
                "rmse_modele": round(rmse_modele, 4),
                "rmse_sklearn_verif": round(rmse_sklearn, 4),
                "r2_modele": round(r2_modele, 4),
            },
            "distribution_cible": {
                "min": float(np.min(y)),
                "max": float(np.max(y)),
                "moyenne": round(float(np.mean(y)), 2),
                "valeurs_echantillon": [round(float(v), 2) for v in y[:1024]],
            },
        }
        return self._metadonnees["metriques"]

    def sauvegarder(self, chemin_modele: str, chemin_meta: str) -> None:
        """Sauvegarde le modèle entraîné (joblib) et ses métadonnées (JSON)."""
        if self._pipeline is None or not self._metadonnees:
            raise ModeleNonEntraineError("Impossible de sauvegarder : le modèle n'est pas entraîné.")

        for chemin in (chemin_modele, chemin_meta):
            dossier = os.path.dirname(chemin)
            if dossier:
                os.makedirs(dossier, exist_ok=True)

        joblib.dump(self._pipeline, chemin_modele)
        with open(chemin_meta, mode="w", encoding="utf-8") as fichier_json:
            json.dump(self._metadonnees, fichier_json, indent=4, ensure_ascii=False)

    def charger(self, chemin_modele: str, chemin_meta: str) -> None:
        """Charge un modèle existant et ses métadonnées depuis le disque."""
        if not os.path.exists(chemin_modele):
            raise FichierIntrouvableError(f"Modèle introuvable : {chemin_modele}")
        if not os.path.exists(chemin_meta):
            raise FichierIntrouvableError(f"Métadonnées introuvables : {chemin_meta}")

        self._pipeline = joblib.load(chemin_modele)
        with open(chemin_meta, mode="r", encoding="utf-8") as fichier_json:
            self._metadonnees = json.load(fichier_json)

    def predire(self, entree: Dict[str, Any]) -> Tuple[float, float]:
        """Prédit le nombre de cœurs régénérés et estime l'écart-type entre les arbres."""
        if self._pipeline is None:
            raise ModeleNonEntraineError("Le modèle doit être chargé ou entraîné avant de prédire.")

        valider_recette_globale(
            int(entree["nb_viandes"]),
            int(entree["nb_legumes"]),
            int(entree["nb_champignons"]),
            int(entree["nb_assaisonnements"]),
        )

        df_entree = pd.DataFrame([entree])[JeuDeDonnees.COLONNES_ENTREE]
        prediction = float(self._pipeline.predict(df_entree)[0])

        preproc = self._pipeline.named_steps["preprocesseur"]
        foret = self._pipeline.named_steps["regresseur"]
        X_trans = preproc.transform(df_entree)
        preds_arbres = np.array([arbre.predict(X_trans)[0] for arbre in foret.estimators_])
        incertitude = float(np.std(preds_arbres))

        return round(prediction, 2), round(incertitude, 2)

    def __str__(self) -> str:
        etat = "entraîné" if self._pipeline is not None else "non entraîné"
        return f"ModeleRecetteZelda({etat})"
