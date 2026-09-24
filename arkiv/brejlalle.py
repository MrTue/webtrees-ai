# -*- coding: utf-8 -*-
"""brejlalle.py <ord> [ord2 ...] — fuldtekstsøger i ALLE Erik Brejls sider.

Henter sidefortegnelsen fra forsiden, gennemgår hver side og viser hvert træf med
tekst omkring. Siderne caches i arbejdsmappen, saa gentagne soegninger er hurtige.

    python brejlalle.py Eksempelsen
    python brejlalle.py "Anders Peter Eksempelsen" Eksempelsen
"""
import os
import re
import sys
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
BASE = "https://www.brejl.dk/"
CACHE = os.path.join(os.environ.get("TEMP", "."), "brejlcache")


def hent(sti):
    os.makedirs(CACHE, exist_ok=True)
    n = os.path.join(CACHE, sti.replace("/", "_"))
    if os.path.exists(n) and os.path.getsize(n) > 500:
        return open(n, encoding="utf-8", errors="replace").read()
    raw = urllib.request.urlopen(urllib.request.Request(
        BASE + sti, headers=UA), timeout=180).read()
    # Nogle af Brejls sider er latin-1, andre utf-8. Vaelg den, der giver faerrest
    # erstatningstegn — ellers bliver aeoeaa til sort snak.
    kand = []
    for enc in ("utf-8", "windows-1252"):
        s = raw.decode(enc, "replace")
        kand.append((s.count("�") + s.count("Ã") + s.count("ï¿½"), s))
    t = min(kand, key=lambda x: x[0])[1]
    open(n, "w", encoding="utf-8").write(t)
    return t


def sider():
    t = hent("index.html") if False else urllib.request.urlopen(
        urllib.request.Request(BASE, headers=UA), timeout=90).read().decode("utf-8", "replace")
    ud = {}
    for m in re.finditer(r'(?is)<a[^>]*href="([^"]+\.html?)"[^>]*>(.*?)</a>', t):
        h = m.group(1)
        for p in ("https://www.brejl.dk/", "https://brejl.dk/", "http://www.brejl.dk/"):
            h = h.replace(p, "")
        if h.startswith("http") or "#" in h:
            continue
        txt = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
        ud.setdefault(h, txt or h)
    return ud


def flad(t):
    return re.sub(r"\s+", " ", H.unescape(
        re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t)))


ord_ = sys.argv[1:]
if not ord_:
    raise SystemExit(__doc__)
s = sider()
print("%d sider paa brejl.dk\n" % len(s))
i_alt = 0
for sti, navn in sorted(s.items(), key=lambda x: x[1]):
    try:
        f = flad(hent(sti))
    except Exception as e:
        continue
    for o in ord_:
        for m in re.finditer(re.escape(o), f, re.I):
            i_alt += 1
            p = m.start()
            print("[%s | %s]" % (navn[:34], sti))
            print("   ..." + f[max(0, p - 200):p + 280].strip() + "...\n")
print("I ALT %d traef paa %s" % (i_alt, ", ".join(ord_)))
