#!/usr/bin/env python3
"""check.py — validate every template against the vault's structural rules.

Stdlib only (no deps). Parses HTML properly instead of grepping, so visible
text that merely mentions a URL (or the word "lorem ipsum" in a rule comment)
is never confused with a real violation. Styling is each template's own
business — this enforces structure, not taste.

    ./check.py            validate the repo this file lives in
    ./check.py --selftest run the built-in checks on the validator itself
    ./check.py --plain    no colour / no banner (also auto-off when piped)

Exits non-zero if anything fails, so it drops into CI or a pre-commit hook.

ponytail: one file, stdlib only. The HTML parser is the rigorous core; the
selftest guards it. "Every *fillable* string has a data-slot" can't be proven
by a machine, so we require at least one and trust the rules for the rest.
"""
import os, re, sys, html.parser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDIT_JS = "../../edit.js"
NS_OK = re.compile(r"(w3\.org|purl\.org|xml)", re.I)   # namespace URLs, not fetches
CSS_REMOTE = re.compile(r"""(?:url\(\s*["']?|@import\s+["']?)\s*(//|https?://)""", re.I)

# ---- phosphor terminal styling (auto-off when piped or NO_COLOR/--plain) -----
_ON = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None and "--plain" not in sys.argv
def c(s, code):
    return f"\033[{code}m{s}\033[0m" if _ON else s

_BW = 44  # interior width; ljust keeps the right border aligned regardless of text
def banner():
    return [
        c("  ┌" + "─" * (_BW + 2) + "┐", "92"),
        c("  │ " + "the old web showroom · integrity".ljust(_BW) + " │", "92"),
        c("  └" + "─" * (_BW + 2) + "┘", "92"),
    ]


class Scan(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.style_tag = self.data_slot = self.edit_js = False
        self.stylesheets = []          # hrefs of <link rel=stylesheet>
        self.remote = []               # remote resource refs in attributes
        self.text_parts = []           # visible text only — comments excluded

    def handle_data(self, data):
        self.text_parts.append(data)

    def handle_starttag(self, tag, attrs):
        d = {k: (v or "") for k, v in attrs}
        if tag == "style":
            self.style_tag = True
        if any(k == "data-slot" for k, _ in attrs):
            self.data_slot = True
        if tag == "script" and d.get("src", "").strip() == EDIT_JS:
            self.edit_js = True
        if tag == "link" and "stylesheet" in d.get("rel", "").lower().split():
            self.stylesheets.append(d.get("href", "").strip())
        for k, v in d.items():
            if k.startswith("xmlns"):
                continue  # namespace declaration, not a fetch
            if k in ("src", "href", "poster", "data", "xlink:href"):
                u = v.strip()
                if (u.startswith("//") or re.match(r"https?://", u, re.I)) and not NS_OK.search(u):
                    self.remote.append(f"{k}={u}")


def check_html(path, fails):
    s = Scan()
    s.feed(path.read_text(encoding="utf-8", errors="replace"))
    b = path.name
    if s.style_tag:
        fails.append(f"{b}: inline <style> tag")
    if not s.data_slot:
        fails.append(f"{b}: no data-slot")
    if not s.edit_js:
        fails.append(f'{b}: missing <script src="{EDIT_JS}">')
    if not s.stylesheets:
        fails.append(f"{b}: no external stylesheet <link>")
    for href in s.stylesheets:
        if not href.startswith(("http", "//")) and not (path.parent / href).is_file():
            fails.append(f"{b}: stylesheet '{href}' not found")
    for r in s.remote:
        fails.append(f"{b}: remote resource {r}")
    if "lorem ipsum" in " ".join(s.text_parts).lower():
        fails.append(f"{b}: lorem ipsum placeholder in visible text")


def check_template(d):
    fails = []
    if not (d / "index.html").is_file():
        fails.append("no index.html")
    if not (d / "style.css").is_file():
        fails.append("no style.css")
    for f in sorted(d.rglob("*")):
        if not f.is_file():
            continue
        if f.suffix == ".html":
            check_html(f, fails)
            continue
        body = f.read_text(encoding="utf-8", errors="replace")
        if "lorem ipsum" in body.lower():
            fails.append(f"{f.name}: lorem ipsum placeholder")
        if f.suffix == ".css":
            for proto in CSS_REMOTE.findall(body):
                fails.append(f"{f.name}: remote url()/@import ({proto})")
    return fails


def validate(root, quiet=False):
    out = (lambda *a: None) if quiet else (lambda *a: print(*a))
    tdir, index = root / "templates", root / "index.html"
    total = bad = 0

    def verdict(slug, fails):              # one grouped line per slug — never two verdicts
        nonlocal total, bad
        total += 1
        if fails:
            bad += 1
            out("  " + c("✗", "91") + " " + c(slug, "1"))
            for x in fails:
                out("      " + c(x, "2"))
        else:
            out("  " + c("✓", "92") + " " + slug)

    if not quiet:
        for ln in banner():
            out(ln)
        out("")

    if not index.is_file():
        out("  " + c("✗", "91") + " no index.html at repo root"); return 1
    idx_text = index.read_text(encoding="utf-8")
    reg = set(re.findall(r'\bs\s*:\s*"([^"]+)"', idx_text))
    folders = {p.name for p in tdir.iterdir() if p.is_dir()}

    if "const T" not in idx_text:
        verdict("index.html", ["no T array / showroom list"])
    for d in sorted(p for p in tdir.iterdir() if p.is_dir()):
        fails = check_template(d)
        if not d.name.startswith("_") and d.name not in reg:
            fails.append("not registered in index.html")
        verdict(d.name, fails)
    for slug in sorted(reg - folders):     # registered but missing — orphan showroom entry
        verdict(slug, ["registered in index.html but no template folder"])

    out("  " + c("─" * (_BW + 2), "2"))
    if bad == 0:
        out("  " + c(f"{total} templates · all clear", "92"))
    else:
        out("  " + c(f"{total - bad} ok · {bad} failed", "91"))
    return 1 if bad else 0


def selftest():
    import tempfile, textwrap
    good = textwrap.dedent('''\
        <!doctype html><html><head><link rel="stylesheet" href="style.css"></head>
        <body><h1 data-slot="site-name">Hi</h1>
        <svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>
        <script src="../../edit.js" defer></script></body></html>''')
    with tempfile.TemporaryDirectory() as t:
        r = Path(t); (r / "templates" / "good").mkdir(parents=True)
        (r / "index.html").write_text('<script>const T=[{s:"good"}]</script>')
        (r / "templates" / "good" / "index.html").write_text(good)
        (r / "templates" / "good" / "style.css").write_text("body{color:red}")
        assert validate(r, quiet=True) == 0, "clean repo should pass"

        g = r / "templates" / "good" / "index.html"
        for bad in [
            good.replace('data-slot="site-name"', ''),                        # no slot
            good.replace('<script src="../../edit.js" defer></script>', ''),  # no edit.js
            good.replace('<link rel="stylesheet" href="style.css">', ''),     # no stylesheet
            good + "<style>x{}</style>",                                      # inline style
            good.replace('<rect/>', '<image href="https://evil.test/x.png"/>'),  # remote attr
            good.replace('>Hi<', '>lorem ipsum<'),                            # filler in text
        ]:
            g.write_text(bad)
            assert validate(r, quiet=True) == 1, f"should fail: {bad[:40]!r}"
        g.write_text(good)
        (r / "templates" / "good" / "style.css").write_text("@import url(https://x.test/a.css);")
        assert validate(r, quiet=True) == 1, "remote @import in css should fail"
        (r / "templates" / "good" / "style.css").write_text("body{color:red}")
        (r / "templates" / "orphan").mkdir()                                  # bad folder
        assert validate(r, quiet=True) == 1, "orphan folder should fail"
    print(c("  selftest: OK", "92"))
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv[1:] else validate(ROOT))
