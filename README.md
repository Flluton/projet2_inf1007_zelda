# Zelda BotW — Prédicteur de cœurs régénérés (INF1007, Projet 2)

Application Python avec interface graphique (Tkinter) qui **prédit combien de cœurs un plat soigne**
dans *The Legend of Zelda: Breath of the Wild*, à partir de sa composition (viandes, légumes,
champignons, assaisonnements), de son mode de cuisson, d'un effet spécial et de la lune de sang.
Un modèle de forêt aléatoire est entraîné une fois, sauvegardé, puis chargé par l'application.

**Équipe :** Paul Kanengieser 2456864 et Otsem-Pieurix Medegan 2461487— Polytechnique Montréal, INF1007, session A2026.

## Jeu de données

| | |
|---|---|
| Fichier | `donnees/recettes_zelda_botw.csv` (1024 lignes, 7 colonnes d'entrée + 1 cible) |
| Nature | **Jeu de données synthétique** : il n'a pas été extrait du jeu ni d'un site web. Il a été **généré avec l'outil d'IA Gemini** (Google) puis intégré au projet, et ses valeurs contiennent une part de bruit aléatoire. [À COMPLÉTER : consigne donnée à Gemini et règles de génération utilisées] |
| Référence sur les mécaniques du jeu | Zelda Wiki, page « Food in Breath of the Wild » : <https://zeldawiki.wiki/wiki/Food_in_Breath_of_the_Wild> (texte sous licence GFDL). Elle sert de **référence pour comprendre la cuisine du jeu** ; les valeurs du CSV n'en sont pas extraites. [À CONFIRMER : date de consultation] |
| Droits | Le jeu *Zelda: Breath of the Wild* appartient à Nintendo. Le fichier ne contient aucune donnée personnelle et, à notre connaissance, aucun contenu copié d'un site ; il a été produit pour ce projet pédagogique. |

- **Entrées numériques** : `nb_viandes`, `nb_legumes`, `nb_champignons`, `nb_assaisonnements` (0 à 5 chacune, **5 ingrédients maximum au total**).
- **Entrées catégorielles** : `effet_special` (7 valeurs), `mode_cuisson` (3), `lune_de_sang` (Oui/Non).
- **Cible** : `coeurs_regeneres` (nombre décimal) — problème de **régression**.
- Les ingrédients du jeu sont regroupés en 4 catégories pour limiter le nombre de combinaisons.

## Installation et lancement

Python 3.10 ou plus récent. Tkinter est inclus avec Python (sous Linux : `sudo apt install python3-tk`).

```bash
git clone <lien-du-depot>
cd projet_inf1007_zelda
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux : source .venv/bin/activate)
pip install -r requirements.txt

python -m src.main              # lance l'application
```

Commandes utiles :

```bash
python -m src.entrainer         # ré-entraîne le modèle et le sauvegarde dans modeles/
python -m pytest                # lance les tests
python -m coverage run --source=src -m pytest && python -m coverage report
```

Le modèle de `modeles/` a été entraîné avec scikit-learn 1.9.1. Si votre version diffère et que
le chargement échoue ou affiche un avertissement, relancez `python -m src.entrainer`.
Au premier lancement, si `modeles/` est vide, `main.py` entraîne le modèle automatiquement.

## Utilisation

1. Choisir le nombre d'ingrédients de chaque catégorie (0 à 5), l'effet, le mode de cuisson et la lune de sang.
2. Cliquer sur **Prédire les cœurs** : le résultat s'affiche avec une marge d'incertitude
   (écart-type entre les arbres de la forêt) et le graphique montre où se situe le plat parmi les recettes.
3. Une saisie vide, non numérique, hors intervalle ou un total de plus de 5 ingrédients affiche un message d'erreur clair.
4. **Consulter l'historique** ouvre toutes les prédictions (enregistrées dans `historique/historique_predictions.csv`).

## Résultats du modèle

Séparation 80 % entraînement / 20 % test, graine aléatoire fixée à 42. Modèle : `RandomForestRegressor`
(100 arbres, profondeur maximale 10). Référence : modèle trivial qui prédit toujours la moyenne.

| | RMSE (cœurs) | R² |
|---|---|---|
| Référence (moyenne) | 3,33 | −0,01 |
| Forêt aléatoire | **1,11** | **0,89** |

Le RMSE est calculé avec NumPy (`calculer_rmse_numpy`) et vérifié contre scikit-learn dans les tests.
Graphique d'exploration : `figures/exploration.png`.

### Limites (à lire avant d'interpréter le score)

- Les données sont **simulées par une IA** : le modèle apprend les règles du simulateur, pas celles du vrai jeu.
  Les valeurs (par exemple l'effet de la « lune de sang » ou du mode « gelé ») ne sont pas vérifiées
  contre les données réelles du jeu. Ce projet démontre une démarche (données → modèle → application) :
  il ne permet pas de conclure sur les vrais soins du jeu.
- Des lignes ont les mêmes entrées avec des cibles légèrement différentes (bruit simulé, écart-type d'environ 0,5 cœur),
  et 347 lignes partagent leurs entrées avec une autre ligne. Une partie du jeu de test est donc déjà « vue » à l'entraînement :
  le score est un peu optimiste.
- `effet_special` se choisit librement, alors que dans le vrai jeu il dépend des ingrédients précis :
  l'utilisateur peut composer des combinaisons impossibles dans le jeu.
- Les catégories regroupent des ingrédients différents : deux plats de même catégorie ont la même prédiction.

## Structure du code

```
projet_inf1007_zelda/
├── README.md, DECISIONS.md, JOURNAL_IA.md
├── requirements.txt, pytest.ini
├── .github/workflows/tests.yml     # lance pytest à chaque push
├── donnees/recettes_zelda_botw.csv
├── modeles/                        # modèle joblib + métadonnées JSON
├── figures/exploration.png         # graphique d'exploration (savefig)
├── src/
│   ├── donnees.py                  # classes Variable (abstraite) / VariableNumerique / VariableCategorielle, JeuDeDonnees, générateur CSV
│   ├── modele.py                   # ModeleRecetteZelda, décorateur @chronometrer, RMSE NumPy
│   ├── entrainer.py                # entraînement complet + sauvegarde
│   ├── exceptions.py               # DonneeInvalideError, FichierIntrouvableError, ModeleNonEntraineError
│   ├── interface.py                # ApplicationZelda (Tkinter + Matplotlib + historique)
│   └── main.py                     # point d'entrée
└── tests/                          # 12 tests pytest
```

- **POO** : `Variable` (abstraite) → `VariableNumerique` et `VariableCategorielle` (polymorphisme de `valider`) ;
  composition : `ApplicationZelda` contient un `ModeleRecetteZelda` et la liste de ses `Variable` ;
  attributs protégés (`_nom`, `_pipeline`…) et méthodes spéciales `__str__`, `__repr__`, `__len__`.
- **Outils du chapitre 7** : le décorateur `@chronometrer` mesure la durée de l'entraînement ;
  le générateur `lire_csv_par_blocs` lit le CSV par blocs de 256 lignes sans tout charger d'un coup.
- L'interface ne contient pas la logique : elle appelle `valider_recette_globale` et `ModeleRecetteZelda.predire`.

## Tests et couverture

12 tests pytest (cas usuels, cas limites, erreurs avec `pytest.raises`, flottants avec `pytest.approx`).
Couverture mesurée avec `coverage` : **57 % au total** ; environ **92 %** si l'on exclut
`interface.py` et `main.py` (interface graphique, non testée automatiquement).

## Références consultées

[À COMPLÉTER avec les pages réellement consultées. Pistes :]

- pandas : <https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html>
- scikit-learn : <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>
- Tkinter : <https://docs.python.org/3/library/tkinter.html>
- Zelda Wiki, « Food in Breath of the Wild » (mécaniques de cuisine, référence) : <https://zeldawiki.wiki/wiki/Food_in_Breath_of_the_Wild>
- Matplotlib dans Tkinter : <https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html>

## Documents du projet

- `DECISIONS.md` : fiche de décisions (options envisagées, choix, validations).
- `JOURNAL_IA.md` : journal d'utilisation des outils d'IA.
