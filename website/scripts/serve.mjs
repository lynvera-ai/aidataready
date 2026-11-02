import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { extname, resolve, sep } from "node:path";

const root = resolve(fileURLToPath(new URL("../dist/", import.meta.url)));
const port = Number(process.env.PORT || 4176);
const headerText = await readFile(resolve(root, "_headers"), "utf8");
const security = Object.fromEntries(
  headerText
    .split("\n\n")[0]
    .split("\n")
    .slice(1)
    .map((line) => {
      const index = line.indexOf(":");
      return [line.slice(0, index).trim(), line.slice(index + 1).trim()];
    }),
);
const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8",
  ".xml": "application/xml",
  ".json": "application/json",
};
createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(
      new URL(req.url, "http://localhost").pathname,
    );
    if (pathname === "/") {
      res.writeHead(302, { Location: "/en", ...security }).end();
      return;
    }
    if (/\.(?:html)$/.test(pathname) && !pathname.endsWith("/404.html")) {
      res.writeHead(308, { Location: pathname.slice(0, -5) }).end();
      return;
    }
    if (pathname.endsWith("/")) {
      res.writeHead(308, { Location: pathname.slice(0, -1) }).end();
      return;
    }
    let path = resolve(root, "." + pathname);
    if (
      !path.startsWith(root + sep) ||
      pathname.split("/").pop().startsWith("_")
    )
      throw new Error("Not found");
    if (!extname(path)) path += ".html";
    await stat(path);
    res.writeHead(200, {
      "Content-Type": mime[extname(path)] || "application/octet-stream",
      ...security,
      ...(pathname.startsWith("/examples/")
        ? { "Content-Disposition": "attachment" }
        : {}),
    });
    res.end(await readFile(path));
  } catch {
    res.writeHead(404, {
      "Content-Type": "text/html; charset=utf-8",
      ...security,
    });
    res.end(await readFile(resolve(root, "404.html")));
  }
}).listen(port, "127.0.0.1", () =>
  console.log(`AIDataReady preview: http://127.0.0.1:${port}`),
);
