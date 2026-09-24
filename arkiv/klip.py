# -*- coding: utf-8 -*-
"""klip.py <mediefil> --gitter               10 %-gitter over hele billedet
klip.py <mediefil> <x0> <x1> <y0> <y1> [--kontrast]   proeveklip

Finder broek-koordinaterne til et billedklip i SLAEGTSHISTORIEN*.md. Mediefilen angives
relativt til webtrees' mediemappe (kirkeboger/1850-eksempel-doede-anders-eksempelsen.jpg; et
foranstillet «media/» taales) — eller som en sti i projektet, der findes som den staar
(billeder/… og arkiv/billeder/…). Koordinaterne er de samme som i gkasse.py: x0 x1 y0 y1.

Skriver KUN en forhaandsvisning til $SLAEGT_ARBEJDSMAPPE (ellers temp-mappen) — aldrig til
mediemappen og aldrig til projektet. Selve klippet laves af mdpdf.py i hukommelsen,
hver gang PDF'en bygges, saa ingen fil kommer til at ligge to steder.

Udskriver den faerdige markdown-linje, lige til at saette ind.
"""
import os
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

ROD = os.environ.get("WEBTREES_MEDIA", "//NAS/docker/webtrees/data/media")   # som medietjek.py: fremad-skraastreger
UD = (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or (len(args) not in (1, 5)):
        raise SystemExit(__doc__)
    rel = args[0].replace("\\", "/")
    rel = rel[len("media/"):] if rel.startswith("media/") else rel
    # En sti, der findes som den staar — fx billeder/… eller arkiv/billeder/… i projektet —
    # bruges direkte; ellers slaas den op i mediemappen.
    sti = rel if os.path.exists(rel) else ROD + "/" + rel
    im = Image.open(sti)
    im = im.convert("RGB")
    w, h = im.size
    navn = os.path.splitext(os.path.basename(rel))[0]
    print("%s: %d x %d px" % (rel, w, h))

    if len(args) == 1:
        skala = 1800.0 / max(w, h)
        if skala < 1:
            im = im.resize((int(w * skala), int(h * skala)), Image.LANCZOS)
        w, h = im.size
        d = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("arialbd.ttf", 20)
        except Exception:
            font = ImageFont.load_default()
        for k in range(1, 10):
            for (a, b) in (((w * k // 10, 0), (w * k // 10, h)), ((0, h * k // 10), (w, h * k // 10))):
                d.line([a, b], fill=(220, 30, 30), width=2 if k == 5 else 1)
            d.text((w * k // 10 + 3, 3), "x .%d" % k, fill=(220, 30, 30), font=font)
            d.text((3, h * k // 10 + 3), "y .%d" % k, fill=(220, 30, 30), font=font)
        ud = os.path.join(UD, "klip-%s-gitter.jpg" % navn)
        im.save(ud, quality=88)
        print("gitter:", ud)
        return

    x0, x1, y0, y1 = [float(a) for a in args[1:]]
    ud_im = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
    if "--kontrast" in sys.argv:
        ud_im = ImageOps.autocontrast(ud_im, cutoff=1)
    print("klippet: %d x %d px (%.0f %% af arealet)" % (ud_im.size + ((x1 - x0) * (y1 - y0) * 100,)))
    if ud_im.size[0] > 2000:
        ud_im = ud_im.resize((2000, int(2000.0 * ud_im.size[1] / ud_im.size[0])), Image.LANCZOS)
    ud = os.path.join(UD, "klip-%s.jpg" % navn)
    ud_im.save(ud, quality=90)
    print("proeve:", ud)
    valg = "klip=%s %s %s %s%s" % (args[1], args[2], args[3], args[4],
                                   " kontrast" if "--kontrast" in sys.argv else "")
    print('\n![BILLEDTEKST: kilde, aar, nr. og hvem](media/%s "%s")' % (rel, valg))


if __name__ == "__main__":
    main()
