# rcybers.github.io

Portfolio of Stephanio RAZARISON. Static site, English at `/` and French at `/fr/`.

## Edit and rebuild

- Text: `src/content.py`
- Settings (domain, email, analytics, contact form): `src/config.py`
- Styles: `src/css/main.css` · Scripts: `src/js/`
- Build: `python3 src/build.py` (needs Python 3 and `esbuild` on the PATH, or `ESBUILD=/path/to/esbuild`)

The build writes the HTML pages, `sitemap.xml`, `robots.txt`, `site.webmanifest`, `_headers` and the minified CSS/JS to the repository root.

## Hosting

- GitHub Pages: works as is. The Content-Security-Policy and Referrer-Policy are set with `<meta>` tags.
- Cloudflare Pages or Netlify: `_headers` adds HSTS, CSP with `frame-ancestors`, X-Content-Type-Options, X-Frame-Options, Referrer-Policy and Permissions-Policy.
- Custom domain: set `SITE_URL` in `src/config.py`, rebuild, and add a `CNAME` file.
