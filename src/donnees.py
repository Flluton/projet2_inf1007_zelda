"""Module de gestion, nettoyage et validation des données et variables."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Generator, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.exceptions import DonneeInvalideError, FichierIntrouvableError


class Variable(ABC):
    """Classe parente abstraite représentant une variable d'entrée du modèle."""

    def __init__(self, nom: str, etiquette: str) -> None:
        self._nom = nom
        self._etiquette = etiquette

    @property
    def nom(self) -> str:
        return self._nom

    @property
    def etiquette(self) -> str:
        return self._etiquette

    @abstractmethod
    def valider(self, valeur: Any) -> Any:
        """Valide et convertit la valeur saisie."""

    def __str__(self) -> str:
        return f"{self._etiquette} ({self._nom})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nom={self._nom!r}, etiquette={self._etiquette!r})"


class VariableNumerique(Variable):
    """Représente une variable d'entrée numérique bornée."""

    def __init__(
        self, nom: str, etiquette: str, minimum: float, maximum: float, entier: bool = True
    ) -> None:
        super().__init__(nom, etiquette)
        self._minimum = minimum
        self._maximum = maximum
        self._entier = entier

    @property
    def minimum(self) -> float:
        return self._minimum

    @property
    def maximum(self) -> float:
        return self._maximum

    def valider(self, valeur: Any) -> int | float:
        """Valide qu'une saisie est numérique et comprise dans [minimum, maximum]."""
        if valeur is None or str(valeur).strip() == "":
            raise DonneeInvalideError(f"Le champ '{self._etiquette}' ne peut pas être vide.")
        try:
            num = float(valeur)
        except (ValueError, TypeError) as exc:
            raise DonneeInvalideError(
                f"La valeur '{valeur}' pour '{self._etiquette}' doit être un nombre."
            ) from exc

        if np.isnan(num) or np.isinf(num):
            raise DonneeInvalideError(f"Valeur numérique invalide pour '{self._etiquette}'.")

        if self._entier:
            if not num.is_integer():
                raise DonneeInvalideError(
                    f"La valeur pour '{self._etiquette}' doit être un nombre entier."
                )
            num = int(num)

        if num < self._minimum or num > self._maximum:
            raise DonneeInvalideError(
                f"'{self._etiquette}' doit être entre {self._minimum} et {self._maximum} (reçu : {num})."
            )
        return num


class VariableCategorielle(Variable):
    """Représente une variable d'entrée catégorielle avec liste de choix autorisés."""

    def __init__(self, nom: str, etiquette: str, categories: List[str]) -> None:
        super().__init__(nom, etiquette)
        self._categories = list(categories)

    @property
    def categories(self) -> List[str]:
        return list(self._categories)

    def valider(self, valeur: Any) -> str:
        """Valide que la saisie appartient aux catégories autorisées."""
        if valeur is None or str(valeur).strip() == "":
            raise DonneeInvalideError(f"Veuillez sélectionner une option pour '{self._etiquette}'.")
        val_str = str(valeur).strip()
        if val_str not in self._categories:
            raise DonneeInvalideError(
                f"Valeur '{val_str}' invalide pour '{self._etiquette}'. "
                f"Choix autorisés : {', '.join(self._categories)}."
            )
        return val_str


def valider_recette_globale(
    nb_viandes: int,
    nb_legumes: int,
    nb_champignons: int,
    nb_assaisonnements: int,
) -> int:
    """Vérifie la règle métier de Zelda BotW : entre 1 et 5 ingrédients au total.

    Args:
        nb_viandes: Nombre de viandes (0 à 5).
        nb_legumes: Nombre de légumes (0 à 5).
        nb_champignons: Nombre de champignons (0 à 5).
        nb_assaisonnements: Nombre d'assaisonnements (0 à 5).

    Returns:
        Le nombre total d'ingrédients.

    Raises:
        DonneeInvalideError: Si le total est 0 ou dépasse 5.
    """
    total = nb_viandes + nb_legumes + nb_champignons + nb_assaisonnements
    if total == 0:
        raise DonneeInvalideError("Un plat doit contenir au moins 1 ingrédient.")
    if total > 5:
        raise DonneeInvalideError(
            f"La marmite est limitée à 5 ingrédients maximum au total (ici : {total})."
        )
    return total


def lire_csv_par_blocs(chemin_csv: str, taille_bloc: int = 256) -> Generator[pd.DataFrame, None, None]:
    """Générateur (Chapitre 7) lisant un fichier CSV par blocs pour économiser la mémoire."""
    if not os.path.exists(chemin_csv):
        raise FichierIntrouvableError(f"Le fichier CSV est introuvable : {chemin_csv}")

    with open(chemin_csv, mode="r", encoding="utf-8") as fichier:
        for bloc in pd.read_csv(fichier, chunksize=taille_bloc):
            yield bloc


class JeuDeDonnees:
    """Classe encapsulant le chargement, le nettoyage et l'exploration du jeu de données."""

    COLONNES_ENTREE = [
        "nb_viandes",
        "nb_legumes",
        "nb_champignons",
        "nb_assaisonnements",
        "effet_special",
        "mode_cuisson",
        "lune_de_sang",
    ]
    COLONNE_CIBLE = "coeurs_regeneres"

    def __init__(self, chemin_csv: str) -> None:
        self._chemin_csv = chemin_csv
        self._df: pd.DataFrame | None = None

    @property
    def donnees(self) -> pd.DataFrame:
        if self._df is None:
            raise DonneeInvalideError("Les données n'ont pas encore été chargées.")
        return self._df.copy()

    def charger_et_nettoyer(self) -> pd.DataFrame:
        """Charge le CSV via le générateur, supprime les valeurs manquantes/aberrantes."""
        if not os.path.exists(self._chemin_csv):
            raise FichierIntrouvableError(f"Fichier introuvable : {self._chemin_csv}")

        blocs = list(lire_csv_par_blocs(self._chemin_csv, taille_bloc=256))
        df = pd.concat(blocs, ignore_index=True)

        colonnes_requises = set(self.COLONNES_ENTREE + [self.COLONNE_CIBLE])
        if not colonnes_requises.issubset(df.columns):
            manquantes = colonnes_requises - set(df.columns)
            raise DonneeInvalideError(f"Colonnes manquantes dans le CSV : {manquantes}")

        df = df.dropna(subset=list(colonnes_requises)).copy()
        total_ing = (
            df["nb_viandes"]
            + df["nb_legumes"]
            + df["nb_champignons"]
            + df["nb_assaisonnements"]
        )
        df = df[(total_ing >= 1) & (total_ing <= 5) & (df[self.COLONNE_CIBLE] > 0)].copy()

        self._df = df.reset_index(drop=True)
        return self._df.copy()

    def obtenir_xy(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Sépare les caractéristiques X et la variable cible y sous forme de tableau NumPy."""
        df = self.donnees
        X = df[self.COLONNES_ENTREE].copy()
        y = df[self.COLONNE_CIBLE].to_numpy(dtype=float)
        return X, y

    def generer_graphique_exploration(self, chemin_sortie: str) -> str:
        """Génère et sauvegarde un graphique d'exploration (Volet 2, Étape 1)."""
        df = self.donnees
        dossier = os.path.dirname(chemin_sortie)
        if dossier:
            os.makedirs(dossier, exist_ok=True)

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

        axes[0].hist(df[self.COLONNE_CIBLE], bins=20, color="#2e7d32", edgecolor="black", alpha=0.85)
        axes[0].set_title(f"Distribution des cœurs régénérés ({len(df)} recettes)")
        axes[0].set_xlabel("Cœurs régénérés")
        axes[0].set_ylabel("Nombre de recettes")
        axes[0].grid(axis="y", linestyle="--", alpha=0.5)

        moyennes = df.groupby("mode_cuisson")[self.COLONNE_CIBLE].mean().sort_values()
        axes[1].bar(moyennes.index, moyennes.values, color=["#64b5f6", "#ffb74d", "#e57373"], edgecolor="black")
        axes[1].set_title("Cœurs moyens selon le mode de cuisson")
        axes[1].set_xlabel("Mode de cuisson")
        axes[1].set_ylabel("Moyenne des cœurs régénérés")
        axes[1].grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        fig.savefig(chemin_sortie, dpi=150)
        plt.close(fig)
        return chemin_sortie

    def __len__(self) -> int:
        return 0 if self._df is None else len(self._df)

    def __str__(self) -> str:
        return f"JeuDeDonnees({self._chemin_csv}, lignes={len(self)})"
