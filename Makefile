# Archives IMS Content pour Moodle (AMeTICE)
#
#   make                construit les quatre archives
#   make trace          atomistique_trace.zip        (tracés s et p)
#   make recouvrement   atomistique_recouvrement.zip (recouvrements s–p et p–p)
#   make om             atomistique_om.zip           (diagrammes d'OM)
#   make tout           activites_atomistique.zip    (intégralité)
#   make list           affiche le contenu des archives
#   make clean          supprime les archives et le dossier build/
#
# La répartition des activités et du cours entre archives est définie dans
# build.py (table ARCHIVES) et par les attributs data-archives de index.html.

PYTHON   ?= python3
ARCHIVES := trace recouvrement om tout
ZIPS     := atomistique_trace.zip atomistique_recouvrement.zip atomistique_om.zip activites_atomistique.zip

.PHONY: all $(ARCHIVES) list clean

all:
	$(PYTHON) build.py

$(ARCHIVES):
	$(PYTHON) build.py $@

list:
	@for z in $(ZIPS); do [ -f $$z ] && unzip -l $$z; done; true

clean:
	rm -rf build $(ZIPS)
