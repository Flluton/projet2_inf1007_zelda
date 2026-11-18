# Fiche de décisions

Une ligne par choix important. La colonne « Validé par l'auxiliaire » est à remplir **après** chaque
validation (A à D) avec la date et sa réponse. Si l'auxiliaire suggère de changer d'avis, noter pourquoi
vous maintenez ou modifiez votre choix.

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Domaine (validation A) | Recettes de cuisine de Zelda BotW ; jeu vidéo/Pokémon sur Kaggle (plan B) | **Recettes Zelda BotW** : sujet qui nous intéresse ; l'application répond à « combien de cœurs ce plat soigne-t-il ? » | [À FAIRE — date] |
| Question posée à l'application | Filtre « cœurs voulus → plats possibles » ; prédiction « composition → cœurs soignés » | **Prédiction des cœurs** : un simple filtre sur un tableau n'est pas un modèle d'apprentissage et ne se prête pas à une évaluation train/test | [À FAIRE — date] |
| Jeu de données (validation B) | Données réelles du jeu (quelques centaines de recettes seulement, moins que les 500 lignes exigées) ; jeu synthétique simplifié | **Jeu synthétique de 1024 lignes généré avec Gemini** : dépasse 500 lignes, 7 entrées dont des numériques et des catégorielles. Limite : les valeurs sont simulées avec du bruit et non extraites du jeu ; c'est écrit clairement dans le README | [À FAIRE — date] |
| Catégories d'ingrédients | Un champ par ingrédient exact (trop de combinaisons) ; 4 catégories | **4 catégories** (viande, légumes, champignons, assaisonnement) : limite le nombre de combinaisons et garde une interface simple | [À FAIRE — date] |
| Règle de la marmite | Aucune limite ; maximum de 5 ingrédients | **1 à 5 ingrédients au total**, comme dans le jeu : erreur claire sinon (`valider_recette_globale`) | [À FAIRE — date] |
| Cible et métrique (validation C) | Régression sur les cœurs ; classification du nom du plat | **Régression sur `coeurs_regeneres`**. Métriques : RMSE (en cœurs, lisible) et R² (comparaison avec la référence) | [À FAIRE — date] |
| Modèle (validation C) | Régression linéaire ; forêt aléatoire | **Forêt aléatoire** (100 arbres, profondeur max 10) : gère les interactions entre catégories sans transformation et donne une marge d'incertitude (écart entre arbres). Référence : prédire la moyenne | [À FAIRE — date] |
| Séparation des données | 80/20 ; autre proportion | **80 % entraînement / 20 % test**, graine 42 pour la reproductibilité | — |
| Technologie d'interface (validation D) | Tkinter ; Streamlit ; Gradio | **Tkinter** : inclus avec Python, fonctionne en local sans installation, Matplotlib s'y intègre (`FigureCanvasTkAgg`) | [À FAIRE — date] |
| Outil du chapitre 7 | Décorateur ; générateur ; lambda | **Décorateur `@chronometrer`** (durée de l'entraînement) et **générateur `lire_csv_par_blocs`** (lecture du CSV par blocs) | — |
| Lancement des tests en CI | `pytest` seul ; `python -m pytest` + `pytest.ini` | **`pytest.ini` avec `pythonpath = .`** et `python -m pytest` dans la CI : `pytest` seul échouait (`No module named 'src'`) | — |
| Retour de l'enseignant : données générées par IA, « pas vraiment valides » | Remplacer par des données réelles (tableaux de Zelda Wiki, fichiers de recettes sur GitHub, autre jeu de données Kaggle/UCI) ; garder le jeu simulé et le déclarer clairement | **Garder le jeu simulé et le déclarer** (README, limites, journal d'IA). Raisons constatées : les pages de recettes n'étaient pas accessibles automatiquement ; un dépôt de recettes trouvé n'avait pas de licence visible ; étendre les quantités de façon estimée aurait aussi produit des valeurs simulées. [À COMPLÉTER : votre justification finale] | [À FAIRE — date et réponse de l'enseignant] |
