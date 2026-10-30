# The Old Web Showroom

The old web, on display — a showroom for anyone who's interested.

It's a shelf of small website templates, each one dressed in the style of a
different slice of computing history: a Windows 3.1 desktop, a dial-up BBS, a
Geocities fan page, a split-flap airport board, a Game Boy screen. They're
plain HTML and CSS. Nothing to install, nothing to build — open a file and it
just works.

## Looking around

Open `index.html`. That's the showroom: a list of everything on the shelf,
each opening in its own tab. Have a wander.

```
index.html     the showroom
edit.js         the little editor (optional)
check.py        checks the templates hold together
templates/
  _blank/       a blank one to copy
  <name>/       index.html, style.css, maybe a few more pages
```

## Making one

Copy `templates/_blank/` to `templates/your-name/` and make it yours. How it
*looks* is entirely your call — the whole point is that every template is its
own world, so don't borrow another one's look. How it's *wired* is the part
that stays the same, and it's barely anything:

- Keep the folder to an `index.html` and its own `style.css`. Extra pages are
  welcome; they just share that one stylesheet and link to each other normally.
- Put a `data-slot` on any bit of text someone might want to change — the
  heading, the tagline, each card, the footer. There's a handful of common
  names to reach for first (`site-name`, `tagline`, `hero-title`, `hero-body`,
  `card-title`, `card-body`, `nav-item`, `footer`); invent others as needed.
- Write real words, in the voice of the thing. A BBS has a sysop's welcome; a
  grimoire has incantations. Never leave "lorem ipsum" lying around.
- Keep it offline. No fonts or images fetched from the web, no libraries — just
  CSS, a little inline SVG, and the fonts already on the machine. A sprinkle of
  plain JavaScript only if the era really calls for it.
- Leave the last line of the body as it is: `<script src="../../edit.js" defer></script>`.
- Add your template's name to the list near the bottom of `index.html` so it
  shows up in the showroom.

## Changing the words

Three ways, pick whichever suits:

- Just open the HTML and type.
- Add `?edit` to a page's address (e.g. `templates/meridian/index.html?edit`),
  click the text, and hit **Save HTML** to download the edited page.
- Or let a back-end fill it. Every `data-slot` is a hook; in PHP that's:
  ```php
  $doc = new DOMDocument(); $doc->loadHTMLFile('templates/meridian/index.html');
  $xp = new DOMXPath($doc);
  foreach ($content as $slot => $text)
    foreach ($xp->query("//*[@data-slot='$slot']") as $n) $n->textContent = $text;
  echo $doc->saveHTML();
  ```

## Using one for real

Copy a template's folder to your web host — it's a finished site, links and all.
If you like, drop the one `edit.js` line on the way out:

```sh
cp -r templates/meridian ~/mysite
sed -i '/edit\.js/d' ~/mysite/*.html
```

Or just put the whole repo on GitHub Pages and share the showroom.

## Keeping it honest

`./check.py` reads every template and makes sure it still follows the handful of
rules above. It needs nothing but Python 3. A git hook runs it before each
commit so nothing broken slips in — turn it on once after cloning:

```sh
git config core.hooksPath hooks
```

(`git commit --no-verify` skips it if you must.)
