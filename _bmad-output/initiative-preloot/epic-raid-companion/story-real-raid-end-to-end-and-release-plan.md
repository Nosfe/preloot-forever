---
title: 'Real raid end to end and release'
type: 'feature'
ticket: '7'
created: '2026-11-02'
status: 'in-progress'
baseline_revision: '644fed7'
route: 'hitl'
route_source: 'ticket'
context: []
---

## Intent

The owner runs the whole loop once in game: workbook snapshot, companion in Gargul, awards with treatments, Gargul Custom export, End raid import. The raid's export becomes 4.9's fixture, and the release is tagged `v2.0.0`. Forever is not out yet, so TBC Anniversary counts for the run (TOC has `Interface-BCC: 20506`); a short Forever load check follows at launch.

## Owner checklist (in game, one session)

**Préparation**
1. Copier le dossier `Gargul_Preloot/Gargul_Preloot` dans `Interface/AddOns` (remplace l'ancienne 1.1.0).
2. Classeur : Configuration > Rafraîchir le classeur ; Roster rempli ; Config *Version Wowhead* = `TBC` et *Serveur WCL* renseigné ; Configuration > Afficher le format d'export Gargul, coller la ligne dans Gargul (Export loot > Custom, décocher offspec et disenchanted).

**Chargement (5.1)**
3. L'addon apparaît et se charge avec Gargul, sans « périmé ». Une ligne `[Preloot]` résume les fonctions installées.
4. Raid > Démarrer dans le classeur, copier le Base64 ; Gargul Importer > bouton Preloot (une seule fois après réouverture) ou `/preloot import` ; le message donne le nombre de raiders.
5. Un snapshot modifié (un caractère changé) est refusé.

**Rolls et attributions (5.2, 5.5, 5.6)**
6. Un roll : colonnes Preloot après les 10 colonnes Gargul ; Ratio BiS identique au Roster.
7. Objet avec Statut IMPACT pour certaines spés : Impact affiché pour ces rollers seulement, vide pour les tanks.
8. Attribuer : la fenêtre de traitement s'ouvre, préremplie depuis le Statut ; choisir BIS/IMPACT/CLASS_BOUND/ALT ; le type de roll reste enregistré.
9. Deux attributions de suite : les colonnes se mettent à jour avant le roll suivant ; la ligne de chat apparaît pour BIS et IMPACT seulement.
10. Changer le traitement, changer le gagnant, supprimer une attribution : `/preloot list` suit chaque étape.

**Export et import (5.3, 4.9)**
11. Gargul Export loot (Custom) : chaque ligne a `raidId` et `treatment` remplis ; une attribution faite avant l'import du snapshot sort avec des valeurs vides.
12. Classeur : Raid > Terminer avec le lien WCL et l'export ; la prévisualisation montre les traitements ; les loots arrivent dans Awards.
13. M'envoyer : l'export Custom complet (texte) et le résultat de Terminer (message), plus tout écart constaté.

**Portail raiders**
14. Avant le raid : Mon personnage (rangs Impact, lien Warcraft Logs, bouton Armory) ; Classement Impact, objet choisi : le détail du calcul correspond au classeur ; infobulle Wowhead au survol d'un objet.
15. Après Terminer, recharger le portail (cache d'une minute) : les loots du raid apparaissent dans Loots et Mon personnage, l'objet reçu sort du Classement Impact du gagnant.

## After the owner's run

- Save the export as `tools/google_apps_script/fixtures/real-raid-export.txt` and run 4.9 on it.
- Fix any gap found, rerun `luajit tests/addon/run.lua` and the workbook pages.
- Check the root README and `Gargul.code-workspace` (dev workspace with the `../Gargul` clone; kept).
- Tag `v2.0.0` locally, push on request.

## Verification

- The real export imports in the workbook with raidId and treatment on every captured line; the tag exists.
