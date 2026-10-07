# Paquet IMS Content pour Moodle (AMeTICE)
#
#   make          construit l'archive (après vérification)
#   make check    vérifie que tous les fichiers du manifeste existent
#   make list     affiche le contenu de l'archive
#   make clean    supprime l'archive
#
# La liste des fichiers est lue dans imsmanifest.xml (balises <file href="...">) :
# pour ajouter une activité, il suffit de la déclarer dans le manifeste.

ARCHIVE  ?= activites_atomistique.zip
MANIFEST := imsmanifest.xml
FILES    := $(MANIFEST) $(shell sed -n 's/.*<file href="\([^"]*\)".*/\1/p' $(MANIFEST))

.PHONY: all check list clean

all: $(ARCHIVE)

# imsmanifest.xml doit être à la racine de l'archive (pas de dossier parent)
$(ARCHIVE): $(FILES) | check
	rm -f $@
	zip -X -9 $@ $(FILES)
	@echo "Archive prête : $@ ($(words $(FILES)) fichiers)"

check:
	@missing=0; \
	for f in $(FILES); do \
	  [ -f "$$f" ] || { echo "Fichier manquant : $$f"; missing=1; }; \
	done; \
	python3 -c "import xml.dom.minidom as m; m.parse('$(MANIFEST)')" \
	  || { echo "$(MANIFEST) n'est pas un XML valide"; missing=1; }; \
	[ $$missing -eq 0 ] && echo "Manifeste OK : $(words $(FILES)) fichiers"

list: $(ARCHIVE)
	unzip -l $(ARCHIVE)

clean:
	rm -f $(ARCHIVE)
