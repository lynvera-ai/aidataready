const language = document.documentElement.lang;
const labels =
  language === "es"
    ? {
        copy: "Copiar",
        copied: "Copiado",
        failed: "No se pudo copiar. Selecciona y copia el código.",
      }
    : {
        copy: "Copy",
        copied: "Copied",
        failed: "Copy failed. Select and copy the code.",
      };

for (const button of document.querySelectorAll("[data-copy]")) {
  button.hidden = false;
  button.addEventListener("click", async () => {
    const code = document.getElementById(button.dataset.copy);
    const status = button.closest("figure").querySelector('[role="status"]');
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = labels.copied;
      status.textContent = labels.copied;
      setTimeout(() => {
        button.textContent = labels.copy;
      }, 2500);
    } catch {
      status.textContent = labels.failed;
    }
  });
}

const languageLink = document.querySelector("[data-language]");
if (languageLink) {
  languageLink.addEventListener("click", () => {
    const target = new URL(languageLink.href);
    target.hash = location.hash;
    languageLink.href = target.href;
  });
}
