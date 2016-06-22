#!/usr/bin/env python

import copy, os, re, sqlite3, string, urllib
from bs4 import BeautifulSoup, NavigableString, Tag

DOCUMENTS_DIR = os.path.join('SPDX_Licenses.docset', 'Contents', 'Resources', 'Documents')
SPDX_DIR = os.path.join('spdx.org/licenses')

db = sqlite3.connect('SPDX_Licenses.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

page = open(os.path.join(DOCUMENTS_DIR, SPDX_DIR, "index.html")).read()
soup = BeautifulSoup(page, "html5lib")
table = soup.find("table")

item_type = "Guide"

# check items in table
for item in table.find_all("tr"):
    item_link = item.find("a")

    # skip if there is no link
    if not item_link:
        continue

    item_name = item_link.text.strip()
    item_path = os.path.join(SPDX_DIR, item_link.attrs["href"])

    item_shortname = item.find("code")

    if item_shortname:
        item_name = item_shortname.text.strip() + " - " + item_name;

    cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)", (item_name, item_type, item_path))

    print "name: %s, type: %s, path: %s" % (item_name, item_type, item_path)

    subpage = open(os.path.join(DOCUMENTS_DIR, SPDX_DIR, item_link.attrs["href"])).read()
    subsoup = BeautifulSoup(subpage, 'html5lib')

    [t.extract() for t in subsoup("script")]

    dashAnchor = item_link.find("a", class_="dashAnchor")

    if dashAnchor:
        continue

    print "adding toc tag for section: %s" % item_name
    item_name = "//apple_ref/cpp/Type/" + urllib.quote(item_name.encode('utf8'), "")
    dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % item_name).a
    item_link.insert(0, dashAnchor)

    # add sections for license pages
    for headline in subsoup.find_all("h2"):
        if not 'page' in headline.parent['id']:
            continue

        dashAnchor = headline.find("a", class_="dashAnchor")

        if dashAnchor:
            continue

        headline_name = headline.text.strip()

        print "adding toc tag for section: %s" % headline_name
        headline_name = "//apple_ref/cpp/Section/" + urllib.quote(headline_name, "")
        dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % headline_name).a
        headline.insert(0, dashAnchor)

    # add types for <code /> tags (name and short name)
    for code in subsoup.find_all("code"):
        dashAnchor = headline.find("a", class_="dashAnchor")

        if dashAnchor:
            continue

        code_name = code.text.strip()

        print "adding toc tag for section: %s" % code_name
        code_name = "//apple_ref/cpp/Type/" + urllib.quote(code_name, "")
        dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % code_name).a
        code.insert(0, dashAnchor)

    fp = open(os.path.join(DOCUMENTS_DIR, SPDX_DIR, item_link.attrs["href"]), "w")
    fp.write(str(subsoup))
    fp.close()

# strip unecessary tags
[t.extract() for t in soup("script")]

fp = open(os.path.join(DOCUMENTS_DIR, SPDX_DIR, "index.html"), "w")
fp.write(str(soup))
fp.close()

db.commit()
db.close()
