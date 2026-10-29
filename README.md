# Retro Template Vault

A repository of standalone old-school website templates. Each template is its
own folder — its own layout, theme, pages, and personality, built as a piece of
art in its period. No build, no framework, no dependencies. The repo shares
exactly two things across every template: the **editing workflow** and the
**project index** (`index.html`). Nothing else links them.

## Layout

```
index.html              the showroom: gallery + build checklist
edit.js                 the shared opt-in content editor
README.md               this file — the rulebook
templates/
  _blank/               copy this folder to start a new template
    index.html  about.html  style.css
  meridian/
    index.html  style.css
  <slug>/ …
```

The `T` array at the bottom of `index.html` is the single source of truth for
what exists. Open `index.html` to browse; each built template opens in a new tab.

## Rules for a template

Everything not listed here — layout, colour, type, pages, tabs, period-correct
effects — is the template's own art. No house style, no shared CSS.

1. Lives at `templates/<slug>/`; entry point `index.html`; styling in its own
   external `style.css`.
2. Every fillable piece of text carries `data-slot="…"` — that's how `edit.js`
   and any back-end find content. Common names, reused so one back-end fills any
   template: `site-name`, `tagline`, `hero-title`, `hero-body`, `page-title`,
   `page-body`, `footer`, `nav-item`, `card-title`, `card-body`. Use the subset
   the design needs.
3. **Fill every slot with in-world copy invented for the theme — never lorem
   ipsum.** A BBS has sysop banners, a grimoire has incantations. The text is
   part of the design.
4. Keep the `edit.js` line at the end of `<body>`. It is the repo's authoring
   aid; once exported it 404s harmlessly.
5. Register the slug in the `T` array in `/index.html`.

## Multipage

Add `about.html`, `work.html`, … in the folder. Pages share the one `style.css`
and link each other with plain relative hrefs (`href="about.html"`). The
header/nav markup is repeated per page — fine at template scale, and the clean
markup means a back-end can later lift it into a single partial. No includes, no
JS: the way sites were built before bundlers, and it works the same on `file://`,
on a server, and after export.

> Perfect "edit the nav once" with no back-end on `file://` doesn't exist — every
> include (SSI, PHP, `fetch`, a build step) breaks either `file://` or the
> no-tooling rule. So styling is deduped (`style.css`); chrome markup repeats
> until a back-end owns it.

## Editing

- **By hand** — slots are plain elements. Edit the text, save.
- **In the browser** — open any page with `?edit`
  (`templates/meridian/index.html?edit`). Slots become editable; **Save HTML**
  downloads the page to replace the file. Text only; edit each page in turn.
- **With a back-end** — slots are injection points; loop `[data-slot]` and set
  text. The `.html` file *is* the template:

  ```php
  $doc = new DOMDocument(); $doc->loadHTMLFile('templates/meridian/index.html');
  $xp = new DOMXPath($doc);
  foreach ($content as $slot => $text)
    foreach ($xp->query("//*[@data-slot='$slot']") as $n) $n->textContent = $text;
  echo $doc->saveHTML();
  ```

## Deploy & export

The repo is the immutable source and showroom; you never serve it directly. To
use a template, copy its folder to your web root — it's a complete site (relative
links, own CSS). Optionally drop the one `edit.js` line (it 404s otherwise, which
is invisible to visitors):

```sh
cp -r templates/meridian ~/mysite
sed -i '/edit\.js/d' ~/mysite/*.html   # optional tidy
```

## New template

Copy `templates/_blank/` to `templates/<slug>/`, rewrite `style.css` and the
markup, follow the five rules, add the slug to `T` in `index.html`.

## Checking templates

`./check.sh` verifies every template against the structural rules (external
`style.css`, no inline `<style>`, `data-slot` present, the `edit.js` hook,
no `lorem ipsum`, no remote/CDN assets, and showroom registration). POSIX sh,
no dependencies. Styling is each template's own business — the script enforces
structure, never taste. Exits non-zero on any failure, so it drops straight
into CI or a pre-commit hook.
