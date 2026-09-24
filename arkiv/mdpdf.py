# -*- coding: utf-8 -*-
"""mdpdf.py [--bog] <ind.md> <ud.pdf> — saetter et af projektets markdown-dokumenter op som PDF.

Haandterer overskrifter, afsnit, **fed**, *kursiv*, ~~streget~~, `kode`, > citatbokse,
| tabeller |, lister, --- streger, og desuden:

  ```tavle        en TEGNET slaegtstavle — syntaksen staar i .claude/skills/slaegtsbog/SKILL.md og i
                  docstringen til klassen Tavle nedenfor
  ```             enhver anden kodeblok saettes i fastbreddeskrift og skaleres ned,
                  hvis den er bredere end satsen
  ![tekst](media/kirkeboger/fil.jpg "klip=x0 x1 y0 y1 side=højre bredde=0.42 kontrast")
                  et billedklip. «media/» er webtrees' mediemappe paa NAS'en. Klippet
                  beskaeres og nedskaleres I HUKOMMELSEN — der skrives ingen billedfil,
                  saa reglen om, at ingen fil maa ligge to steder, holdes.
                  Koordinaterne findes med arkiv/klip.py.

--bog giver titelblad, indholdsfortegnelse, ny side for hver «del» (H1) og levende
sidehoved. Uden --bog saettes dokumentet fortloebende som hidtil. PDF-bogmaerker
kommer med i begge tilfaelde.

Oeverst i .md kan staa (usynligt i en markdown-viser):
  <!-- undertitel: Anders Eksempelsens slægt -->
  <!-- forside: media/kirkeboger/fil.jpg "klip=…" -->
  <!-- forsidetekst: billedtekst til forsidebilledet -->

Bygget paa reportlab og Pillow, som allerede er installeret.
"""
import datetime
import html
import io
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, HRFlowable,
                                ImageAndFlowables, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle, XPreformatted)
from reportlab.platypus.tableofcontents import TableOfContents

sys.stdout.reconfigure(encoding="utf-8")

# Samme rod og samme fremad-skraastreger som arkiv/medietjek.py.
MEDIEROD = os.environ.get("WEBTREES_MEDIA", "//NAS/docker/webtrees/data/media")

INK = colors.HexColor("#1b2733")
MUTED = colors.HexColor("#5d6773")
ACCENT = colors.HexColor("#2f6f4f")
RULE = colors.HexColor("#d3d8de")
BOXBG = colors.HexColor("#f2f5f1")
CODEBG = colors.HexColor("#f7f7f5")
PAPIR = colors.HexColor("#fbfaf6")
KANT = colors.HexColor("#b9b3a3")
LINJE = colors.HexColor("#6f7f76")


# ---------------------------------------------------------------- skrifter

FONTDIR = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")
_GLYF = {}          # fontnavn -> tegn, fonten kan tegne (kun for TTF)


def _reg(navn, fil):
    try:
        f = TTFont(navn, os.path.join(FONTDIR, fil))
        pdfmetrics.registerFont(f)
        _GLYF[navn] = f.face.charToGlyph
        return True
    except Exception:
        return False


def _familie():
    for filer in (("pala.ttf", "palab.ttf", "palai.ttf", "palabi.ttf"),
                  ("georgia.ttf", "georgiab.ttf", "georgiai.ttf", "georgiaz.ttf"),
                  ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf")):
        navne = ("Brod", "Brod-B", "Brod-I", "Brod-BI")
        if all(_reg(n, f) for n, f in zip(navne, filer)):
            registerFontFamily("Brod", normal="Brod", bold="Brod-B",
                               italic="Brod-I", boldItalic="Brod-BI")
            return navne
    print("ADVARSEL: ingen TTF-skrift fundet i", FONTDIR, "- bruger Times; saertegn kan mangle")
    return ("Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic")


BROD, FED, KURSIV, FEDKURSIV = _familie()
MONO = "Mono" if _reg("Mono", "consola.ttf") else "Courier"
SYMB = "Symb" if _reg("Symb", "seguisym.ttf") else None
_MANGLER = set()


def _font_til(tegn, font):
    """Den skrift, der kan tegne tegnet: den oenskede, ellers reserveskriften."""
    glyf = _GLYF.get(font)
    if glyf is None or ord(tegn) in glyf or ord(tegn) < 0x7f:
        return font
    if SYMB and ord(tegn) in _GLYF[SYMB]:
        return SYMB
    _MANGLER.add(tegn)
    return font


def reserve(t, font=BROD):
    """Pakker tegn, hovedskriften mangler (pile, stjerner), ind i reserveskriften."""
    def byt(m):
        f = _font_til(m.group(0), font)
        return m.group(0) if f == font else '<font face="%s">%s</font>' % (f, m.group(0))
    return re.sub(r"[^\x00-\u024f]", byt, t)


def _loeb(s, font):
    ud = []
    for ch in s:
        f = _font_til(ch, font)
        if ud and ud[-1][0] == f:
            ud[-1][1] += ch
        else:
            ud.append([f, ch])
    return ud


def bredde(s, font, size):
    return sum(stringWidth(t, f, size) for f, t in _loeb(s, font))


def skriv(c, x, y, s, font, size, midt=False):
    if midt:
        x -= bredde(s, font, size) / 2.0
    for f, t in _loeb(s, font):
        c.setFont(f, size)
        c.drawString(x, y, t)
        x += stringWidth(t, f, size)


def ombryd(s, font, size, maxw):
    linjer, nu = [], ""
    for ord_ in s.split():
        kand = (nu + " " + ord_).strip()
        if nu and bredde(kand, font, size) > maxw:
            linjer.append(nu)
            nu = ord_
        else:
            nu = kand
    if nu:
        linjer.append(nu)
    return linjer or [""]


# ---------------------------------------------------------------- stilarter

S = {
    "h1": ParagraphStyle("h1", fontName=FED, fontSize=19, leading=23,
                         textColor=INK, spaceBefore=26, spaceAfter=9, keepWithNext=1),
    "del-etiket": ParagraphStyle("del-etiket", fontName=BROD, fontSize=10.5, leading=14,
                                 textColor=ACCENT, spaceAfter=6),
    "del-titel": ParagraphStyle("del-titel", fontName=FED, fontSize=27, leading=32,
                                textColor=INK),
    "h2": ParagraphStyle("h2", fontName=FED, fontSize=14, leading=18,
                         textColor=ACCENT, spaceBefore=17, spaceAfter=6, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName=FEDKURSIV, fontSize=11.5, leading=15,
                         textColor=INK, spaceBefore=12, spaceAfter=4, keepWithNext=1),
    "p": ParagraphStyle("p", fontName=BROD, fontSize=10.4, leading=14.8,
                        textColor=INK, spaceAfter=7, alignment=TA_JUSTIFY),
    "quote": ParagraphStyle("quote", fontName=BROD, fontSize=9.7, leading=13.7,
                            textColor=colors.HexColor("#2c3742")),
    "li": ParagraphStyle("li", fontName=BROD, fontSize=10.4, leading=14.4,
                         textColor=INK, spaceAfter=3, leftIndent=12, bulletIndent=2),
    "th": ParagraphStyle("th", fontName=FED, fontSize=8.6, leading=11.4,
                         textColor=colors.white),
    "td": ParagraphStyle("td", fontName=BROD, fontSize=8.8, leading=11.8,
                         textColor=INK),
    "billedtekst": ParagraphStyle("billedtekst", fontName=KURSIV, fontSize=8.4, leading=10.8,
                                  textColor=MUTED, alignment=TA_CENTER),
    "titel": ParagraphStyle("titel", fontName=FED, fontSize=34, leading=40,
                            textColor=INK, alignment=TA_CENTER),
    "undertitel": ParagraphStyle("undertitel", fontName=KURSIV, fontSize=16, leading=21,
                                 textColor=ACCENT, alignment=TA_CENTER),
    "forsidedato": ParagraphStyle("forsidedato", fontName=BROD, fontSize=10.5, leading=14,
                                  textColor=MUTED, alignment=TA_CENTER),
    "indhold": ParagraphStyle("indhold", fontName=FED, fontSize=22, leading=27,
                              textColor=INK, spaceAfter=14),
    "toc0": ParagraphStyle("toc0", fontName=FED, fontSize=10.6, leading=14,
                           textColor=INK, spaceBefore=9),
    "toc1": ParagraphStyle("toc1", fontName=BROD, fontSize=9.6, leading=12.8,
                           textColor=INK, leftIndent=14),
}


def afsnit(markup, stil, **kw):
    """Paragraph, der ikke vaelter bygningen paa skaevt indlejret markdown."""
    try:
        return Paragraph(markup, stil, **kw)
    except Exception:
        ren = html.escape(re.sub(r"<[^>]+>", "", html.unescape(markup)), quote=False)
        print("ADVARSEL: markup kunne ikke saettes, sat som ren tekst:", ren[:70])
        return Paragraph(reserve(ren), stil, **kw)


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*([^*\n]+?)\*", r"<i>\1</i>", t)   # fed er allerede byttet ud ovenfor
    t = re.sub(r"~~(.+?)~~", r"<strike>\1</strike>", t)
    t = re.sub(r"`([^`]+?)`", r'<font face="%s" size="8.6">\1</font>' % MONO, t)
    t = re.sub(r"\[\[(X\d+)\]\]", r'<font size="7" color="#8a929b">\1</font>', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", t)
    return reserve(t)


def ren_tekst(t):
    t = re.sub(r"\[\[X\d+\]\]\s*", "", t)
    return re.sub(r"[*`~]", "", t).strip()


# ---------------------------------------------------------------- tabeller og citater

def tabel(raekker, W):
    data, laengder = [], []
    for i, r in enumerate(raekker):
        celler = [c.strip() for c in r.strip().strip("|").split("|")]
        if i > 0 and set("".join(celler)) <= set("-: "):
            continue
        st = S["th"] if not data else S["td"]
        data.append([afsnit(inline(c), st) for c in celler])
        laengder.append([len(ren_tekst(c)) for c in celler])
    n = max(len(r) for r in data)
    for r, l in zip(data, laengder):
        while len(r) < n:
            r.append(Paragraph("", S["td"]))
            l.append(0)
    # Kolonnebredder efter indhold, men ingen kolonne under en rimelig mindstebredde.
    vaegt = [min(60, max(9, max(l[k] for l in laengder))) for k in range(n)]
    bredder = [W * v / float(sum(vaegt)) for v in vaegt]
    t = Table(data, colWidths=bredder, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafbfa")]),
    ]))
    return t


# En boks, der begynder med en af disse etiketter, er FORTAELLERENS forbehold og faar
# den tonede boks med groen kant. Alt andet i «>» er kildecitater og sidebemaerkninger
# og saettes lettere — saa formodningerne er dem, der springer i oejnene.
FORBEHOLD = re.compile(r"^\*\*(Formodning|Om kilderne|Fra \w+ hukommelse|Et spor|"
                       r"Familieoplysning|Et lukket spor)", re.I)


def _del_langt(tekst, graense=2200):
    """Et afsnit, der er hoejere end en side, kan en tabelraekke ikke bryde."""
    ud = []
    while len(tekst) > graense:
        k = tekst.rfind(". ", 0, graense)
        k = k + 1 if k > graense // 2 else graense
        ud.append(tekst[:k])
        tekst = tekst[k:].lstrip()
    return ud + [tekst]


def citatboks(tekster, W):
    forbehold = bool(FORBEHOLD.match(tekster[0]))
    stykker = [s for t in tekster for s in _del_langt(t)]
    raekker = [[afsnit(inline(x), S["quote"])] for x in stykker]
    indryk = 0 if forbehold else 10
    t = Table(raekker, colWidths=[W - indryk], hAlign="LEFT")
    n = len(raekker) - 1
    stil = [
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, 0), 7 if forbehold else 2),
        ("BOTTOMPADDING", (0, n), (-1, n), 7 if forbehold else 2),
    ]
    if forbehold:
        stil += [("BACKGROUND", (0, 0), (-1, -1), BOXBG),
                 ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT)]
    else:
        stil += [("LINEBEFORE", (0, 0), (0, -1), 0.9, KANT)]
    t.setStyle(TableStyle(stil))
    if indryk:
        t = Table([[t]], colWidths=[W], hAlign="LEFT")
        t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), indryk),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return KeepTogether(t) if sum(len(x) for x in tekster) < 900 else t


def kodeblok(tekst, W):
    laengst = max([bredde(l, MONO, 1.0) for l in tekst.split("\n")] or [1]) or 1
    size = min(7.6, (W - 18) / laengst)
    stil = ParagraphStyle("kode", fontName=MONO, fontSize=size, leading=size * 1.27,
                          textColor=INK)
    p = XPreformatted(reserve(html.escape(tekst, quote=False), MONO), stil)
    t = Table([[p]], colWidths=[W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.4, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------- billedklip

BRUGTE_KLIP = []


def _sti(rel, mdmappe):
    rel = rel.replace("\\", "/")
    if rel.startswith("media/"):
        return MEDIEROD + "/" + rel[len("media/"):]
    return rel if os.path.isabs(rel) else os.path.join(mdmappe, rel)


def _valg(s):
    v = {"klip": None, "side": None, "bredde": None, "kontrast": False}
    s = s or ""
    m = re.search(r"klip=([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)", s)
    if m:
        v["klip"] = tuple(float(x) for x in m.groups())
    m = re.search(r"side=(højre|venstre|hoejre)", s)
    if m:
        v["side"] = "left" if m.group(1) == "venstre" else "right"
    m = re.search(r"bredde=([\d.]+)", s)
    if m:
        v["bredde"] = float(m.group(1))
    v["kontrast"] = "kontrast" in s
    return v


class Klip(Flowable):
    """Et beskaaret billede med tynd ramme og billedtekst under. Har de to metoder,
    ImageAndFlowables kalder paa et Image, saa teksten kan loebe rundt om det."""

    def __init__(self, laeser, w, h, tekst, hAlign="CENTER"):
        Flowable.__init__(self)
        self.laeser, self.bw, self.bh = laeser, w, h
        self.hAlign = hAlign
        self.tekst = afsnit(inline(tekst), S["billedtekst"]) if tekst else None
        self.th = self.tekst.wrap(w, 1000)[1] + 4 if self.tekst else 0
        self.drawWidth, self.drawHeight = w, h + self.th

    def wrap(self, aW, aH):
        return self.drawWidth, self.drawHeight

    def _restrictSize(self, aW, aH):
        return self.drawWidth, self.drawHeight

    def _unRestrictSize(self):
        pass

    def draw(self):
        c = self.canv
        if self.laeser is None:
            c.setFillColor(colors.HexColor("#e6e6e3"))
            c.rect(0, self.th, self.bw, self.bh, stroke=0, fill=1)
            c.setFillColor(MUTED)
            skriv(c, self.bw / 2, self.th + self.bh / 2 - 3, "billedet mangler", KURSIV, 9, midt=True)
        else:
            c.drawImage(self.laeser, 0, self.th, self.bw, self.bh)
        c.setStrokeColor(KANT)
        c.setLineWidth(0.5)
        c.rect(0, self.th, self.bw, self.bh, stroke=1, fill=0)
        if self.tekst:
            self.tekst.drawOn(c, 0, 0)


def klip(alt, rel, valgtekst, W, H, mdmappe, maxh=0.5):
    from PIL import Image as PILImage, ImageOps
    v = _valg(valgtekst)
    andel = v["bredde"] or (0.42 if v["side"] else 1.0)
    w = W * min(1.0, andel)
    sti = _sti(rel, mdmappe)
    try:
        im = PILImage.open(sti)
        im.load()
    except Exception as e:
        print("ADVARSEL: billedet kunne ikke laeses:", sti, "(%s)" % e.__class__.__name__)
        return Klip(None, w, w * 0.3, alt), v
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bund = PILImage.new("RGB", im.size, "white")
        bund.paste(im, mask=im.split()[-1])
        im = bund
    elif im.mode != "RGB" and im.mode != "L":
        im = im.convert("RGB")
    if v["klip"]:
        x0, x1, y0, y1 = v["klip"]
        bw, bh = im.size
        im = im.crop((int(bw * x0), int(bh * y0), int(bw * x1), int(bh * y1)))
    if v["kontrast"]:
        im = ImageOps.autocontrast(im, cutoff=1)
    h = w * im.size[1] / float(im.size[0])
    if h > H * maxh:
        h = H * maxh
        w = h * im.size[0] / float(im.size[1])
    px = int(w / 72.0 * 220)
    if im.size[0] > px:
        im = im.resize((px, max(1, int(px * im.size[1] / float(im.size[0])))), PILImage.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    buf.seek(0)
    BRUGTE_KLIP.append("%s  %s" % (rel, valgtekst or ""))
    return Klip(ImageReader(buf), w, h, alt), v


# ---------------------------------------------------------------- slaegtstavler

class TavleFejl(Exception):
    pass


class Tavle(Flowable):
    """En tegnet slaegtstavle. Én linje per generation, oeverst de aeldste:

        Far ∞ Mor; undertekst  ||  Far ∞ Mor          to par side om side
        Mand; f. 1887  ∞[gift 12. maj 1911]  Kone     to par over ét par = de to boern gifter sig
        søskende[8 børn, 6 fundet]: A · B · ^C · D    soeskendeflok som ét felt; ^ = den, linjen gaar igennem
        børn: Evald; rebslager || ^Grete ∞ Svend       boern i hver sin boks
        Ole — Karen                                   — er samliv (stiplet), ∞ er aegteskab
        Peder Påfundsen  <-- femtipoldefar            randnote til hoejre

    ;  indleder en undertekst (flere ; giver flere linjer). «Navn (1872-1939)» faar
    aarstallene paa egen linje. ^ foran en person: slaegtslinjen gaar gennem hende —
    ellers gennem den foerstnaevnte.
    """
    FN, FS, FL = 8.7, 7.3, 7.4      # navn, undertekst, paaskrift
    PAD, VGAB, RADIUS = 5.0, 19.0, 3.0

    def __init__(self, tekst, linjenr=0):
        Flowable.__init__(self)
        self.raekker = []
        for k, l in enumerate(tekst.split("\n")):
            if l.strip():
                try:
                    self.raekker.append(self._laes(l.strip()))
                except TavleFejl as e:
                    raise SystemExit("FEJL i tavle, linje %d: %s\n    %s" % (linjenr + k + 1, e, l.strip()))
        if not self.raekker:
            raise SystemExit("FEJL: tom tavle ved linje %d" % linjenr)

    # -- laesning
    def _person(self, s):
        s = s.strip()
        gennem = s.startswith("^")
        dele = [d.strip() for d in s.lstrip("^").split(";")]
        if not dele[0]:
            raise TavleFejl("en person mangler navn")
        navn, aar = dele[0], None
        m = re.match(r"^(.*\S)\s*\(([^()]*)\)$", navn)
        if m:
            # «(* 9. april 1886 · † 17. januar 1961)» er levetid og saettes uden parenteser,
            # ombrudt ved «·». Enhver anden parentes — «(ca. 1905)», «(tvilling)» — som foer.
            if re.match(r"^\s*(\*|†|døbt|begr\.)", m.group(2)):
                navn, aar = m.group(1), [d.strip() for d in m.group(2).split("·")]
            else:
                navn, aar = m.group(1), ["(%s)" % m.group(2)]
        return {"navn": navn, "aar": aar or [], "under": [d for d in dele[1:] if d],
                "gennem": gennem}

    def _enhed(self, s):
        m = re.match(r"^(.*?)\s+(∞|—)\s*(?:\[([^\]]*)\])?\s+(.*)$", s.strip())
        if not m:
            return {"personer": [self._person(s)], "baand": None, "skrift": ""}
        skrift = (m.group(3) or "").strip()
        if m.group(2) == "∞":
            if not skrift:
                skrift = "∞"
            elif not re.match(r"^(gift|viet|∞)", skrift):
                skrift = "∞ " + skrift
        return {"personer": [self._person(m.group(1)), self._person(m.group(4))],
                "baand": m.group(2), "skrift": skrift}

    def _laes(self, l):
        r = {"slags": "led", "skrift": "", "note": ""}
        if "<--" in l:
            l, r["note"] = [x.strip() for x in l.split("<--", 1)]
        m = re.match(r"^(børn|søskende)\s*(?:\[([^\]]*)\])?\s*:\s*(.*)$", l)
        if m:
            r["slags"], r["skrift"], l = m.group(1), (m.group(2) or "").strip(), m.group(3)
        if r["slags"] == "søskende":
            r["navne"] = [x.strip() for x in l.split("·") if x.strip()]
            if not r["navne"]:
                raise TavleFejl("søskende-linjen er tom")
            return r
        r["enheder"] = [self._enhed(x) for x in l.split("||")]
        return r

    # -- opstilling
    def _boks(self, p, maxw):
        inder = maxw - 2 * self.PAD
        linjer = [(t, FED, self.FN, INK) for t in ombryd(p["navn"], FED, self.FN, inder)]
        for a in p["aar"]:
            linjer += [(t, BROD, self.FS + 0.5, INK) for t in ombryd(a, BROD, self.FS + 0.5, inder)]
        for u in p["under"]:
            linjer += [(t, BROD, self.FS, MUTED) for t in ombryd(u, BROD, self.FS, inder)]
        p["linjer"] = linjer
        p["w"] = max(bredde(t, f, s) for t, f, s, _ in linjer) + 2 * self.PAD
        p["h"] = p["ih"] = sum(s * 1.22 for _, _, s, _ in linjer) + 2 * self.PAD - 1

    def _maal(self, e, plads):
        """Maaler en enhed, der hoejst maa fylde «plads» i bredden."""
        e["personer"] = list(e.setdefault("orden", list(e["personer"])))
        if e["baand"]:
            e["gab"] = max(26.0, bredde(e["skrift"], KURSIV, self.FL) + 12)
            maxw = max(48.0, min(165.0, (plads - e["gab"]) / 2.0))
        else:
            e["gab"] = 0.0
            maxw = max(48.0, min(210.0, plads))
        for p in e["personer"]:
            self._boks(p, maxw)
        h = max(p["h"] for p in e["personer"])
        for p in e["personer"]:
            p["h"] = h
        e["w"] = sum(p["w"] for p in e["personer"]) + e["gab"]
        e["h"] = h

    def _stil(self, e, x, y):
        for p in e["personer"]:
            p["x"], p["y"] = x, y
            x += p["w"] + e["gab"]

    @staticmethod
    def _maal_person(e):
        for p in e["personer"]:
            if p["gennem"]:
                return p
        return e.get("orden", e["personer"])[0]     # ogsaa naar parret er spejlvendt

    @staticmethod
    def _kilde(e):
        """Punktet, en efterslaegtslinje udgaar fra: parrets baand, eller boksens bund."""
        if e["baand"]:
            a, b = e["personer"]
            return ((a["x"] + a["w"] + b["x"]) / 2.0, a["y"] + a["h"] / 2.0)
        p = e["personer"][0]
        return (p["x"] + p["w"] / 2.0, p["y"] + p["h"])

    def wrap(self, aW, aH):
        W = self.W = aW
        self.streger, y, forrige = [], 0.0, None
        for r in self.raekker:
            # 1. hvorfra kommer linjerne ned til denne raekke?
            kilder = []
            if forrige is not None:
                if forrige["slags"] == "søskende":
                    kilder = [(W / 2.0, forrige["y"] + forrige["h"])]
                else:
                    E = forrige["enheder"]
                    maerket = [e for e in E if any(p["gennem"] for p in e["personer"])]
                    if forrige["slags"] == "børn" and len(E) > 1:
                        E = maerket[:1] or E[:1]
                    elif len(E) > 1 and r["slags"] != "led":
                        E = maerket[:1] or E[:1]
                    kilder = [self._kilde(e) for e in E]
                y += self.VGAB + (8 if r["skrift"] and r["slags"] == "børn" else 0)
            r["y"] = y

            # 2. stil raekken op
            if r["slags"] == "søskende":
                inder = W * 0.86 - 2 * self.PAD
                tekst = " · ".join(n.lstrip("^") for n in r["navne"])
                r["linjer"] = ombryd(tekst, BROD, self.FN, inder)
                r["w"] = W * 0.86
                r["h"] = (len(r["linjer"]) + (1 if r["skrift"] else 0)) * self.FN * 1.3 + 2 * self.PAD
                r["x"] = (W - r["w"]) / 2.0
                maal = [(W / 2.0, y)]
            else:
                E = r["enheder"]
                moedes = (r["slags"] == "led" and len(E) == 1 and E[0]["baand"]
                          and len(kilder) == 2)
                if moedes:
                    # to slaegter loeber sammen: hver aegtefaelle under sine foraeldre
                    e = E[0]
                    self._maal(e, W - 4)
                    a, b = e["personer"]
                    ax = min(max(kilder[0][0] - a["w"] / 2.0, 0), W - a["w"])
                    bx = min(max(kilder[1][0] - b["w"] / 2.0, 0), W - b["w"])
                    if bx - (ax + a["w"]) < e["gab"]:
                        ax = (W - e["w"]) / 2.0
                        bx = ax + a["w"] + e["gab"]
                    a["x"], b["x"], a["y"], b["y"] = ax, bx, y, y
                    maal = [(a["x"] + a["w"] / 2.0, y), (b["x"] + b["w"] / 2.0, y)]
                else:
                    kol = W / float(len(E))
                    maal = []
                    for k, e in enumerate(E):
                        self._maal(e, kol - 8)
                        x = k * kol + (kol - e["w"]) / 2.0
                        if r["slags"] == "led" and (len(kilder) == len(E) or len(kilder) == 1 == len(E)):
                            # ret maalpersonen ind under sin kilde, saa linjen bliver lodret
                            lo, hi = (k * kol, (k + 1) * kol - e["w"]) if len(E) > 1 else (0, W - e["w"])
                            lo, hi = min(lo, hi), max(lo, hi)
                            e["personer"] = list(e["orden"])
                            bedst = None
                            # Stoeder parret mod margenen, saa spejlvend det hellere end at
                            # knaekke linjen: aegtefaellen kan lige saa godt staa til venstre.
                            # Kun naar raekken har én enhed — ellers kommer to hustruer til at
                            # staa side om side og ligne et par.
                            for orden in ((e["orden"], e["orden"][::-1]) if len(E) == 1
                                          else (e["orden"],)):
                                e["personer"] = list(orden)
                                self._stil(e, 0, y)
                                mp = self._maal_person(e)
                                x0 = kilder[k][0] - (mp["x"] + mp["w"] / 2.0)
                                x1 = min(max(x0, lo), hi)
                                if bedst is None or abs(x1 - x0) < bedst[0] - 0.5:
                                    bedst = (abs(x1 - x0), x1, list(orden))
                            x, e["personer"] = bedst[1], bedst[2]
                        self._stil(e, x, y)
                        mp = self._maal_person(e)
                        maal.append((mp["x"] + mp["w"] / 2.0, y))
                    if r["slags"] == "led" and len(kilder) == 1 and len(E) > 1:
                        # én kilde, flere enheder: linjen gaar kun til den maerkede
                        m = [t for t, e in zip(maal, E) if any(p["gennem"] for p in e["personer"])]
                        maal = m[:1] or maal[:1]
                    elif r["slags"] == "led" and kilder and len(kilder) != len(maal):
                        raise SystemExit("FEJL i tavle: %d linjer oppefra kan ikke fordeles paa %d "
                                         "enheder — brug ^ eller «børn:»" % (len(kilder), len(maal)))
                r["h"] = max(e["h"] for e in E)

            # 3. forbindelseslinjer
            if kilder:
                my = y - self.VGAB / 2.0
                if r["slags"] == "børn" and len(maal) > 1:
                    sx, sy = kilder[0]
                    xs = [t[0] for t in maal] + [sx]
                    self.streger.append((sx, sy, sx, my))
                    self.streger.append((min(xs), my, max(xs), my))
                    for tx, ty in maal:
                        self.streger.append((tx, my, tx, ty))
                    r["skriftpos"] = (sx + 5, my - 3 - self.FL)
                else:
                    for (sx, sy), (tx, ty) in zip(kilder, maal):
                        if abs(sx - tx) < 1.5:
                            self.streger.append((tx, sy, tx, ty))
                        else:
                            self.streger += [(sx, sy, sx, my), (sx, my, tx, my), (tx, my, tx, ty)]
                    r["skriftpos"] = (kilder[0][0] + 5, my - 3)
            y += r["h"]
            forrige = r
        self.H = y + 2
        return W, self.H

    # -- tegning
    def draw(self):
        c, H = self.canv, self.H
        c.setStrokeColor(LINJE)
        c.setLineWidth(0.8)
        c.setLineCap(1)
        for x0, y0, x1, y1 in self.streger:
            c.line(x0, H - y0, x1, H - y1)
        for r in self.raekker:
            if r["slags"] == "søskende":
                self._felt(r["x"], r["y"], r["w"], r["h"])
                yy = H - r["y"] - self.PAD - self.FN
                if r["skrift"]:
                    c.setFillColor(MUTED)
                    skriv(c, self.W / 2.0, yy, r["skrift"], KURSIV, self.FL + 0.4, midt=True)
                    yy -= self.FN * 1.3
                gennem = [n.lstrip("^") for n in r["navne"] if n.startswith("^")]
                for l in r["linjer"]:
                    self._soeskendelinje(l, yy, gennem)
                    yy -= self.FN * 1.3
                continue
            if r["slags"] == "børn" and r["skrift"] and "skriftpos" in r:
                c.setFillColor(MUTED)
                x, yy = r["skriftpos"]
                skriv(c, x, H - yy - self.FL, r["skrift"], KURSIV, self.FL)
            for e in r["enheder"]:
                if e["baand"]:
                    a, b = e["personer"]
                    ly = H - (a["y"] + a["h"] / 2.0)
                    c.setStrokeColor(LINJE)
                    c.setLineWidth(0.8)
                    c.setDash([2.2, 2.2] if e["baand"] == "—" else [])
                    c.line(a["x"] + a["w"], ly, b["x"], ly)
                    c.setDash([])
                    if e["skrift"]:
                        c.setFillColor(ACCENT)
                        stor = self.FL + 3 if e["skrift"] == "∞" else self.FL
                        skriv(c, (a["x"] + a["w"] + b["x"]) / 2.0, ly + 3.2, e["skrift"],
                              BROD if e["skrift"] == "∞" else KURSIV, stor, midt=True)
                for p in e["personer"]:
                    self._felt(p["x"], p["y"], p["w"], p["h"])
                    yy = H - p["y"] - self.PAD + 1 - (p["h"] - p["ih"]) / 2.0
                    for t, f, s, farve in p["linjer"]:
                        yy -= s * 1.22
                        c.setFillColor(farve)
                        skriv(c, p["x"] + p["w"] / 2.0, yy + s * 0.27, t, f, s, midt=True)
            if r["note"]:
                sidste = r["enheder"][-1]["personer"][-1]
                c.setFillColor(MUTED)
                skriv(c, sidste["x"] + sidste["w"] + 8, H - sidste["y"] - sidste["h"] / 2.0 - 2.5,
                      "← " + r["note"], KURSIV, self.FL + 0.4)

    def _felt(self, x, y, w, h):
        c = self.canv
        c.setFillColor(PAPIR)
        c.setStrokeColor(KANT)
        c.setLineWidth(0.6)
        c.roundRect(x, self.H - y - h, w, h, self.RADIUS, stroke=1, fill=1)

    def _soeskendelinje(self, l, yy, gennem):
        """Én centreret linje i soeskendefeltet, med den gennemgaaende i fed."""
        c = self.canv
        stykker, rest = [], l
        for g in gennem:
            if g in rest:
                foer, efter = rest.split(g, 1)
                stykker += [(foer, BROD), (g, FED)]
                rest = efter
        stykker.append((rest, BROD))
        x = self.W / 2.0 - sum(bredde(t, f, self.FN) for t, f in stykker) / 2.0
        c.setFillColor(INK)
        for t, f in stykker:
            skriv(c, x, yy, t, f, self.FN)
            x += bredde(t, f, self.FN)


# ---------------------------------------------------------------- markdown -> flowables

class Overskrift:
    """Maerker en flowable, saa dokumentet kan foere den ind i indhold og bogmaerker."""
    nr = 0

    @classmethod
    def maerk(cls, fl, niv, tekst):
        cls.nr += 1
        fl._niv, fl._ren, fl._key = niv, ren_tekst(tekst), "ovs%d" % cls.nr
        return fl


def delstart(tekst, W):
    """En «del» aabner sin egen side: lille etiket, stor titel, groen streg."""
    m = re.match(r"^(.{3,24}?\bdel)\s*[:—–-]\s*(.+)$", tekst, re.I)
    inder = []
    if m:
        etiket = "   ".join(" ".join(o) for o in m.group(1).upper().split())
        inder.append(afsnit(reserve(html.escape(etiket)), S["del-etiket"]))
        inder.append(afsnit(inline(m.group(2)), S["del-titel"]))
    else:
        inder.append(afsnit(inline(tekst), S["del-titel"]))
    inder.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT, spaceBefore=10, spaceAfter=0))
    t = Table([[inder]], colWidths=[W])
    t.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 95),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t


BILLEDE = re.compile(r'^!\[(.*?)\]\((\S+?)(?:\s+"(.*?)")?\)\s*$')
BLOKSTART = re.compile(r"^\s*(#{1,3} |>|\||```|---|!\[|<!--)")


def byg(md, W, H, mdmappe, bog):
    ud, i, linjer = [], 0, md.split("\n")
    foerste_h1 = True

    def laes_afsnit(i):
        saml = []
        while i < len(linjer) and linjer[i].strip() and not BLOKSTART.match(linjer[i]):
            saml.append(linjer[i].strip())
            i += 1
        return (afsnit(inline(" ".join(saml)), S["p"]) if saml else None), i

    while i < len(linjer):
        L = linjer[i]
        s = L.strip()

        if not s:
            i += 1
            continue

        if s.startswith("<!--"):
            while i < len(linjer) and "-->" not in linjer[i]:
                i += 1
            i += 1
            continue

        if s.startswith("```"):
            slags, start = s[3:].strip().lower(), i
            blok, i = [], i + 1
            while i < len(linjer) and not linjer[i].strip().startswith("```"):
                blok.append(linjer[i].rstrip())
                i += 1
            i += 1
            if slags == "tavle":
                t = Tavle("\n".join(blok), start + 1)
                # «**Faderens far — Eksempelsen**» og tavlen hoerer sammen paa samme side
                if (ud and isinstance(ud[-1], Paragraph) and not hasattr(ud[-1], "_niv")
                        and len(ud[-1].text) < 120):
                    ud[-1] = KeepTogether([ud[-1], Spacer(1, 6), t])
                    ud.append(Spacer(1, 12))
                else:
                    ud += [Spacer(1, 6), t, Spacer(1, 12)]
            else:
                ud += [Spacer(1, 3), kodeblok("\n".join(blok), W), Spacer(1, 7)]
            continue

        m = BILLEDE.match(s)
        if m:
            i += 1
            k, v = klip(m.group(1), m.group(2), m.group(3), W, H, mdmappe)
            if v["side"]:
                # teksten loeber rundt om: tag de naeste (hoejst tre) almindelige afsnit med
                ved = []
                while len(ved) < 3:
                    while i < len(linjer) and not linjer[i].strip():
                        i += 1
                    if i >= len(linjer) or BLOKSTART.match(linjer[i]) or re.match(
                            r"^\s*(\d+\. |[-*] )", linjer[i]):
                        break
                    p, i = laes_afsnit(i)
                    if p is None:
                        break
                    ved.append(p)
                if ved:
                    hoejre = v["side"] == "right"
                    for p in ved:      # lige margen giver huller i den smalle spalte
                        p.style = ParagraphStyle("p-venstre", parent=S["p"], alignment=TA_LEFT)
                    ud.append(ImageAndFlowables(
                        k, ved, imageSide=v["side"], imageTopPadding=3, imageBottomPadding=6,
                        imageLeftPadding=12 if hoejre else 0, imageRightPadding=0 if hoejre else 12))
                    continue
            if ud and isinstance(ud[-1], Paragraph) and not hasattr(ud[-1], "_niv"):
                # «… skrev han:» og billedet, det peger paa, maa ikke skilles af et sideskift
                ud[-1] = KeepTogether([ud[-1], Spacer(1, 5), k])
                ud.append(Spacer(1, 11))
            else:
                ud += [Spacer(1, 5), k, Spacer(1, 11)]
            continue

        if s.startswith("|"):
            blok = []
            while i < len(linjer) and linjer[i].strip().startswith("|"):
                blok.append(linjer[i])
                i += 1
            ud += [Spacer(1, 3), tabel(blok, W), Spacer(1, 9)]
            continue

        if s.startswith(">"):
            blok = []
            while i < len(linjer) and (linjer[i].strip().startswith(">")
                                       or (blok and linjer[i].strip()
                                           and not BLOKSTART.match(linjer[i]))):
                x = linjer[i].strip()
                x = x[1:].strip() if x.startswith(">") else x
                if x:
                    blok.append(x)
                elif blok:
                    blok.append("")
                i += 1
            tekst, saml = [], []
            for x in blok:
                if x:
                    saml.append(x)
                elif saml:
                    tekst.append(" ".join(saml))
                    saml = []
            if saml:
                tekst.append(" ".join(saml))
            if tekst:
                ud += [Spacer(1, 4), citatboks(tekst, W), Spacer(1, 9)]
            continue

        if s.startswith("---"):
            ud += [Spacer(1, 6), HRFlowable(width="100%", thickness=0.6, color=RULE),
                   Spacer(1, 8)]
            i += 1
            continue

        m = re.match(r"^(#{1,3}) +(.*)$", s)
        if m:
            niv, tekst = len(m.group(1)), m.group(2)
            i += 1
            if niv == 1 and bog:
                if foerste_h1:          # bogens titel staar paa titelbladet
                    foerste_h1 = False
                    continue
                ud += [PageBreak(), Overskrift.maerk(delstart(tekst, W), 1, tekst)]
                continue
            foerste_h1 = False
            ud.append(Overskrift.maerk(afsnit(inline(tekst), S["h%d" % niv]), niv, tekst))
            if niv == 1:
                ud.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT,
                                     spaceBefore=1, spaceAfter=9))
            continue

        nummer = re.match(r"^(\d+)\. +(.*)$", s)
        punkt = re.match(r"^[-*] +(.*)$", s)
        if nummer or punkt:
            tekst = [nummer.group(2) if nummer else punkt.group(1)]
            kugle = ("%s." % nummer.group(1)) if nummer else "•"
            i += 1
            # Ombrudte listepunkter: indrykkede fortsaettelseslinjer hoerer med.
            while (i < len(linjer) and linjer[i].strip()
                   and linjer[i][:1] in (" ", "\t")
                   and not re.match(r"^\s*(\d+\. |[-*] |[#>|]|```|---)", linjer[i])):
                tekst.append(linjer[i].strip())
                i += 1
            ud.append(afsnit(inline(" ".join(tekst)), S["li"], bulletText=kugle))
            continue

        # Bemaerk: afsnittet maa IKKE brydes af «5. november», som ligner et
        # listepunkt. Listetjekket ovenfor har allerede fanget de aegte lister.
        p, ny = laes_afsnit(i)
        if p is None:                   # en linje, ingen regel tog: spring den over
            i += 1
            continue
        ud.append(p)
        i = ny
    return ud


# ---------------------------------------------------------------- dokumentet

MAANEDER = ("januar februar marts april maj juni juli august september "
            "oktober november december").split()


class Dokument(BaseDocTemplate):
    def __init__(self, fil, bog, titel, **kw):
        BaseDocTemplate.__init__(self, fil, **kw)
        self.bog, self.titel = bog, titel

    def beforeDocument(self):
        self.del_navn, self.aabner, self.har_h1, self.sidste_niv = "", False, False, -1

    def afterFlowable(self, fl):
        niv = getattr(fl, "_niv", None)
        if niv is None:
            return
        self.canv.bookmarkPage(fl._key)
        bm = min(niv - 1 if self.har_h1 or niv == 1 else niv - 2, self.sidste_niv + 1)
        bm = max(bm, 0)
        self.canv.addOutlineEntry(fl._ren, fl._key, level=bm, closed=(bm >= 1))
        self.sidste_niv = bm
        if niv == 1:
            self.har_h1, self.del_navn, self.aabner = True, fl._ren, True
        if niv <= 2:
            toc = 0 if (niv == 1 or not self.har_h1) else 1
            self.notify("TOCEntry", (toc, html.escape(fl._ren, quote=False), self.page, fl._key))

    def sidestart(self, c, d):
        self.aabner = False

    def sideslut(self, c, d):
        v, h = self.leftMargin, A4[0] - self.rightMargin
        c.saveState()
        c.setFillColor(MUTED)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        if not self.bog:
            skriv(c, v, 13 * mm, self.titel, BROD, 8)
            c.setFont(BROD, 8)
            c.drawRightString(h, 13 * mm, "%d" % d.page)
            c.line(v, 16 * mm, h, 16 * mm)
        else:
            c.setFont(BROD, 9.5)
            c.drawCentredString(A4[0] / 2.0, 13 * mm, "%d" % d.page)
            if not self.aabner:
                y = A4[1] - 14 * mm
                skriv(c, v, y, self.titel, KURSIV, 8.4)
                if self.del_navn:
                    skriv(c, h - bredde(self.del_navn, KURSIV, 8.4), y, self.del_navn, KURSIV, 8.4)
                c.line(v, y - 3.5, h, y - 3.5)
        c.restoreState()

    def kun_sidetal(self, c, d):
        c.saveState()
        c.setFillColor(MUTED)
        c.setFont(BROD, 9.5)
        c.drawCentredString(A4[0] / 2.0, 13 * mm, "%d" % d.page)
        c.restoreState()


def forside(titel, meta, W, H, mdmappe, mdfil):
    hoved, _, under = titel.partition(" — ")
    under = meta.get("undertitel", under)
    ud = [Spacer(1, 52 * mm), afsnit(inline(hoved), S["titel"])]
    if under:
        ud += [Spacer(1, 9), afsnit(inline(under), S["undertitel"])]
    ud += [Spacer(1, 16), HRFlowable(width="28%", thickness=1.4, color=ACCENT, hAlign="CENTER"),
           Spacer(1, 26)]
    if meta.get("forside"):
        m = re.match(r'^(\S+)(?:\s+"(.*?)")?\s*$', meta["forside"])
        k, _ = klip(meta.get("forsidetekst", ""), m.group(1),
                    ((m.group(2) or "") + " bredde=0.8").strip(), W, H, mdmappe, maxh=0.32)
        ud += [k, Spacer(1, 20)]
    t = datetime.date.fromtimestamp(os.path.getmtime(mdfil))
    ud.append(afsnit("%s %d" % (MAANEDER[t.month - 1].capitalize(), t.year), S["forsidedato"]))
    return ud


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    bog = "--bog" in sys.argv
    if len(args) != 2:
        raise SystemExit(__doc__)
    ind, udfil = args
    mdmappe = os.path.dirname(os.path.abspath(ind))
    md = open(ind, encoding="utf-8-sig").read().replace("\r\n", "\n")
    meta = dict((k.lower(), v.strip()) for k, v in
                re.findall(r"^<!--\s*([\wæøå]+)\s*:\s*(.*?)\s*-->\s*$", md, re.M))
    m = re.search(r"^# +(.*)$", md, re.M)
    titel = ren_tekst(m.group(1)) if m else "Slægtshistorien"

    doc = Dokument(udfil, bog, titel, pagesize=A4,
                   leftMargin=28 * mm, rightMargin=28 * mm,
                   topMargin=24 * mm if bog else 22 * mm, bottomMargin=22 * mm,
                   title=titel, author="Slægtstræet i webtrees")
    ramme = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    W, H = doc.width, doc.height
    doc.addPageTemplates([
        PageTemplate(id="forside", frames=[ramme]),
        PageTemplate(id="indhold", frames=[ramme], onPageEnd=doc.kun_sidetal),
        PageTemplate(id="tekst", frames=[ramme], onPage=doc.sidestart, onPageEnd=doc.sideslut),
    ])

    indhold = byg(md, W, H, mdmappe, bog)
    if bog:
        toc = TableOfContents(dotsMinLevel=0)
        toc.levelStyles = [S["toc0"], S["toc1"]]
        historie = (forside(titel, meta, W, H, mdmappe, ind)
                    + [NextPageTemplate("indhold"), PageBreak(),
                       Paragraph("Indhold", S["indhold"]), toc,
                       NextPageTemplate("tekst"), PageBreak()] + indhold)
        doc.multiBuild(historie)
    else:
        doc.pageTemplates.insert(0, doc.pageTemplates.pop(2))   # «tekst» foerst
        doc.build(indhold)

    for k in BRUGTE_KLIP:
        print("klip:", k)
    if _MANGLER:
        print("ADVARSEL: ingen skrift kan tegne:", " ".join(sorted(_MANGLER)))
    print("skrevet:", udfil)


if __name__ == "__main__":
    main()
