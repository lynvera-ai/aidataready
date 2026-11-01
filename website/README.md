# Lynvera AIDataReady website

Official bilingual product site for https://aidataready.lynvera.ai. English is
the default at `/en`; `/es` contains the complete Spanish version. The root
redirects to `/en`. The site is separate from the Python distribution and uses
the static Cloudflare Pages conventions of the other Lynvera product sites.

## Build and preview

Use Node.js 24. No npm installation, Python environment, credentials, framework
or external services are needed for the website build.

```bash
npm --prefix website run release
npm --prefix website run dev
```

Preview: http://127.0.0.1:4176/en. `PORT` changes the local port. Output is
`website/dist`, which is ignored by Git. The build reads the product version
from `pyproject.toml` and validates the stored synthetic example version.
`npm --prefix website run check` checks syntax, content, links, metadata,
artifact sizes, security headers and actual saved example results.

For public HTTPS verification after building, run:

```bash
node website/scripts/smoke.mjs https://aidataready.lynvera.ai
```

This checks deployed files against the local artifact, redirects, 404s, headers
and report attachments. It tolerates only Cloudflare's consumed email opt-out
comments and its existing managed robots prefix, while requiring the original
robots policy and sitemap to remain intact. See [VERIFICATION.md](VERIFICATION.md)
for the publication record.

The separate Website workflow builds and checks only the site and uploads a
seven-day build artifact. It does not deploy, install Python dependencies or
send email. Existing Python CI is preserved. No automatic package publication
is introduced.

## Content and verified examples

`content.mjs` keeps equivalent English and Spanish content. Documentation,
installation and synthetic fixtures are pinned to the reviewed public
documentation commit in `sourceRef`; that documentation is not yet on `main`.
Do not replace those links with `main` until their destinations exist there.
The website branch includes that documentation commit as its base.

Only source installation is advertised. The reviewed project README and release
guide state that version 0.1.0 has not been published to PyPI. No PyPI install
command, model-performance certification or unverified coverage figure is used.
Sensitive-data checks are heuristic and decoded batch budgets are not hard
process memory caps.

With the product development environment active, refresh synthetic artifacts:

```bash
python website/scripts/verify_examples.py
npm --prefix website run release
```

This invokes the real CLI, checks expected exit codes and record counts, and
creates local JSON, HTML and JUnit reports from the repository fixtures. It
also checks command help and profiling. It does not connect to PostgreSQL,
send data or use a model. Review artifacts before committing. Results are
dated in `public/examples/verification.json`. The RAG freshness result is
time-dependent because the fixture has fixed dates and a 3,650-day window.

The report downloads use attachment disposition so that the original offline
HTML report, including its filters, can be opened locally. Website CSP allows
only local assets and the hashes of its non-executable structured metadata.
Copy buttons are progressively enhanced; all content and code remain available
without JavaScript. Clipboard denial displays an accessible manual-copy message.

## Cloudflare Pages Free

Create an independent Pages project named `lynvera-aidataready` in the existing
Lynvera Cloudflare account. Use the Pages workflow, not a Worker. No paid plan,
bindings, Functions, telemetry, Cloudflare API token or runtime secret is needed.
Keep existing projects and DNS records unchanged.

For direct upload, build and upload the contents of `website/dist` (or a ZIP
whose root contains `en.html`, `_headers` and `_redirects`). Add the custom domain
`aidataready.lynvera.ai` from that project's Custom domains screen. It should
create only that subdomain's CNAME to `lynvera-aidataready.pages.dev`. Verify
the deployment, domain activation and HTTPS before announcing publication.

For a separately authorized Git integration, restrict the official Cloudflare
app to this repository. Framework: None. Root: repository root. Build:
`npm --prefix website run release`. Output: `website/dist`. Node: 24. Production
branch: `web/aidataready-site` until the reviewed PR is merged. Git integration
is optional; do not grant repository access merely to perform direct upload.
A direct-upload project cannot later be converted into a Git-integrated one;
create a replacement project and reassign only this custom domain if needed.

Pages Free has usage limits, including 500 builds per month, 20,000 files per
site and 25 MiB per file. This artifact stays well below them. Domain registration
and mail retain their existing conditions. There is no website backend or
per-email charge; contact is a mailto link to felipe.castillo@lynvera.ai.

`_headers` restricts scripts, styles, fonts, images and framing. Preview
`pages.dev` hosts are marked noindex; canonical and sitemap URLs use only the
production domain. Do not enable automatic email-address obfuscation or script
injection on this subdomain: it conflicts with local-only CSP and is unnecessary
for the public project contact. Do not change a shared zone-wide setting.

After deployment check `/`, `/en`, `/es`, a missing route, both language links,
all copy controls, FAQ keyboard interaction, synthetic downloads, metadata,
`robots.txt` and `sitemap.xml`. Test mobile, tablet and desktop. Verify the
existing Lynvera and RagParity domains still respond.

## Local assets and attribution

The product banner comes from `docs/assets/readme-banner.svg`. The local Lynvera
logo and favicon follow the existing Lynvera brand assets. Manrope is bundled
locally under its included SIL Open Font License in `assets/manrope-license.txt`.
The social card is a local SVG with a pre-rendered PNG for social crawlers; its
PNG is committed so site builds require no graphics dependency.

Author and maintainer: Dr. Felipe Castillo Rendón, `fcastillorendon`.
Organization: Lynvera Open Source. Project license: Apache License 2.0.
Contact: felipe.castillo@lynvera.ai.

References:

- https://developers.cloudflare.com/pages/get-started/direct-upload/
- https://developers.cloudflare.com/pages/configuration/custom-domains/
- https://developers.cloudflare.com/pages/configuration/headers/
- https://developers.cloudflare.com/pages/platform/limits/
