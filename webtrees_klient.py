#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webtrees_klient — opret poster i webtrees ved at drive dets egne formularer.

Webtrees har ingen API. Klienten logger ind som en almindelig bruger og poster
de samme felter, som browseren gør. Login læses fra en fil, brugeren selv
opretter (standard: %USERPROFILE%\\.webtrees\\login.json):

    {"base_url": "http://din-nas.dit-tailnet.ts.net:8081",
     "tree": "aner", "username": "ai", "password": "..."}

Kodeordet holdes i én lokal variabel, sendes kun i login-formularen og
maskeres i al output. Filen må ikke ligge på et netværksdrev eller i
scriptets egen mappe.

Brug:
    python webtrees_klient.py --check
    python webtrees_klient.py --dry-run poster/job.json
    python webtrees_klient.py poster/job.json
    python webtrees_klient.py poster/job.json --set KILDE=S12 --set EDIT=X20

Jobformat: se poster/README-DA.md.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html
import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSION = "1.0"
USER_AGENT = "webtrees_klient/" + VERSION

# Ops der opretter et nyt individ og derfor kræver 1 SEX + 1 NAME
INDIVIDUAL_OPS = {"add-parent", "add-child", "add-spouse", "add-spouse-to-family", "add-unlinked"}

# Sti-felt per op (feltet i jobbet, der peger på den eksisterende post)
TARGET_FIELD = {
    "add-parent": "child",
    "add-child": "family",
    "add-spouse": "individual",
    "add-spouse-to-family": "family",
    "add-fact": "target",
    "edit-fact": "target",
    # Kæder en person, der ALLEREDE findes, ind i en familie, der ALLEREDE findes.
    # Xref'et i URL'en er barnet; familien sendes som formularfeltet `famid`.
    "link-child-to-family": "child",
}

LINE_RE = re.compile(r"([0-9]) ([A-Z0-9_]+)(?: (.*))?", re.S)
PLACEHOLDER_RE = re.compile(r"@([A-Za-z][A-Za-z0-9_]*(?:\.(?:FAMS|FAMC))?)@")
SURNAME_RE = re.compile(r"/([^/]*)/")


class WebtreesError(Exception):
    """Fejl, der skal vises pænt uden traceback."""


# --------------------------------------------------------------------------- #
# Hjælpere
# --------------------------------------------------------------------------- #

def redact(text: str, secret: str | None) -> str:
    if secret and text:
        return text.replace(secret, "***")
    return text


def parse_line(line: str) -> tuple[str, str, str]:
    m = LINE_RE.fullmatch(line.strip())
    if not m:
        raise WebtreesError("Ugyldig GEDCOM-linje: %r (forventet 'niveau TAG værdi')" % line)
    level, tag, value = m.group(1), m.group(2), m.group(3) or ""
    return level, tag, value


def validate_lines(lines: list[str], *, needs_person: bool, needs_value: bool) -> None:
    if not lines:
        raise WebtreesError("Tom linjeliste")
    parsed = [parse_line(l) for l in lines]
    if parsed[0][0] != "1":
        raise WebtreesError("Første linje skal være niveau 1: %r" % lines[0])
    prev = 0
    for (level, tag, value), raw in zip(parsed, lines):
        lv = int(level)
        if lv > prev + 1:
            raise WebtreesError("Niveau springer fra %d til %d ved %r" % (prev, lv, raw))
        prev = lv
    if needs_person:
        sexes = [v for l, t, v in parsed if l == "1" and t == "SEX"]
        if len(sexes) != 1 or sexes[0] not in ("M", "F", "U"):
            raise WebtreesError("Personoprettelse kræver præcis én linje '1 SEX M|F|U'")
        if not any(l == "1" and t == "NAME" for l, t, v in parsed):
            raise WebtreesError("Personoprettelse kræver en linje '1 NAME ...'")
    if needs_value and not any(v.strip() for l, t, v in parsed):
        raise WebtreesError("add-fact uden nogen værdi ville slette — afvist")


def surname_of(lines: list[str]) -> str | None:
    for l in lines:
        level, tag, value = parse_line(l)
        if level == "1" and tag == "NAME":
            m = SURNAME_RE.search(value)
            return (m.group(1).strip() if m else value.strip()) or None
    return None


def lines_to_pairs(prefix: str, lines: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for l in lines:
        level, tag, value = parse_line(l)
        pairs.append((prefix + "levels[]", level))
        pairs.append((prefix + "tags[]", tag))
        pairs.append((prefix + "values[]", value))
    return pairs


def paa_netvaerk(p: Path) -> bool:
    """Sand, hvis stien ligger på et netværksshare: en UNC-sti (\\\\server\\...)
    eller et tilknyttet netværksdrev (fx et netværksdrev som Z:). Netværksmapper backes ofte op
    eller synkroniseres, og dér må et kodeord ikke ligge."""
    s = str(p).replace("/", "\\")
    if s.startswith("\\\\"):
        return True
    if os.name == "nt" and p.drive:
        import ctypes
        return ctypes.windll.kernel32.GetDriveTypeW(p.drive + "\\") == 4  # DRIVE_REMOTE
    return False


def load_creds(path: Path, script_dir: Path) -> dict:
    p = path.expanduser().resolve()
    if paa_netvaerk(p):
        raise WebtreesError("Login-filen må ikke ligge på et netværksdrev: %s" % p)
    try:
        p.relative_to(script_dir.resolve())
        raise WebtreesError("Login-filen må ikke ligge i scriptets egen mappe: %s" % p)
    except ValueError:
        pass
    if not p.exists():
        raise WebtreesError(
            "Login-fil mangler: %s\nOpret den selv med indholdet\n"
            '  {"base_url": "http://...:8081", "tree": "aner", "username": "ai", "password": "..."}' % p
        )
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as e:  # noqa: BLE001
        raise WebtreesError("Kan ikke læse login-filen som JSON: %s" % e) from None
    for key in ("base_url", "tree", "username", "password"):
        if not data.get(key):
            raise WebtreesError("Login-filen mangler feltet %r" % key)
    data["base_url"] = data["base_url"].rstrip("/")
    return data


# --------------------------------------------------------------------------- #
# HTTP-klient
# --------------------------------------------------------------------------- #

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


class WebtreesClient:
    def __init__(self, base_url: str, tree: str, *, verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.tree = tree
        self.verbose = verbose
        self.csrf: str | None = None
        self._secret: str | None = None
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(self.jar))

    # -- lavniveau ---------------------------------------------------------- #

    def _url(self, path: str) -> str:
        return self.base_url + path

    def _log(self, msg: str) -> None:
        if self.verbose:
            print("  · " + redact(msg, self._secret))

    def _request(self, method: str, path: str, data: bytes | None = None,
                 headers: dict | None = None) -> tuple[int, dict, str]:
        req = urllib.request.Request(self._url(path), data=data, method=method)
        req.add_header("User-Agent", USER_AGENT)
        req.add_header("Accept", "text/html,application/json;q=0.9,*/*;q=0.8")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            resp = self.opener.open(req, timeout=30)
            status, hdrs, body = resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as e:            # 3xx/4xx/5xx havner her
            status, hdrs, body = e.code, dict(e.headers), e.read()
        except urllib.error.URLError as e:
            raise WebtreesError(
                "Kan ikke nå %s (%s). Kører Tailscale?" % (self.base_url, e.reason)
            ) from None
        # Serveren sender headernavne med småt; gør opslag versaluafhængige.
        hdrs = {k.lower(): v for k, v in hdrs.items()}
        text = body.decode("utf-8", "replace")
        loc = hdrs.get("location", "")
        self._log("%s %s -> %s%s" % (method, path, status, ("  Location: " + loc) if loc else ""))
        return status, hdrs, text

    @staticmethod
    def _path_of(url: str) -> str:
        return urllib.parse.urlsplit(url).path

    @staticmethod
    def _csrf_from_html(text: str) -> str | None:
        m = re.search(r'<meta name="csrf" content="([^"]+)"', text)
        return html.unescape(m.group(1)) if m else None

    def _post(self, path: str, pairs: list[tuple[str, str]], *, ajax: bool = False) -> tuple[int, dict, str]:
        if self.csrf is None:
            raise WebtreesError("Ingen CSRF-token — kald login() først")
        if len(pairs) > 200:
            print("  ! Advarsel: %d formularfelter — PHP max_input_vars kan afkorte" % len(pairs))
        body = urllib.parse.urlencode(pairs + [("_csrf", self.csrf)], encoding="utf-8").encode("ascii")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-CSRF-TOKEN": self.csrf,
        }
        if ajax:
            headers["X-Requested-With"] = "XMLHttpRequest"
        status, hdrs, text = self._request("POST", path, body, headers)
        loc = hdrs.get("location", "")
        if status in (301, 302, 303, 307, 308):
            lp = self._path_of(loc)
            if lp == path:
                raise WebtreesError("CSRF-fejl (webtrees sendte tilbage til samme side): %s" % path)
            if lp.startswith("/login"):
                raise WebtreesError("Sessionen er tabt — ikke logget ind længere")
        return status, hdrs, text

    @staticmethod
    def _excerpt(text: str, n: int = 300) -> str:
        t = re.sub(r"(?is)<(script|style|nav|header)[^>]*>.*?</\1>", " ", text)
        t = html.unescape(re.sub(r"(?s)<[^>]+>", " ", t))
        t = re.sub(r"\s+", " ", t).strip()
        m = re.search(r"(alert[^.]{0,200}|Fejl[^.]{0,200}|Error[^.]{0,200})", t)
        return (m.group(0) if m else t)[:n]

    # -- session ------------------------------------------------------------ #

    def bootstrap(self) -> None:
        path = "/login/%s" % self.tree
        status, hdrs, text = self._request("GET", path)
        if status in (301, 302):
            status, hdrs, text = self._request("GET", self._path_of(hdrs.get("location", "")) or path)
        if status != 200:
            raise WebtreesError("Login-siden svarede %s" % status)
        self.csrf = self._csrf_from_html(text)
        if not self.csrf:
            raise WebtreesError("Fandt ingen CSRF-token på login-siden")

    def login(self, username: str, password: str) -> None:
        self._secret = password
        self.bootstrap()
        path = "/login/%s" % self.tree
        pairs = [("username", username), ("password", password), ("url", self._url("/tree/%s" % self.tree))]
        body = urllib.parse.urlencode(pairs + [("_csrf", self.csrf)], encoding="utf-8").encode("ascii")
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-CSRF-TOKEN": self.csrf}
        status, hdrs, text = self._request("POST", path, body, headers)
        loc_path = self._path_of(hdrs.get("location", ""))
        if status not in (302, 303) or loc_path.startswith("/login"):
            raise WebtreesError("Login afvist for brugeren %r (forkert kodeord, ikke verificeret eller ikke godkendt?)" % username)
        self.check_editor()

    def check_editor(self) -> None:
        path = "/tree/%s/add-unlinked-individual" % self.tree
        status, hdrs, text = self._request("GET", path)
        if status == 200:
            tok = self._csrf_from_html(text)
            if tok:
                self.csrf = tok
            return
        if status in (302, 303) and self._path_of(hdrs.get("location", "")).startswith("/login"):
            raise WebtreesError("Ikke logget ind")
        raise WebtreesError("Brugeren mangler redaktørrettigheder på træet %r (svar %s)" % (self.tree, status))

    # -- oprettelse --------------------------------------------------------- #

    def create_source(self, f: dict) -> str:
        pairs = [
            ("source-title", f.get("title", "")),
            ("source-abbreviation", f.get("abbreviation", "")),
            ("source-author", f.get("author", "")),
            ("source-publication", f.get("publication", "")),
            ("source-call-number", f.get("call_number", "")),
            ("source-text", f.get("text", "")),
            ("restriction", ""),
        ]
        if not pairs[0][1].strip():
            raise WebtreesError("create-source kræver 'title'")
        status, hdrs, text = self._post("/tree/%s/create-source" % self.tree, pairs, ajax=True)
        if status != 200:
            raise WebtreesError("create-source svarede %s: %s" % (status, self._excerpt(text)))
        try:
            value = json.loads(text)["value"]
        except Exception:  # noqa: BLE001
            raise WebtreesError("create-source gav ikke JSON: %s" % self._excerpt(text)) from None
        m = re.fullmatch(r"@([A-Za-z0-9_]+)@", value)
        if not m:
            raise WebtreesError("Uventet kilde-xref: %r" % value)
        return m.group(1)

    def create_media(self, f: dict) -> str:
        """Opretter et medieobjekt for en fil, der ALLEREDE ligger i mediemappen.

        'file' er stien relativt til `data/media/`, fx
        "kirkeboger/1919-eksempelsogn-opslag-35.jpg". Filen skal ligge der i forvejen —
        klienten uploader ikke, den peger.
        """
        rel = f.get("file", "").strip().lstrip("/")
        if not rel:
            raise WebtreesError("create-media kræver 'file' (sti under data/media/)")
        if not f.get("title", "").strip():
            raise WebtreesError("create-media kræver 'title'")
        pairs = [
            ("file_location", "unused"),
            ("unused", rel),
            ("title", f["title"]),
            ("type", f.get("type", "")),
            ("media-note", f.get("note", "")),
            ("restriction", ""),
        ]
        status, hdrs, text = self._post("/tree/%s/create-media-object" % self.tree, pairs, ajax=True)
        if status != 200:
            raise WebtreesError("create-media svarede %s: %s" % (status, self._excerpt(text)))
        try:
            value = json.loads(text)["value"]
        except Exception:  # noqa: BLE001
            raise WebtreesError(
                "create-media gav ikke JSON — ligger filen %r i data/media/? Svar: %s"
                % (rel, self._excerpt(text))) from None
        m = re.fullmatch(r"@([A-Za-z0-9_]+)@", value)
        if not m:
            raise WebtreesError("Uventet medie-xref: %r" % value)
        return m.group(1)

    def add_individual(self, op: str, target: str | None, lines: list[str],
                       family_lines: list[str] | None = None) -> str:
        t = self.tree
        if op == "add-parent":
            path = "/tree/%s/add-parent-to-individual/%s" % (t, target)
        elif op == "add-child":
            path = "/tree/%s/add-child-to-family/%s" % (t, target)
        elif op == "add-spouse":
            path = "/tree/%s/add-spouse-to-individual/%s" % (t, target)
        elif op == "add-spouse-to-family":
            path = "/tree/%s/add-spouse-to-family/%s" % (t, target)
        elif op == "add-unlinked":
            path = "/tree/%s/add-unlinked-individual" % t
        else:
            raise WebtreesError("Ukendt op: %s" % op)
        pairs = lines_to_pairs("i", lines)
        if op in ("add-spouse", "add-spouse-to-family"):
            pairs += lines_to_pairs("f", family_lines or [])
        status, hdrs, text = self._post(path, pairs)
        if status in (302, 303):
            m = re.search(r"/individual/([^/?#]+)", self._path_of(hdrs.get("location", "")))
            if m:
                return m.group(1)
            raise WebtreesError("%s: omdirigerede til %s — fandt intet individ-xref" % (op, hdrs.get("location")))
        if status == 200:
            raise WebtreesError("%s: formularen blev vist igen (valideringsfejl?): %s" % (op, self._excerpt(text)))
        raise WebtreesError("%s svarede %s: %s" % (op, status, self._excerpt(text)))

    def link_child_to_family(self, child: str, family: str, pedi: str = "") -> str:
        """Kæder et EKSISTERENDE barn ind i en EKSISTERENDE familie.

        Modstykket til `add-child`, som altid opretter en ny person. Formularen
        ligger på /tree/<træ>/link-child-to-family/<barn> og vil kun have `famid`
        (familiens xref) og `PEDI`. Tom PEDI er brugerfladens egen standard og
        betyder fødsel — GEDCOM udelader da tagget helt.

        Kædningen er reversibel i brugerfladen («fjern fra familien»), til forskel
        fra en dublet, der kun kan slettes af brugeren selv i brugerfladen.
        """
        if pedi and pedi not in ("BIRTH", "ADOPTED", "FOSTER", "SEALING", "RADA"):
            raise WebtreesError("link-child-to-family: ukendt PEDI %r" % pedi)
        path = "/tree/%s/link-child-to-family/%s" % (self.tree, child)
        status, hdrs, text = self._post(path, [("famid", family), ("PEDI", pedi)])
        if status in (302, 303):
            return child
        if status == 200:
            raise WebtreesError(
                "link-child-to-family: formularen blev vist igen — findes familien %s, "
                "og er %s allerede barn et andet sted? %s" % (family, child, self._excerpt(text)))
        raise WebtreesError("link-child-to-family svarede %s: %s" % (status, self._excerpt(text)))

    def add_fact(self, xref: str, lines: list[str]) -> None:
        path = "/tree/%s/update-fact/%s/new" % (self.tree, xref)
        status, hdrs, text = self._post(path, lines_to_pairs("", lines))
        if status not in (302, 303):
            raise WebtreesError("add-fact svarede %s: %s" % (status, self._excerpt(text)))

    def find_fact_id(self, xref: str, match: str) -> tuple[str, str]:
        """Finder den ene kendsgerning på en post, hvis første linje starter med `match`.

        Returnerer (fact_id, den nuværende GEDCOM-tekst). Rejser fejl ved 0 eller
        flere end ét træf — så et 'ret dette' aldrig rammer den forkerte kendsgerning.
        """
        status, hdrs, text = self._request("GET", "/tree/%s/edit-raw/%s" % (self.tree, xref))
        if status != 200:
            raise WebtreesError("Kunne ikke læse %s (edit-raw svarede %s)" % (xref, status))
        ids = re.findall(r'<input[^>]*name="fact_id\[\]"[^>]*value="([^"]*)"', text)
        facts = re.findall(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', text)
        if len(ids) != len(facts):
            raise WebtreesError("%s: %d fact_id men %d kendsgerninger — kan ikke parre dem sikkert"
                                % (xref, len(ids), len(facts)))
        hits = [(i, html.unescape(f).strip()) for i, f in zip(ids, facts)
                if html.unescape(f).strip().startswith(match)]
        if not hits:
            raise WebtreesError("%s: ingen kendsgerning starter med %r" % (xref, match))
        if len(hits) > 1:
            raise WebtreesError("%s: %d kendsgerninger starter med %r — gør 'match' mere præcis"
                                % (xref, len(hits), match))
        return hits[0]

    def edit_fact(self, xref: str, fact_id: str, lines: list[str]) -> None:
        """Erstatter en eksisterende kendsgerning. Tomme linjer ville SLETTE den."""
        if not any((parse_line(l)[2] or "").strip() for l in lines):
            raise WebtreesError("edit-fact: mindst én linje skal have en værdi "
                                "(en tom kendsgerning sletter posten)")
        path = "/tree/%s/update-fact/%s/%s" % (self.tree, xref, fact_id)
        status, hdrs, text = self._post(path, lines_to_pairs("", lines))
        if status not in (302, 303):
            raise WebtreesError("edit-fact svarede %s: %s" % (status, self._excerpt(text)))

    # -- opslag ------------------------------------------------------------- #

    def get_family_link(self, xref: str, tag: str = "FAMS") -> str:
        """Første '1 FAMS/FAMC @F@' hos et individ — læses fra edit-raw-siden."""
        status, hdrs, text = self._request("GET", "/tree/%s/edit-raw/%s" % (self.tree, xref))
        if status == 200:
            for ta in re.findall(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', text):
                m = re.search(r"^1 %s @([^@]+)@" % tag, html.unescape(ta), re.M)
                if m:
                    return m.group(1)
        # fallback: personsiden (nyoprettet forælder har præcis én familie)
        status, hdrs, text = self.get_individual_page(xref)
        m = re.search(r"/tree/%s/family/([^/?#\"]+)" % re.escape(self.tree), text)
        if m:
            return m.group(1)
        raise WebtreesError("Fandt ingen %s-familie for %s — er ændringen godkendt (auto-accept)?" % (tag, xref))

    def get_individual_page(self, xref: str) -> tuple[int, dict, str]:
        path = "/tree/%s/individual/%s" % (self.tree, xref)
        status, hdrs, text = self._request("GET", path)
        if status in (301, 302):
            status, hdrs, text = self._request("GET", self._path_of(hdrs.get("location", "")))
        return status, hdrs, text

    def verify_individual(self, xref: str, surname: str | None) -> None:
        status, hdrs, text = self.get_individual_page(xref)
        if status != 200:
            raise WebtreesError("Kontrol af %s fejlede (HTTP %s)" % (xref, status))
        if surname and surname not in html.unescape(text):
            raise WebtreesError(
                "%s blev oprettet, men efternavnet %r ses ikke på siden — "
                "er 'Godkend ændringer foreslået af denne bruger' slået til?" % (xref, surname)
            )


# --------------------------------------------------------------------------- #
# Job-kørsel
# --------------------------------------------------------------------------- #

def resolve(value: str, results: dict[str, str], known: set[str], *, bare: bool, dry: bool) -> str:
    """@ID@ opslås kun, hvis ID er et op-id i jobbet (eller sat med --set).

    Alt andet — fx @X8@ eller @X6@ — er en almindelig GEDCOM-henvisning til en
    post, der allerede findes i træet, og lades urørt.
    """
    def sub(m: re.Match) -> str:
        key = m.group(1)
        if key in results:
            return results[key] if bare else "@%s@" % results[key]
        if key.split(".")[0] not in known:
            return m.group(0)                      # literal GEDCOM-henvisning
        if dry:
            return "@?%s?@" % key
        raise WebtreesError("Uløst placeholder @%s@ — op %r er ikke kørt endnu"
                            % (key, key.split(".")[0]))
    return PLACEHOLDER_RE.sub(sub, value)


def validate_op(op: dict) -> None:
    kind = op.get("op")
    if not kind:
        raise WebtreesError("Op mangler 'op'")
    if not op.get("id"):
        raise WebtreesError("Op %r mangler 'id'" % kind)
    if kind == "create-source":
        if not op.get("title"):
            raise WebtreesError("%s: create-source kræver 'title'" % op["id"])
        return
    if kind == "create-media":
        for felt in ("title", "file"):
            if not op.get(felt):
                raise WebtreesError("%s: create-media kræver %r" % (op["id"], felt))
        return
    if kind == "link-child-to-family":
        if not op.get("family"):
            raise WebtreesError("%s: link-child-to-family kræver 'family'" % op["id"])
        if op.get("lines"):
            raise WebtreesError("%s: link-child-to-family tager ingen 'lines' — "
                                "den kæder kun to poster sammen" % op["id"])
    elif kind in INDIVIDUAL_OPS:
        validate_lines(op.get("lines", []), needs_person=True, needs_value=False)
        if op.get("family_lines"):
            validate_lines(op["family_lines"], needs_person=False, needs_value=False)
    elif kind == "add-fact":
        validate_lines(op.get("lines", []), needs_person=False, needs_value=True)
    elif kind == "edit-fact":
        validate_lines(op.get("lines", []), needs_person=False, needs_value=True)
        if not op.get("match"):
            raise WebtreesError("%s: edit-fact kræver 'match' (fx \"1 BIRT\") — "
                                "den kendsgerning, der skal erstattes" % op["id"])
    else:
        raise WebtreesError("Ukendt op-type %r i %s" % (kind, op["id"]))
    field = TARGET_FIELD.get(kind)
    if field and not op.get(field):
        raise WebtreesError("%s: %s kræver feltet %r" % (op["id"], kind, field))


def describe_op(op: dict, results: dict[str, str], known: set[str], tree: str) -> tuple[str, list[tuple[str, str]]]:
    """Endpoint + formularfelter for --dry-run (placeholders uløste vises som @?ID?@)."""
    kind = op["op"]
    r = lambda s, bare=False: resolve(s, results, known, bare=bare, dry=True)  # noqa: E731
    if kind == "create-source":
        return "POST /tree/%s/create-source" % tree, [
            ("source-title", op.get("title", "")), ("source-abbreviation", op.get("abbreviation", "")),
            ("source-author", op.get("author", "")), ("source-publication", op.get("publication", "")),
            ("source-call-number", op.get("call_number", "")), ("source-text", op.get("text", "")),
            ("restriction", "")]
    if kind == "create-media":
        return "POST /tree/%s/create-media-object" % tree, [
            ("file_location", "unused"), ("unused", op.get("file", "")),
            ("title", op.get("title", "")), ("type", op.get("type", "")),
            ("media-note", op.get("note", "")), ("restriction", "")]
    if kind == "link-child-to-family":
        return ("POST /tree/%s/link-child-to-family/%s" % (tree, r(op["child"], True)),
                [("famid", r(op["family"], True)), ("PEDI", op.get("pedi", ""))])
    lines = [r(l) for l in op.get("lines", [])]
    if kind == "add-fact":
        return "POST /tree/%s/update-fact/%s/new" % (tree, r(op["target"], True)), lines_to_pairs("", lines)
    if kind == "edit-fact":
        return ("POST /tree/%s/update-fact/%s/<fact_id for %r>"
                % (tree, r(op["target"], True), op.get("match", "")), lines_to_pairs("", lines))
    paths = {
        "add-parent": "/add-parent-to-individual/%s", "add-child": "/add-child-to-family/%s",
        "add-spouse": "/add-spouse-to-individual/%s", "add-spouse-to-family": "/add-spouse-to-family/%s",
        "add-unlinked": "/add-unlinked-individual",
    }
    field = TARGET_FIELD.get(kind)
    path = paths[kind] % r(op[field], True) if field else paths[kind]
    pairs = lines_to_pairs("i", lines)
    if kind in ("add-spouse", "add-spouse-to-family"):
        pairs += lines_to_pairs("f", [r(l) for l in op.get("family_lines", [])])
    return "POST /tree/%s%s" % (tree, path), pairs


def run_op(client: WebtreesClient, op: dict, results: dict[str, str], known: set[str]) -> str:
    kind, oid = op["op"], op["id"]
    r = lambda s, bare=False: resolve(s, results, known, bare=bare, dry=False)  # noqa: E731
    if kind == "create-source":
        return client.create_source(op)
    if kind == "create-media":
        return client.create_media(op)
    if kind == "link-child-to-family":
        barn, fam = r(op["child"], True), r(op["family"], True)
        print("  · kæder %s ind i familien %s" % (barn, fam))
        return client.link_child_to_family(barn, fam, op.get("pedi", ""))
    lines = [r(l) for l in op.get("lines", [])]
    if kind == "add-fact":
        client.add_fact(r(op["target"], True), lines)
        return r(op["target"], True)
    if kind == "edit-fact":
        target = r(op["target"], True)
        fact_id, before = client.find_fact_id(target, op["match"])
        print("  · erstatter i %s: %s" % (target, before.split("\n")[0]))
        client.edit_fact(target, fact_id, lines)
        return target
    field = TARGET_FIELD.get(kind)
    target = r(op[field], True) if field else None
    fam_lines = [r(l) for l in op.get("family_lines", [])] or None
    xref = client.add_individual(kind, target, lines, fam_lines)
    client.verify_individual(xref, surname_of(lines))
    return xref


def needs_family_lookup(job_ops: list[dict], known: set[str]) -> set[str]:
    keys: set[str] = set()
    for op in job_ops:
        for v in [op.get(TARGET_FIELD.get(op.get("op", ""), ""), "")] + op.get("lines", []) + op.get("family_lines", []):
            for m in PLACEHOLDER_RE.finditer(v or ""):
                key = m.group(1)
                if "." in key and key.split(".")[0] in known:
                    keys.add(key)
    return keys


def run_job(client: WebtreesClient, job_path: Path, presets: dict[str, str], *, dry: bool) -> dict[str, str]:
    job = json.loads(job_path.read_text(encoding="utf-8-sig"))
    ops = job.get("ops") or []
    if not ops:
        raise WebtreesError("Jobbet har ingen 'ops'")
    for op in ops:
        validate_op(op)
    results: dict[str, str] = dict(presets)
    tree = job.get("tree") or client.tree
    known = {op["id"] for op in ops} | {k.split(".")[0] for k in presets}

    if dry:
        print("Tørkørsel af %s (%d ops) mod træ %r — intet sendes.\n" % (job_path.name, len(ops), tree))
        for op in ops:
            endpoint, pairs = describe_op(op, results, known, tree)
            print("[%s] %s\n  %s" % (op["id"], op["op"], endpoint))
            for k, v in pairs:
                print("    %-12s %s" % (k, v))
            print()
        return results

    result_file = job_path.with_suffix(".result.json")
    log_file = job_path.parent / "log.jsonl"
    print("Kører %s (%d ops) mod %s / %s" % (job_path.name, len(ops), client.base_url, tree))
    for op in ops:
        oid = op["id"]
        if oid in results:
            print("[%s] springes over — allerede %s" % (oid, results[oid]))
            continue
        # afledte nøgler (FAMS/FAMC) slås op lige før brug
        for key in needs_family_lookup([op], known):
            if key not in results:
                base, tag = key.split(".")
                if base not in results:
                    raise WebtreesError("@%s@ kræver at %s er oprettet først" % (key, base))
                results[key] = client.get_family_link(results[base], tag)
                print("  · %s = %s" % (key, results[key]))
        status = "ok"
        try:
            results[oid] = run_op(client, op, results, known)
            print("[%s] %s -> %s" % (oid, op["op"], results[oid]))
        except WebtreesError as e:
            status = "fejl: %s" % e
            raise
        finally:
            result_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            with log_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "tid": _dt.datetime.now().isoformat(timespec="seconds"),
                    "job": job_path.name, "op": oid, "type": op["op"], "status": status,
                    "xref": results.get(oid),
                }, ensure_ascii=False) + "\n")
    print("\nFærdig. Oprettet:")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return results


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    ap = argparse.ArgumentParser(description="Opret poster i webtrees via dets egne formularer.")
    ap.add_argument("job", nargs="?", help="jobfil (JSON)")
    ap.add_argument("--check", action="store_true", help="test kun login og redaktørrettigheder")
    ap.add_argument("--dry-run", action="store_true", help="vis hvad der ville blive sendt; intet netværk")
    ap.add_argument("--set", action="append", default=[], metavar="ID=XREF",
                    help="forudsæt et xref for et id (springer den op over)")
    ap.add_argument("--creds", default=os.environ.get("WEBTREES_LOGIN") or str(Path.home() / ".webtrees" / "login.json"),
                    help="login-fil (standard: %%USERPROFILE%%\\.webtrees\\login.json)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    presets: dict[str, str] = {}
    for s in args.set:
        if "=" not in s:
            ap.error("--set forventer ID=XREF")
        k, v = s.split("=", 1)
        presets[k.strip()] = v.strip()

    secret = None
    try:
        if args.dry_run:
            if not args.job:
                ap.error("--dry-run kræver en jobfil")
            client = WebtreesClient("http://dry-run.invalid", "aner", verbose=args.verbose)
            job = json.loads(Path(args.job).read_text(encoding="utf-8-sig"))
            client.tree = job.get("tree") or client.tree
            run_job(client, Path(args.job), presets, dry=True)
            return 0

        creds = load_creds(Path(args.creds), Path(__file__).parent)
        secret = creds["password"]
        client = WebtreesClient(creds["base_url"], creds["tree"], verbose=args.verbose)
        client.login(creds["username"], creds["password"])
        print("Logget ind som %r på %s · redaktør på træet %r: OK" % (creds["username"], creds["base_url"], creds["tree"]))
        if args.check or not args.job:
            return 0
        run_job(client, Path(args.job), presets, dry=False)
        return 0
    except WebtreesError as e:
        print("FEJL: " + redact(str(e), secret), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAfbrudt.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
