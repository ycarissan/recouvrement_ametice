# recouvrement_ametice

Activités interactives de chimie quantique (orbitales atomiques, recouvrement,
diagrammes d'OM), à déposer sur AMeTICE sous forme de paquet IMS Content.

Fichiers nécessaires :
 - imsmanifest.xml : manifeste du paquet (organisation et ressources)
 - index.html : introduction (partie cours) et liens vers les activités
 - activite_trace_s.html : tracé d'une orbitale s
 - activite_trace_p.html : tracé d'une orbitale p
 - activite_recouvrement_sp.html : recouvrement s–p
 - activite_recouvrement_pp.html : recouvrement p–p
 - activite_diagramme_om.html : diagrammes d'orbitales moléculaires

Pour générer l'archive à déposer dans Moodle :

    make          # construit activites_atomistique.zip (imsmanifest.xml à la racine)
    make list     # affiche le contenu de l'archive
    make clean    # supprime l'archive

La liste des fichiers est lue dans imsmanifest.xml : pour ajouter une activité,
il suffit de la déclarer dans le manifeste.
