(function () {
  const style = document.createElement("style");
  style.textContent = `
    .msp-login-card {
      width: min(100%, 520px) !important;
      max-width: 520px !important;
    }

    .msp-login-header {
      width: 100%;
      display: flex !important;
      flex-direction: column !important;
      align-items: stretch !important;
      justify-content: flex-start !important;
      gap: 14px;
    }

    .msp-login-logos {
      width: 100% !important;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-width: 0;
    }

    .msp-login-title {
      width: 100%;
      margin: 0;
      text-align: center;
      font-size: 16px !important;
      line-height: 1.35 !important;
    }

    .msp-login-subtitle {
      width: 100%;
      margin: 0;
      text-align: center;
      font-size: 24px;
      line-height: 1.2;
      font-weight: 600;
    }

    .msp-login-brand {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      flex: 1 1 auto;
      min-width: 0;
      padding: 0;
      background: transparent;
    }

    .msp-login-brand img {
      display: block;
      width: 420px;
      max-width: 100%;
      height: auto;
      object-fit: contain;
    }

    @media (max-width: 1800px) {
      .msp-login-card {
        width: min(100%, 420px) !important;
        max-width: 420px !important;
      }

      .msp-login-header {
        gap: 12px;
      }

      .msp-login-brand {
        justify-content: flex-end;
      }

      .msp-login-brand img {
        width: 180px;
      }
    }
  `;
  document.head.appendChild(style);

  function customizeLogin() {
    const heading = Array.from(document.querySelectorAll("h2")).find(
      (node) => node.textContent && node.textContent.trim() === "Sign into Airflow",
    );
    if (!heading) return false;

    const card = heading.closest(".chakra-container");
    const header = heading.parentElement;
    if (!card || !header || card.dataset.mspCustomized === "true") return true;

    const notice = Array.from(document.querySelectorAll(".chakra-alert__root")).find((node) =>
      node.textContent?.includes("Simple auth manager enabled"),
    );
    if (notice) {
      notice.style.display = "none";
    }

    card.dataset.mspCustomized = "true";
    card.classList.add("msp-login-card");
    header.classList.add("msp-login-header");
    heading.classList.add("msp-login-title");

    const subtitle = document.createElement("p");
    subtitle.className = "msp-login-subtitle";
    subtitle.innerHTML =
      "Dirección Nacional de Estadística y<br>Análisis de la Información del<br>Sistema Nacional de Salud";

    const logosRow = document.createElement("div");
    logosRow.className = "msp-login-logos";
    const airflowLogo = header.querySelector("svg");
    if (airflowLogo) {
      logosRow.appendChild(airflowLogo);
    }

    const logoWrap = document.createElement("div");
    logoWrap.className = "msp-login-brand";

    const logo = document.createElement("img");
    logo.src = "./auth/static/LOGO_MSP.png";
    logo.alt = "Ministerio de Salud Publica";
    logoWrap.appendChild(logo);
    logosRow.appendChild(logoWrap);
    header.prepend(logosRow);
    header.appendChild(subtitle);
    header.appendChild(heading);

    return true;
  }

  if (!customizeLogin()) {
    const observer = new MutationObserver(() => {
      if (customizeLogin()) observer.disconnect();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }
})();
