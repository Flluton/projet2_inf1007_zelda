# Fiche de décisions

Une ligne par choix important. La colonne « Validé par l'auxiliaire » est à remplir **après** chaque
validation (A à D) avec la date et sa réponse. Si l'auxiliaire suggère de changer d'avis, noter pourquoi
vous maintenez ou modifiez votre choix.

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Domaine (validation A) | Recettes de cuisine de Zelda BotW ; jeu vidéo/Pokémon sur Kaggle (plan B) | **Recettes Zelda BotW** : sujet qui nous intéresse ; l'application répond à « combien de cœurs ce plat soigne-t-il ? » | 12 novembre |
| Jeu de données (validation B) | Données réelles du jeu (quelques centaines de recettes seulement, moins que les 500 lignes exigées) ; jeu synthétique simplifié | **Jeu synthétique de 1024 lignes généré avec Gemini** : dépasse 500 lignes, 7 entrées dont des numériques et des catégorielles. Limite : les valeurs sont simulées avec du bruit et non extraites du jeu ; c'est écrit clairement dans le README | 12 novembre |
| Cible et métrique (validation C) | Régression sur les cœurs ; classification du nom du plat | **Régression sur `coeurs_regeneres`**. Métriques : RMSE (en cœurs, lisible) et R² (comparaison avec la référence) | 20 novembre |
| Modèle (validation C) | Régression linéaire ; forêt aléatoire | **Forêt aléatoire** (100 arbres, profondeur max 10) : gère les interactions entre catégories sans transformation et donne une marge d'incertitude (écart entre arbres). Référence : prédire la moyenne | 20 novembre
| Technologie d'interface (validation D) | Tkinter ; Streamlit ; Gradio | **Tkinter** : inclus avec Python, fonctionne en local sans installation, Matplotlib s'y intègre (`FigureCanvasTkAgg`) | 20 novembre |

