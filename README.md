# recouvrement_ametice

Activités interactives de chimie quantique (orbitales atomiques, recouvrement,
diagrammes d'OM), à déposer sur AMeTICE (Moodle) sous forme de paquets IMS Content.

## Fichiers sources

 - index.html : introduction (partie cours), écrite une seule fois pour toutes les archives
 - activite_trace_s.html : tracé d'une orbitale s
 - activite_trace_p.html : tracé d'une orbitale p
 - activite_recouvrement_sp.html : recouvrement s–p
 - activite_recouvrement_pp.html : recouvrement p–p
 - activite_diagramme_om.html : diagrammes d'orbitales moléculaires
 - build.py : construction des archives (cours adapté, manifeste, vérification des liens)

## Générer les archives

    make                # les quatre archives
    make trace          # atomistique_trace.zip        : tracés s et p
    make recouvrement   # atomistique_recouvrement.zip : recouvrements s–p et p–p
    make om             # atomistique_om.zip           : diagrammes d'OM
    make tout           # activites_atomistique.zip    : intégralité
    make list           # contenu des archives
    make clean          # supprime les archives et le dossier build/

Chaque archive contient son propre imsmanifest.xml (généré, à la racine), son
index.html et ses activités.

## Adapter le cours à chaque archive

Dans index.html, un bloc qui ne doit figurer que dans certaines archives porte
l'attribut data-archives, avec les noms trace, recouvrement, om et tout :

    <section data-archives="recouvrement om tout"> … </section>

Un bloc sans attribut figure dans toutes les archives. En ouvrant index.html dans
un navigateur, on voit exactement la version « intégralité » (tout).

La table ARCHIVES de build.py indique quelles activités vont dans quelle archive.
Pour ajouter une activité : la déclarer dans ACTIVITIES et ARCHIVES (build.py),
et ajouter son bouton, étiqueté, dans la liste des activités de index.html.
