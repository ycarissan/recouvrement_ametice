#!/usr/bin/env python3
"""Construit les archives IMS Content (Moodle / AMeTICE) des activités.

Usage : python3 build.py [archive ...]     (sans argument : toutes les archives)

Le cours (index.html) est écrit une seule fois. Les blocs qui ne vont pas dans
toutes les archives portent un attribut data-archives="trace recouvrement om tout"
listant les archives où ils figurent ; un bloc sans attribut figure partout.
Pour chaque archive, ce script :
  1. extrait la version du cours correspondante (blocs filtrés, attributs et CSS
     de prévisualisation retirés) ;
  2. génère imsmanifest.xml ;
  3. copie les activités ;
  4. vérifie que chaque lien interne pointe vers un fichier (et une ancre)
     présents dans l'archive ;
  5. écrit le zip, avec imsmanifest.xml à la racine.
"""

import re
import shutil
import sys
import zipfile
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
COURSE = "index.html"

# Activités : fichier -> titre dans le manifeste (et dans Moodle)
ACTIVITIES = {
    "activite_trace_s.html": "Tracé d'une orbitale s",
    "activite_trace_p.html": "Tracé d'une orbitale p",
    "activite_recouvrement_sp.html": "Recouvrement s-p",
    "activite_recouvrement_pp.html": "Recouvrement p-p",
    "activite_diagramme_om.html": "Diagrammes d'OM",
}

# Archives : nom (utilisé dans data-archives) -> zip, titre, activités
ARCHIVES = {
    "trace": {
        "zip": "atomistique_trace.zip",
        "title": "Représenter les orbitales atomiques s et p",
        "activities": ["activite_trace_s.html", "activite_trace_p.html"],
    },
    "recouvrement": {
        "zip": "atomistique_recouvrement.zip",
        "title": "Visualiser le recouvrement entre orbitales atomiques",
        "activities": ["activite_recouvrement_sp.html", "activite_recouvrement_pp.html"],
    },
    "om": {
        "zip": "atomistique_om.zip",
        "title": "Construire des diagrammes d'orbitales moléculaires",
        "activities": ["activite_diagramme_om.html"],
    },
    "tout": {
        "zip": "activites_atomistique.zip",
        "title": "Orbitales atomiques et recouvrement",
        "activities": list(ACTIVITIES),
    },
}

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "source", "track", "wbr"}
ATTR_RE = re.compile(r'\s+data-archives\s*=\s*("[^"]*"|\'[^\']*\')')
PREVIEW_CSS_RE = re.compile(r"\n?/\* archives:debut.*?/\* archives:fin \*/\n?", re.S)


class CourseFilter(HTMLParser):
    """Recopie le HTML tel quel en supprimant les blocs d'autres archives."""

    def __init__(self, archive):
        super().__init__(convert_charrefs=False)
        self.archive = archive
        self.out = []
        self.skip_depth = 0   # > 0 : à l'intérieur d'un bloc supprimé

    def _emit(self, text):
        if not self.skip_depth:
            self.out.append(text)

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        void = tag in VOID_TAGS or raw.endswith("/>")
        if self.skip_depth:
            if not void:
                self.skip_depth += 1
            return
        archives = dict(attrs).get("data-archives")
        if archives is not None and self.archive not in archives.split():
            if not void:
                self.skip_depth = 1
            return
        self.out.append(ATTR_RE.sub("", raw))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.skip_depth:
            if tag not in VOID_TAGS:
                self.skip_depth -= 1
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        self._emit(data)

    def handle_entityref(self, name):
        self._emit(f"&{name};")

    def handle_charref(self, name):
        self._emit(f"&#{name};")

    def handle_comment(self, data):
        self._emit(f"<!--{data}-->")

    def handle_decl(self, decl):
        self._emit(f"<!{decl}>")

    def handle_pi(self, data):
        self._emit(f"<?{data}>")


def build_course(archive, title):
    source = (ROOT / COURSE).read_text(encoding="utf-8")
    parser = CourseFilter(archive)
    parser.feed(source)
    parser.close()
    html = "".join(parser.out)
    html = PREVIEW_CSS_RE.sub("\n", html)
    html = re.sub(r"<title>.*?</title>", f"<title>{escape(title)} — Introduction</title>", html, flags=re.S)
    # Supprime les lignes vides multiples laissées par les blocs retirés
    return re.sub(r"\n{3,}", "\n\n", html)


def build_manifest(name, spec):
    items, resources = [], []
    entries = [("INTRO", COURSE, "Introduction")] + [
        (Path(f).stem.upper().replace("_", "-"), f, ACTIVITIES[f]) for f in spec["activities"]
    ]
    for ident, href, title in entries:
        items.append(f'      <item identifier="ITEM-{ident}" identifierref="RES-{ident}" isvisible="true">\n'
                     f"        <title>{escape(title)}</title>\n"
                     f"      </item>")
        resources.append(f'    <resource identifier="RES-{ident}" type="webcontent" href="{href}">\n'
                         f'      <file href="{href}"/>\n'
                         f"    </resource>")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="atomistique-{name}-amu-2026"
  xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd">
  <metadata>
    <schema>IMS Content</schema>
    <schemaversion>1.1.3</schemaversion>
  </metadata>
  <organizations default="ORG-1">
    <organization identifier="ORG-1" structure="hierarchical">
      <title>{escape(spec["title"])}</title>
{chr(10).join(items)}
    </organization>
  </organizations>
  <resources>
{chr(10).join(resources)}
  </resources>
</manifest>
"""


def check_links(folder):
    """Liens internes (href/src) : fichier présent dans l'archive, ancre existante."""
    errors = []
    pages = {p.name: p.read_text(encoding="utf-8") for p in folder.glob("*.html")}
    for name, html in pages.items():
        for link in re.findall(r'(?:href|src)\s*=\s*"([^"]*)"', html):
            if re.match(r"^(https?:|mailto:|data:|javascript:)", link) or link == "":
                continue
            target, _, anchor = link.partition("#")
            target = target or name
            if target not in pages and not (folder / target).exists():
                errors.append(f"{name} : lien vers {link}, fichier absent de l'archive")
            elif anchor and target in pages and not re.search(
                    rf'id\s*=\s*"{re.escape(anchor)}"', pages[target]):
                errors.append(f"{name} : lien vers {link}, ancre introuvable")
    return errors


def build(name):
    spec = ARCHIVES[name]
    folder = BUILD / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)

    (folder / COURSE).write_text(build_course(name, spec["title"]), encoding="utf-8")
    (folder / "imsmanifest.xml").write_text(build_manifest(name, spec), encoding="utf-8")
    for f in spec["activities"]:
        shutil.copy2(ROOT / f, folder / f)

    errors = check_links(folder)
    if errors:
        sys.exit(f"Archive « {name} » : liens cassés\n  " + "\n  ".join(errors))

    files = ["imsmanifest.xml", COURSE] + spec["activities"]
    zip_path = ROOT / spec["zip"]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            z.write(folder / f, arcname=f)
    print(f"{spec['zip']} : {len(files)} fichiers ({', '.join(files[2:])})")


def main(argv):
    names = argv or list(ARCHIVES)
    unknown = [n for n in names if n not in ARCHIVES]
    if unknown:
        sys.exit(f"Archive inconnue : {', '.join(unknown)} (choix : {', '.join(ARCHIVES)})")
    for n in names:
        build(n)


if __name__ == "__main__":
    main(sys.argv[1:])
