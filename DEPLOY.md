# Deploying to GitHub Pages

The site is a plain static build (`python3 build.py` writes the `.html` +
`styles.css`; everything else is committed as-is). GitHub Pages just serves the
repo, so hosting is: push the repo, flip Pages on.

## Current state: UNLISTED

The site is configured to be **reachable by direct link but not searchable**:

- `template.html` emits `<meta name="robots" content="noindex, nofollow">` on
  every page.
- `robots.txt` disallows all crawlers.

So you can share the URL with friends now; Google/Bing won't index it. Note:
free GitHub Pages has **no password protection** — anyone with the link can
view. (For a true login wall you'd need a paid host like Netlify/Cloudflare
Access.)

## One-time setup

Pick where it lives (see the three options discussed):

- **Project site** — `https://<you>.github.io/<repo>` — any repo name.
- **User site** — `https://<you>.github.io` — repo MUST be named `<you>.github.io`.
- **Org site** — `https://dotsandlines.github.io` — create a free org
  `dotsandlines`, repo MUST be named `dotsandlines.github.io`.

Then (using the org/vanity example — swap the name for your choice):

```sh
# from the repo root, with the GitHub CLI authenticated (gh auth login)
gh repo create dotsandlines/dotsandlines.github.io --public --source=. --push
```

or by hand: create the empty repo on github.com, then

```sh
git remote add origin git@github.com:dotsandlines/dotsandlines.github.io.git
git push -u origin main
```

Enable Pages: repo **Settings → Pages → Build and deployment → Source:
"Deploy from a branch" → Branch: `main` / folder: `/ (root)` → Save**.
The site appears at the URL above within a minute or two.

> The repo must be **public** for Pages on a free account (a public repo is
> fine — it's a static site). Publishing from a *private* repo needs GitHub Pro.

## Going public (when you're ready to be searchable)

1. Delete the `<meta name="robots" ...>` line in `template.html`.
2. In `robots.txt`, replace `Disallow: /` with an empty `Disallow:`.
3. `python3 build.py` to rebuild the pages.
4. Commit and push.
5. (Optional) Submit the URL to Google Search Console to be indexed sooner.

## Everyday updates

```sh
python3 build.py     # regenerate html/css from style.md, content.md, pages/*
git add -A && git commit -m "..." && git push
```

Pages redeploys automatically on push.
