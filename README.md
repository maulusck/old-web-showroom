# The Old Web Showroom

*The old web, on display — a showroom for those who may be interested.*

A collection of standalone old-school website templates. Each one is its own
folder — its own era, layout, theme and personality, hand-built as a period
piece. No build, no framework, no dependencies; every template runs offline by
double-clicking its file. The repo shares exactly two things across all of
them: the **editing workflow** and the **showroom index**. Nothing else links
them, and no two look alike.

## Browse

Open `index.html` — the showroom floor. It lists every template; each opens in
a new tab. That's the whole front door.

```
index.html     the showroom (gallery + the T array that lists every template)
edit.js        shared opt-in content editor
check.py       the validator (also a pre-commit gate)
README.md      this file
templates/
  _blank/      copy this to start a new one
  <slug>/      index.html · style.css · (extra pages optional)
```

---

## The contract — building a template

This section is the single source of truth. A template obeys these rules and
nothing more; **everything else — layout, colour, type, motion, page count — is
the template's own art.** No house style, no shared CSS, no copying another
template's look.

1. **Place** — lives at `templates/<slug>/`, entry `index.html`, styling in its
   own external `style.css` (never an inline `<style>` block).
2. **Slots** — every fillable piece of text carries `data-slot="…"` so the
   editor and any back-end can find it. Reuse these common names where they fit
   (use only the subset the design needs): `site-name`, `tagline`,
   `hero-title`, `hero-body`, `page-title`, `page-body`, `footer`, `nav-item`,
   `card-title`, `card-body`. Extra names are fine for anything else.
3. **In-world copy** — fill every slot with text invented for the theme. Never
   lorem ipsum. A BBS has sysop banners, a grimoire has incantations; the words
   are part of the art.
4. **Offline only** — no network. No CDN, no remote fonts, no external images.
   CSS + inline SVG + system fonts, so it works on `file://`. JS only if the era
   truly needs it, and then a few vanilla lines.
5. **Unique** — no two templates share the same era *and* form. A new idea that
   echoes an existing one must differ clearly in palette, content and layout, or
   it isn't built.
6. **Editor hook** — the last line of every page's `<body>` is exactly:
   `<script src="../../edit.js" defer></script>`
7. **Register** — add the slug to the `T` array in `/index.html` (same commit).

**Multipage** is encouraged where the concept wants it (a forum → thread, a
splash → home). Add more `.html` files in the folder; they share the one
`style.css` and link each other with plain relative hrefs. Repeat the header/nav
markup per page — that's how sites worked before bundlers, and every page still
obeys rules 1–6.

**Start from `templates/_blank/`** — copy the folder, rename it, rewrite the
markup and `style.css`, keep the contract.

## Editing

- **By hand** — slots are plain elements; edit the text, save.
- **In the browser** — open any page with `?edit` (e.g.
  `templates/meridian/index.html?edit`). Slots become editable; **Save HTML**
  downloads the page to replace the file. Text only; edit each page in turn.
- **With a back-end** — the `.html` *is* the template; fill the slots:
  ```php
  $doc = new DOMDocument(); $doc->loadHTMLFile('templates/meridian/index.html');
  $xp = new DOMXPath($doc);
  foreach ($content as $slot => $text)
    foreach ($xp->query("//*[@data-slot='$slot']") as $n) $n->textContent = $text;
  echo $doc->saveHTML();
  ```

## Deploy & export

The repo is the source and showroom; you don't serve it directly. To use a
template, copy its folder to your web root — it's a complete site (relative
links, own CSS). Optionally strip the one `edit.js` line (it 404s harmlessly
otherwise):

```sh
cp -r templates/meridian ~/mysite
sed -i '/edit\.js/d' ~/mysite/*.html   # optional tidy
```

Or push the whole repo to GitHub Pages / any static host as-is.

## Validate — and the gate

`./check.py` checks every template against the contract (external `style.css`,
no inline `<style>`, a `data-slot`, the `edit.js` hook, in-world copy, offline
only, two-way registration). Python 3 stdlib only; it parses the HTML, so a URL
or "lorem ipsum" inside a comment never trips it. `--selftest` validates the
checker itself; `--plain` drops colour/banner (auto-off when piped). Non-zero
exit on any failure.

A tracked **pre-commit hook** (`hooks/pre-commit`) runs it on every commit and
blocks failures. It ships with the repo; enable it once after cloning:

```sh
git config core.hooksPath hooks
```

Override a single commit with `git commit --no-verify`.

## Backlog note

Single-page templates that would suit a later multipage pass (not urgent):
geocities, newspaper, bbs, winamp, myspace, dos-commander.
