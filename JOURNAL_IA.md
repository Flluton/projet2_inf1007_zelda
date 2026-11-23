# Journal d'utilisation de l'IA

Outils utilisés : **Claude** (Anthropic) et **Gemini** (Google). Nous restons responsables de chaque ligne remise.
Les cases [À COMPLÉTER] sont à remplir par l'équipe, car elles dépendent de ce que vous avez réellement fait.

| # | Outil | Ce que nous avons demandé | Réponse reçue | Vérification faite | Décision |
|---|---|---|---|---|---|
| 1 | Claude | Résumer l'énoncé du Projet 2 (long et compliqué) | Un résumé structuré : objectif, 3 volets, exigences par chapitre, validations, livrables, barème | Comparaison avec le PDF de l'énoncé [À COMPLÉTER : confirmer que vous avez relu le PDF] | Gardé comme aide-mémoire ; l'énoncé fait foi |
| 3 | Claude | Combien de combinaisons possibles, et comment représenter la marmite ? | Les répétitions d'ingrédients donnent largement plus de 500 lignes ; mise en garde sur la cible calculée par formule et sur la fuite d'information (cœurs après cuisson) |  | Gardé : 4 catégories, cible = cœurs régénérés |
| 4 | Gemini | Fichier csv et code | Aide pour le code Python (répartition des modules, class et fonctions, tests), CSV de 1024 lignes générés avec des données existantes mais en le reformatant pour correspondre au format de notre projet, JSON de métadonnées | Tests lancés par Claude dans son environnement : 10 sur 10 passent avec `python -m pytest`. [À COMPLÉTER : vérification faite sur votre machine] | **Modifié** : remplacement de `except Exception` par des exceptions précises, suppression des « 1024 » écrits en dur |

