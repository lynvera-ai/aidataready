import assert from "node:assert/strict";
import { readFile, readdir, stat } from "node:fs/promises";
import { createHash } from "node:crypto";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const origin = new URL(process.argv[2] || "http://127.0.0.1:4176");
assert.ok(["https:", "http:"].includes(origin.protocol));
const root = fileURLToPath(new URL("../dist/", import.meta.url));
const paths = async (folder) =>
  (
    await Promise.all(
      (await readdir(folder)).map(async (name) => {
        const path = join(folder, name);
        return (await stat(path)).isDirectory() ? paths(path) : path;
      }),
    )
  ).flat();
const hash = (data) => createHash("sha256").update(data).digest("hex");
// Cloudflare consumes these two opt-out markers while preserving the public address.
const normalized = (data, html) =>
  html
    ? Buffer.from(data.toString().replace(/<!--\/?email_off-->/g, ""))
    : data;
let checks = 0;
for (const path of await paths(root)) {
  const relative = path.slice(root.length);
  if (relative.startsWith("_") || ["404.html", "index.html"].includes(relative))
    continue;
  const route = ["en.html", "es.html"].includes(relative)
    ? relative.slice(0, -5)
    : relative;
  const response = await fetch(new URL(route, origin), {
    signal: AbortSignal.timeout(20000),
  });
  assert.equal(response.status, 200, route);
  let actual = Buffer.from(await response.arrayBuffer());
  const expected = await readFile(path);
  if (route === "robots.txt" && !actual.equals(expected)) {
    const text = actual.toString();
    assert.ok(text.includes("# BEGIN Cloudflare Managed content"));
    assert.ok(text.includes("# END Cloudflare Managed Content"));
    assert.ok(
      text.endsWith(expected.toString()),
      "Original robots policy must be preserved",
    );
    actual = Buffer.from(text.slice(-expected.toString().length));
  }
  assert.equal(
    hash(normalized(actual, route === "en" || route === "es")),
    hash(normalized(expected, route === "en" || route === "es")),
    `${route}: deployed content differs`,
  );
  assert.equal(
    response.headers.get("x-content-type-options"),
    "nosniff",
    route,
  );
  assert.ok(
    response.headers
      .get("content-security-policy")
      ?.includes("connect-src 'none'"),
    route,
  );
  if (route.startsWith("examples/"))
    assert.match(response.headers.get("content-disposition"), /attachment/);
  if (origin.hostname.endsWith(".pages.dev"))
    assert.match(response.headers.get("x-robots-tag"), /noindex/);
  else if (route === "en" || route === "es")
    assert.ok(!response.headers.get("x-robots-tag")?.includes("noindex"));
  checks++;
}
const rootResponse = await fetch(origin, { redirect: "manual" });
assert.equal(rootResponse.status, 301);
assert.equal(
  new URL(rootResponse.headers.get("location"), origin).pathname,
  "/en",
);
checks++;
for (const route of ["not-a-page", "api/leads"]) {
  const response = await fetch(new URL(route, origin));
  assert.equal(response.status, 404);
  assert.match(await response.text(), /Page not found/);
  checks++;
}
console.log(
  `${origin.origin}: ${checks} HTTPS/content/security/download checks passed.`,
);
