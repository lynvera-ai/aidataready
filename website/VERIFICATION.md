# Website verification, November 1, 2026

Published: https://aidataready.lynvera.ai. English: `/en`. Spanish: `/es`.
The root redirects to English. Both languages were opened over HTTPS on the
official domain and their copy controls were checked against the actual clipboard.

## Publication

- Repository: https://github.com/lynvera-ai/aidataready
- Branch: `web/aidataready-site`
- Implementation commit: `3b18a52c7a0f4c6c14c804e2791ccfbc8779cb82`
- Pull request: https://github.com/lynvera-ai/aidataready/pull/4
- Cloudflare Pages project: `lynvera-aidataready`, existing Lynvera account.
- Deployment: `ea86f59a-32e2-44c3-a8f3-769798a35686`
- Immutable preview: https://ea86f59a.lynvera-aidataready.pages.dev
- Project preview: https://lynvera-aidataready.pages.dev
- Direct-upload ZIP: 34 files, 106,023 bytes, SHA256
  `b913a4d36c225cbb6e72cd0e6609d1dfdca2d21c50aed6b8f5bf9a209279c491`.
- Only new DNS record: `aidataready.lynvera.ai` CNAME to
  `lynvera-aidataready.pages.dev`, proxied, automatic TTL.

Initial custom-domain requests returned 522 while association propagated.
Cloudflare then served the site successfully over HTTPS. The final public
verification passed 33 checks on the official domain and 33 on the project
preview. HTML is identical after Cloudflare consumes the two email opt-out
comments. The existing zone's managed robots policy is prepended to the site's
robots file; the site's own policy and sitemap remain intact. No zone-wide
settings or other DNS records were changed.

No Functions, paid bindings, analytics, runtime credentials or new GitHub app
permissions were added. Publishing was a direct upload of the verified build.
The Website workflow provides a downloadable build artifact, not an automatic
production deployment. Future updates need the documented direct-upload step.

## Checks performed

- Website build and four artifact checks passed on Node.js, including CI Node 24.
- Ruff lint, Ruff format and mypy passed. Local Python tests: 64 passed, six
  PostgreSQL tests deselected because no local disposable database was used.
- Existing Python CI passed on Python 3.12 and 3.13 with PostgreSQL, lint,
  formatting, types, tests, coverage threshold, CLI examples and package builds:
  https://github.com/lynvera-ai/aidataready/actions/runs/41360468004.
- Website CI passed:
  https://github.com/lynvera-ai/aidataready/actions/runs/41360468001.
- Clean source installation succeeded on macOS ARM64 / Python 3.12. `pip check`
  found no broken requirements. The installed CLI and the shown Python API
  returned PASS with two RAG records.
- Built wheel and source archive exclude `website/`; Python dependencies remain
  unchanged. The website build does not install or execute the Python package.
- Real CLI examples returned RAG PASS, ML PASS, agent-tools PASS and duplicate-ID
  FAIL with one violation. JSON, HTML and JUnit conversion succeeded for all four.
  The dated synthetic verification record is in `public/examples/verification.json`.
- Responsive browser checks covered 390, 768 and 1440 CSS-pixel widths with no
  page overflow. Desktop English and mobile Spanish were visually inspected.
- All ten copy controls passed in English and Spanish, including on the official
  domain. Language changes preserved the section anchor. FAQ opened with Enter;
  the skip link received visible keyboard focus.
- Computed text contrast checked 172 text elements with no result below the
  applicable WCAG AA ratio. Reduced-motion styling was checked in the built CSS.
- No browser console errors or warnings were observed on the public site.
- Installation, CLI, Python API, profiles and PostgreSQL documentation links
  returned HTTP 200. They are pinned to the public documentation commit
  `a7c2c4b3e429617ccb4ad293209e09f2b8e519b6`.
- Existing `lynvera.ai/en`, `ragparity.lynvera.ai/en` and
  `agentrelease.lynvera.ai/en` still returned HTTP 200 after publication.

The source-only installation instruction follows the project's reviewed README
and release guide. Direct PyPI lookup was unavailable behind its browser
challenge; no registry install instruction or public-package claim was added.
No coverage percentage is advertised on the site. No customer data, live model
assessment or email sending was involved.

The pull request remains open for review. No merge to `main` was performed.

## RAGParity visual alignment, November 1, 2026

Published implementation: `bb9df7eb39f537dea122f6ec577323e1dbe1b1fa`.
Production deployment: `f2acefa5-296e-4b12-913a-32a37db399cd`.
Immutable preview: https://f2acefa5.lynvera-aidataready.pages.dev.
The 34-file upload is 106,007 bytes with SHA256
`98cdf5e1ee753b3c7899d8989a80ef051f414a76f3008187eee947a87fa5a4d3`.

Header, project navigation, Manrope type scale, button dimensions and compact
footer now follow RAGParity. Mint accents, attribution, license and the product
contact remain. The header is sticky, with mobile anchor spacing adjusted so
the installation guide stays visible below it.

The build and four existing website checks passed. Both language layouts were
checked at 390, 768 and 1440 CSS pixels in the integrated browser without page
overflow. Desktop Chrome was also inspected. All ten copy controls passed;
language navigation preserved the guide anchor. Computed contrast checks found
no failures in the 167 opaque-background text elements checked. The shared
translucent header uses RAGParity's light text on its near-black background.
No warnings or errors were observed in the public browser console.

The official domain and project preview each passed 33 deployment checks after
publication, including file integrity, headers, downloads, redirects and 404s.
Website CI and Python CI both passed for the implementation commit:
https://github.com/lynvera-ai/aidataready/actions/runs/41362768075 and
https://github.com/lynvera-ai/aidataready/actions/runs/41362768066.
This revision changed no DNS records, other sites, package code or dependencies.
