(function () {
  const desiredTitle = "DNEAISNS";
  const desiredWelcome = "Bienvenido al orquestador de flujos de datos de la DNEAISNS";

  function enforceTitle() {
    if (document.title !== desiredTitle) {
      document.title = desiredTitle;
    }
  }

  enforceTitle();

  const titleElement = document.querySelector("title");
  if (titleElement) {
    new MutationObserver(enforceTitle).observe(titleElement, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  }

  window.addEventListener("load", enforceTitle);
  window.addEventListener("popstate", enforceTitle);

  function enforceWelcomeText() {
    for (const heading of document.querySelectorAll("h2")) {
      if (heading.textContent && heading.textContent.trim() === "Te damos la bienvenida") {
        heading.textContent = desiredWelcome;
      }
    }
  }

  enforceWelcomeText();

  new MutationObserver(() => {
    enforceTitle();
    enforceWelcomeText();
  }).observe(document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true,
  });
})();
