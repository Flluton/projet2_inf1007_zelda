"""Module d'interface graphique Tkinter (Volet 3) avec graphique Matplotlib et historique."""

from __future__ import annotations

import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.donnees import (
    Variable,
    VariableCategorielle,
    VariableNumerique,
    valider_recette_globale,
)
from src.exceptions import DonneeInvalideError, FichierIntrouvableError, ModeleNonEntraineError
from src.modele import ModeleRecetteZelda


class ApplicationZelda:
    """Application graphique permettant d'interroger le modèle de recettes Zelda BotW."""

    ETIQUETTES = {
        "nb_viandes": "Nombre de viandes (0-5)",
        "nb_legumes": "Nombre de légumes (0-5)",
        "nb_champignons": "Nombre de champignons (0-5)",
        "nb_assaisonnements": "Nombre d'assaisonnements (0-5)",
        "effet_special": "Effet spécial principal",
        "mode_cuisson": "Mode de cuisson",
        "lune_de_sang": "Lune de sang active",
    }

    def __init__(self, modele: ModeleRecetteZelda, chemin_historique: str) -> None:
        self._modele = modele
        self._chemin_historique = chemin_historique
        self._variables: List[Variable] = self._construire_variables()
        self._widgets_saisie: Dict[str, tk.Widget] = {}
        self._historique_memoire: List[Dict[str, str]] = []

        self._racine = tk.Tk()
        self._racine.title("Zelda BotW - Prédicteur de Cœurs Régénérés (INF1007)")
        self._racine.geometry("940x660")
        self._racine.resizable(True, True)

        self._construire_interface()
        self._charger_historique_existant()
        self._mettre_a_jour_graphique(prediction=None)

    def _construire_variables(self) -> List[Variable]:
        """Instancie dynamiquement les objets Variable à partir des métadonnées JSON."""
        meta = self._modele.metadonnees
        variables: List[Variable] = []

        for nom, bornes in meta["variables_numeriques"].items():
            variables.append(
                VariableNumerique(
                    nom=nom,
                    etiquette=self.ETIQUETTES.get(nom, nom),
                    minimum=bornes["min"],
                    maximum=bornes["max"],
                    entier=True,
                )
            )

        for nom, choix in meta["variables_categorielles"].items():
            variables.append(
                VariableCategorielle(
                    nom=nom,
                    etiquette=self.ETIQUETTES.get(nom, nom),
                    categories=choix,
                )
            )
        return variables

    def _construire_interface(self) -> None:
        """Construit les cadres de saisie, de résultat, de graphique et d'historique."""
        cadre_gauche = ttk.Frame(self._racine, padding=15)
        cadre_gauche.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(
            cadre_gauche,
            text="Composition du plat (max 5 ingrédients)",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        for var in self._variables:
            ttk.Label(cadre_gauche, text=var.etiquette).pack(anchor=tk.W, pady=(4, 1))
            if isinstance(var, VariableNumerique):
                entree = ttk.Spinbox(cadre_gauche, from_=var.minimum, to=var.maximum, width=25)
                entree.set("0")
                entree.pack(anchor=tk.W, pady=(0, 5))
                self._widgets_saisie[var.nom] = entree
            elif isinstance(var, VariableCategorielle):
                combo = ttk.Combobox(
                    cadre_gauche, values=var.categories, state="readonly", width=23
                )
                if var.categories:
                    combo.set(var.categories[0])
                combo.pack(anchor=tk.W, pady=(0, 5))
                self._widgets_saisie[var.nom] = combo

        btn_predire = ttk.Button(cadre_gauche, text="Prédire les cœurs", command=self._action_predire)
        btn_predire.pack(fill=tk.X, pady=(12, 8))

        self._label_resultat = ttk.Label(
            cadre_gauche,
            text="Résultat : en attente d'une recette...",
            font=("Helvetica", 11, "bold"),
            foreground="#1b5e20",
            wraplength=260,
        )
        self._label_resultat.pack(anchor=tk.W, pady=(5, 5))

        self._label_erreur = ttk.Label(
            cadre_gauche,
            text="",
            foreground="#b71c1c",
            wraplength=260,
        )
        self._label_erreur.pack(anchor=tk.W, pady=(2, 10))

        btn_historique = ttk.Button(
            cadre_gauche, text="Consulter l'historique", command=self._afficher_historique
        )
        btn_historique.pack(fill=tk.X, pady=(5, 5))

        meta_m = self._modele.metadonnees["metriques"]
        ttk.Label(
            cadre_gauche,
            text=f"Précision du modèle : R² = {meta_m['r2_modele']} | RMSE = {meta_m['rmse_modele']}",
            font=("Helvetica", 9),
            foreground="#555555",
        ).pack(side=tk.BOTTOM, anchor=tk.W)

        cadre_droit = ttk.Frame(self._racine, padding=10)
        cadre_droit.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._figure = Figure(figsize=(5.5, 4.5), dpi=100)
        self._ax = self._figure.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._figure, master=cadre_droit)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _mettre_a_jour_graphique(self, prediction: float | None) -> None:
        """Met à jour le graphique Matplotlib montrant la position de la prédiction."""
        self._ax.clear()
        echantillon = self._modele.metadonnees["distribution_cible"]["valeurs_echantillon"]

        self._ax.hist(
            echantillon,
            bins=20,
            color="#81c784",
            edgecolor="black",
            alpha=0.8,
            label=f"Distribution des recettes ({len(echantillon)} plats)",
        )
        if prediction is not None:
            self._ax.axvline(
                prediction,
                color="#d32f2f",
                linestyle="--",
                linewidth=2.5,
                label=f"Votre plat prédit : {prediction} cœurs",
            )

        self._ax.set_title("Position de votre plat dans la distribution des recettes")
        self._ax.set_xlabel("Cœurs régénérés")
        self._ax.set_ylabel("Fréquence")
        self._ax.legend(loc="upper right")
        self._ax.grid(axis="y", linestyle=":", alpha=0.6)
        self._figure.tight_layout()
        self._canvas.draw()

    def _action_predire(self) -> None:
        """Valide les saisies, lance la prédiction, met à jour le graphique et l'historique."""
        self._label_erreur.config(text="")
        try:
            valeurs_validees: Dict[str, object] = {}
            for var in self._variables:
                widget = self._widgets_saisie[var.nom]
                valeur_brute = widget.get()
                valeurs_validees[var.nom] = var.valider(valeur_brute)

            valider_recette_globale(
                int(valeurs_validees["nb_viandes"]),
                int(valeurs_validees["nb_legumes"]),
                int(valeurs_validees["nb_champignons"]),
                int(valeurs_validees["nb_assaisonnements"]),
            )

            coeurs, incertitude = self._modele.predire(valeurs_validees)
            self._label_resultat.config(
                text=f"Soins estimés : {coeurs} cœurs\n(Marge d'incertitude : ±{incertitude} cœurs)"
            )
            self._mettre_a_jour_graphique(prediction=coeurs)
            self._enregistrer_historique(valeurs_validees, coeurs)

        except DonneeInvalideError as exc:
            self._label_erreur.config(text=f"Erreur : {exc}")
        except (ModeleNonEntraineError, FichierIntrouvableError) as exc:
            self._label_erreur.config(text=f"Erreur du modèle : {exc}")

    def _charger_historique_existant(self) -> None:
        if not os.path.exists(self._chemin_historique):
            return
        with open(self._chemin_historique, mode="r", encoding="utf-8", newline="") as f:
            lecteur = csv.DictReader(f)
            self._historique_memoire = list(lecteur)

    def _enregistrer_historique(self, entree: Dict[str, object], prediction: float) -> None:
        dossier = os.path.dirname(self._chemin_historique)
        if dossier:
            os.makedirs(dossier, exist_ok=True)

        ligne = {
            "horodatage": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **{k: str(v) for k, v in entree.items()},
            "coeurs_predits": str(prediction),
        }
        fichier_existe = os.path.exists(self._chemin_historique)
        with open(self._chemin_historique, mode="a", encoding="utf-8", newline="") as f:
            ecrivain = csv.DictWriter(f, fieldnames=list(ligne.keys()))
            if not fichier_existe:
                ecrivain.writeheader()
            ecrivain.writerow(ligne)

        self._historique_memoire.append(ligne)

    def _afficher_historique(self) -> None:
        if not self._historique_memoire:
            messagebox.showinfo("Historique", "Aucune prédiction enregistrée pour le moment.")
            return

        fenetre = tk.Toplevel(self._racine)
        fenetre.title("Historique des prédictions")
        fenetre.geometry("820x320")

        colonnes = list(self._historique_memoire[0].keys())
        tableau = ttk.Treeview(fenetre, columns=colonnes, show="headings")
        for col in colonnes:
            tableau.heading(col, text=col)
            tableau.column(col, width=95, anchor=tk.CENTER)

        for item in self._historique_memoire:
            tableau.insert("", tk.END, values=[item[c] for c in colonnes])

        tableau.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def lancer(self) -> None:
        self._racine.mainloop()

    def __str__(self) -> str:
        return f"ApplicationZelda(variables={len(self._variables)})"
