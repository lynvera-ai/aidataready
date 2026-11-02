import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { copy, repository, sourceRef } from "../content.mjs";

const root = fileURLToPath(new URL("../", import.meta.url));
const dist = join(root, "dist");
const origin = "https://aidataready.lynvera.ai";
const project = await readFile(
  new URL("../../pyproject.toml", import.meta.url),
  "utf8",
);
const version = project.match(/^version = "([^"]+)"/m)?.[1];
if (!version) throw new Error("Missing project version");
const verified = JSON.parse(
  await readFile(join(root, "public/examples/verification.json"), "utf8"),
);
if (verified.version !== version || !verified.synthetic)
  throw new Error("Refresh the verified examples");
const esc = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const doc = (path) => `${repository}/blob/${sourceRef}/${path}`;
const install = `git clone ${repository}.git\ncd aidataready\ngit checkout ${sourceRef}\npython3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install .`;
const run =
  "aidataready check --config examples/rag.yaml --output rag-result.json\naidataready report --input rag-result.json --format html --output rag-report.html";
const python =
  'from lynvera_aidataready import Assessment\n\nresult = Assessment.from_config("examples/rag.yaml").run()\nprint(result.status)\nprint(result.rows_examined)';
const fail =
  "aidataready check --config examples/duplicate-ids.yaml --output duplicates.json";
const reports =
  "aidataready report --input rag-result.json --format json --output report.json\naidataready report --input rag-result.json --format html --output report.html\naidataready report --input rag-result.json --format junit --output report.xml";
const contract =
  "project:\n  name: local-knowledge\nsource:\n  type: csv\n  path: data/documents.csv\nprofile: rag";

function code(id, title, source, t, label = "") {
  return `<figure class="code-block"><figcaption><span>${esc(title)}</span><span class="code-controls">${esc(label)}<button type="button" data-copy="${id}" aria-label="${esc(t.copy + ": " + title)}" hidden>${esc(t.copy)}</button></span></figcaption><pre tabindex="0"><code id="${id}">${esc(source)}</code></pre><span class="sr-only" role="status" aria-live="polite"></span></figure>`;
}

function head(locale, { notFound = false } = {}) {
  const t = copy[locale];
  const title = notFound ? t.notFound : t.title;
  const graph = {
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    name: t.product,
    description: t.description,
    codeRepository: repository,
    programmingLanguage: "Python",
    version,
    license: doc("LICENSE"),
    author: {
      "@type": "Organization",
      name: "Lynvera Intelligence",
      url: "https://lynvera.ai",
    },
    publisher: {
      "@type": "Organization",
      name: "Lynvera Intelligence",
      url: "https://lynvera.ai",
    },
    inLanguage: locale,
    url: `${origin}/${locale}`,
  };
  return `<!doctype html><html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0d1821"><title>${esc(title)}</title><meta name="description" content="${esc(t.description)}"><meta name="robots" content="${notFound ? "noindex" : "index, follow"}"><link rel="canonical" href="${origin}/${locale}"><link rel="alternate" hreflang="en" href="${origin}/en"><link rel="alternate" hreflang="es" href="${origin}/es"><link rel="alternate" hreflang="x-default" href="${origin}/en"><link rel="icon" type="image/png" sizes="96x96" href="/assets/favicon.png"><link rel="preload" href="/assets/manrope.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script><meta property="og:type" content="website"><meta property="og:site_name" content="Lynvera AIDataReady"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(t.description)}"><meta property="og:url" content="${origin}/${locale}"><meta property="og:locale" content="${locale === "es" ? "es_MX" : "en_US"}"><meta property="og:image" content="${origin}/assets/social.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Lynvera AIDataReady. Know your data. Build reliable AI."><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${esc(title)}"><meta name="twitter:description" content="${esc(t.description)}"><meta name="twitter:image" content="${origin}/assets/social.png"><script type="application/ld+json">${JSON.stringify(graph).replace(/</g, "\\u003c")}</script></head>`;
}

function page(locale) {
  const t = copy[locale],
    other = locale === "en" ? "es" : "en";
  const documentation = [
    "docs/getting-started.md#installation",
    "docs/cli.md",
    "docs/python-api.md",
    "docs/profiles.md",
    "docs/postgresql.md",
    "docs/contracts.md",
  ];
  return `${head(locale)}<body><a class="skip" href="#content">${t.skip}</a>
<header class="site-header"><div class="shell header-inner"><a class="brand" href="https://lynvera.ai/${locale}" aria-label="Lynvera Intelligence"><img src="/assets/lynvera.svg" alt="Lynvera Intelligence" width="164" height="48"></a><a class="project-name" href="/${locale}">AIDataReady</a><nav aria-label="${locale === "en" ? "Project navigation" : "Navegación del proyecto"}"><a href="#start">${t.guide}</a><a href="${repository}">GitHub</a><a class="language" data-language lang="${other}" hreflang="${other}" href="/${other}">${t.language}</a></nav></div></header>
<main id="content"><section class="shell hero"><div class="hero-copy"><p class="eyebrow">${t.eyebrow}</p><p class="product-name">${t.product}</p><h1>${t.headline[0]}<br><span>${t.headline[1]}</span></h1><p class="lead">${t.intro}</p><div class="actions"><a class="button primary" href="#start">${t.start}</a><a class="button" href="${repository}">${t.github}</a></div><p class="release">${t.version} ${version} <span>/</span> ${t.python}</p></div>
<aside class="contract-preview" aria-label="${t.preview}"><div class="panel-top"><span>AIDataReady</span><span>rag.yaml</span></div><img class="product-banner" src="/assets/product-banner.svg" width="1200" height="248" alt="AIDataReady by Lynvera"><div class="panel-code"><p class="eyebrow">${t.preview}</p><pre><code>${esc(contract)}</code></pre></div><div class="panel-result"><span class="status pass">PASS</span><div><p>${t.fixture}</p><code>local-knowledge / 2 records</code></div></div><p class="panel-foot">${t.previewFoot}</p></aside></section>
<div class="shell principles">${t.local.map((v, i) => `<span><span class="square" aria-hidden="true"></span>${v}<span class="principle-index" aria-hidden="true">0${i + 1}</span></span>`).join("")}</div>
<section class="paper" id="profiles"><div class="shell section"><div class="section-heading"><p class="eyebrow">${t.profilesLabel}</p><h2>${t.profilesTitle}</h2><p>${t.profilesIntro}</p></div><div class="profiles">${t.profiles.map(([title, text], i) => `<article><span class="index">0${i + 1}</span><h3>${title}</h3><code>${["general", "rag", "machine-learning", "agent-tools"][i]}</code><p>${text}</p></article>`).join("")}</div><a class="text-link" href="${doc("docs/profiles.md")}">${t.profilesLink}</a></div></section>
<section class="shell section sources"><div class="section-heading"><p class="eyebrow">${t.sourcesLabel}</p><h2>${t.sourcesTitle}</h2></div><ul class="source-list">${t.sources.map(([title, text]) => `<li><h3>${title}</h3><p>${text}</p></li>`).join("")}</ul><div class="source-note"><p>${t.postgres}</p><a class="text-link" href="${doc("docs/postgresql.md")}">${t.postgresLink}</a></div></section>
<section class="band" id="workflow"><div class="shell section"><div class="section-heading"><p class="eyebrow">${t.workflowLabel}</p><h2>${t.workflowTitle}</h2></div><ol class="steps">${t.steps.map(([title, text], i) => `<li><span class="step-index">0${i + 1}</span><h3>${title}</h3><p>${text}</p></li>`).join("")}</ol></div></section>
<section class="shell section" id="start"><div class="section-heading"><p class="eyebrow">${t.installLabel}</p><h2>${t.installTitle}</h2><p>${t.installIntro.replace("{version}", version)}</p></div><div class="installation"><div>${code("install", t.installCaption, install, t, t.os)}<p class="small">${t.installNote} <a href="${doc(locale === "es" ? "docs/es/getting-started.md" : "docs/getting-started.md")}">${t.installLink}</a></p></div><div>${code("run", t.runCaption, run, t)}${code("python", t.pythonCaption, python, t, "Python")}</div></div></section>
<section class="paper" id="examples"><div class="shell section"><div class="section-heading"><p class="eyebrow">${t.examplesLabel}</p><h2>${t.examplesTitle}</h2><p>${t.examplesIntro}</p></div><div class="results">${[
    ["rag", "pass", t.passTitle, t.passText, "examples/rag.yaml", run],
    [
      "duplicates",
      "fail",
      t.failTitle,
      t.failText,
      "examples/duplicate-ids.yaml",
      fail,
    ],
  ]
    .map(
      ([id, status, title, text, path, command]) =>
        `<article class="result-card"><div class="result-heading"><span class="status ${status}">${status.toUpperCase()}</span><span>${t.exit} ${verified.examples[id].exitCode}</span></div><h3>${title}</h3><p>${text}</p><p class="result-label">${t.expected}</p><pre><code>${esc(verified.examples[id].summary)}</code></pre>${id === "duplicates" ? '<p class="finding"><code>structure.unique / id / violations: 1</code></p>' : '<p class="finding"><code>profile: rag / rows_examined: 2</code></p>'}<a class="text-link" href="${doc(path)}">${path}</a></article>`,
    )
    .join(
      "",
    )}</div>${code("failure", "CLI / FAIL", fail, t)}<p class="small">${t.failNote}</p><p class="scope-note">${t.outcomes}</p><p class="small verification-date">${t.date} <a href="/examples/verification.json">${locale === "en" ? "Verification record" : "Registro de verificación"}</a></p></div></section>
<section class="shell section" id="reports"><div class="section-heading"><p class="eyebrow">${t.reportsLabel}</p><h2>${t.reportsTitle}</h2></div><div class="reports">${t.reports.map(([title, text], i) => `<article><h3>${title}</h3><p>${text}</p><a class="text-link" href="/examples/rag-report.${["json", "html", "xml"][i]}" download>${t.download} ${title}</a></article>`).join("")}</div>${code("report-commands", t.reportCaption, reports, t)}<p class="small">${t.reportNote}</p></section>
<section class="band" id="docs"><div class="shell section docs-layout"><div><p class="eyebrow">${t.docsLabel}</p><h2>${t.docsTitle}</h2><div class="doc-links">${t.docs.map((label, i) => `<a href="${doc(i === 0 && locale === "es" ? "docs/es/getting-started.md" : documentation[i])}"><span class="index">0${i + 1}</span>${label}</a>`).join("")}</div></div><div class="faq"><h3>${t.faqTitle}</h3>${t.faq.map(([q, a]) => `<details><summary>${q}<span class="expand" aria-hidden="true"></span></summary><p>${a}</p></details>`).join("")}</div></div></section>
<section class="shell closing"><div><h2>${t.closing}</h2><p>${t.closingText}</p></div><a class="button primary" href="#start">${t.start}</a></section></main>
<div class="footer-band"><footer class="shell footer"><a href="https://lynvera.ai/${locale}">Lynvera Intelligence</a><span>© 2026</span><a href="https://www.linkedin.com/company/lynvera/">LinkedIn</a><a href="${repository}">GitHub</a><a href="https://ragparity.lynvera.ai/${locale}">RAGParity</a><a href="${doc("LICENSE")}">${t.license}</a><!--email_off--><a href="mailto:hello@lynvera.ai">hello@lynvera.ai</a><!--/email_off--><p>${t.author} <a href="https://github.com/lynvera-ai">Lynvera Intelligence</a>.</p></footer></div></body></html>`;
}

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });
await cp(join(root, "assets"), join(dist, "assets"), { recursive: true });
await cp(join(root, "public"), dist, { recursive: true });
for (const locale of ["en", "es"])
  await writeFile(join(dist, `${locale}.html`), page(locale));
await writeFile(join(dist, "index.html"), page("en"));
await writeFile(
  join(dist, "404.html"),
  `${head("en", { notFound: true })}<body><main class="shell section"><p class="eyebrow">404</p><h1>Page not found</h1><p>Página no encontrada</p><div class="actions"><a class="button primary" href="/en">English</a><a class="button" href="/es">Español</a></div></main></body></html>`,
);
await writeFile(join(dist, "_redirects"), "/ /en 301\n");
await writeFile(
  join(dist, "robots.txt"),
  `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`,
);
await writeFile(
  join(dist, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${["en", "es"].map((locale) => `<url><loc>${origin}/${locale}</loc><lastmod>2026-11-01</lastmod>${["en", "es", "x-default"].map((lang) => `<xhtml:link rel="alternate" hreflang="${lang}" href="${origin}/${lang === "es" ? "es" : "en"}"/>`).join("")}</url>`).join("")}</urlset>`,
);
const jsonHash = createHash("sha256")
  .update(
    page("en").match(
      /<script type="application\/ld\+json">(.*?)<\/script>/s,
    )[1],
  )
  .digest("base64");
const esHash = createHash("sha256")
  .update(
    page("es").match(
      /<script type="application\/ld\+json">(.*?)<\/script>/s,
    )[1],
  )
  .digest("base64");
await writeFile(
  join(dist, "_headers"),
  `/*\n  Content-Security-Policy: default-src 'none'; script-src 'self' 'sha256-${jsonHash}' 'sha256-${esHash}'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n  Strict-Transport-Security: max-age=31536000\n  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\n\n/examples/*\n  Content-Disposition: attachment\n  X-Robots-Tag: noindex\n\nhttps://:project.pages.dev/*\n  X-Robots-Tag: noindex, nofollow\n\nhttps://:version.:project.pages.dev/*\n  X-Robots-Tag: noindex, nofollow\n`,
);
console.log(
  `Built AIDataReady ${version}: English and Spanish, no runtime dependencies.`,
);
