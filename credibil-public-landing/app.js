(() => {
  "use strict";

  const translations = {
    ro: {
      metaTitle: "Credibil - Verificarea companiilor și a persoanelor asociate",
      metaDescription: "Verificați o companie sau o persoană asociată din Republica Moldova, consultați datele disponibile, conexiunile, rapoartele și monitorizarea schimbărilor.",
      skip: "Sari la conținut",
      navCapabilities: "Posibilități", navProduct: "Produs", navMonitoring: "Monitorizare", navMoldac: "MOLDAC", navHow: "Cum funcționează",
      login: "Autentificare", startCheck: "Începe verificarea",
      heroEyebrow: "Verificarea partenerilor de afaceri în Moldova",
      heroTitle: "Verificați contrapartida <span>înainte de decizia de afaceri</span>",
      heroLead: "Căutați o companie sau o persoană asociată, consultați datele de înregistrare, fondatorii, conexiunile și informațiile disponibile care necesită atenție.",
      searchLabel: "Denumire, IDNO sau nume și prenume", searchPlaceholder: "Introduceți denumirea, IDNO sau numele", find: "Găsește",
      searchNote: "Cererea este păstrată la trecerea prin autentificare și deschisă ulterior în căutarea Credibil.",
      searchRequired: "Introduceți cel puțin două caractere.", searchRedirect: "Cererea a fost păstrată. Este necesară autentificarea pentru a continua.",
      proofOne: "Căutare după denumire, IDNO și nume", proofTwo: "Raport PDF și Excel", proofThree: "Monitorizarea schimbărilor",
      monitorCardLabel: "Monitorizare", monitorCardTitle: "Urmăriți schimbările companiei", reportCardLabel: "Rezultat", reportCardTitle: "Export PDF și Excel",
      localEyebrow: "Specializare locală", localTitle: "Date pentru verificarea companiilor din Republica Moldova",
      localLead: "Credibil reunește într-un singur scenariu informațiile disponibile despre companie, persoanele asociate, rolurile și relațiile corporative. Serviciul nu este un portal de stat și nu înlocuiește consultanța juridică.", seeProduct: "Vedeți produsul",
      capEyebrow: "Patru acțiuni esențiale", capTitle: "De la căutare la monitorizare, într-un singur flux",
      featureSearchTitle: "Căutare unificată", featureSearchText: "Găsiți companii și persoane după denumire, IDNO sau nume, cu separarea rezultatelor pe tipuri.",
      featureDataTitle: "Date și conexiuni", featureDataText: "Consultați fondatorii, administratorii, cotele de participare și companiile asociate prin persoane și organizații.",
      featureReportTitle: "Raport structurat", featureReportText: "Păstrați rezultatul verificării prin exportul raportului disponibil în format PDF sau Excel.",
      featureMonitorTitle: "Monitorizarea companiei", featureMonitorText: "Adăugați compania în lista urmărită și consultați notificările disponibile despre modificări.",
      directionsEyebrow: "Direcțiile produsului", directionsTitle: "Ce puteți verifica în Credibil",
      dirCompanies: "Companii", dirCompaniesText: "Date de înregistrare și clasificare, statut, adresă, CAEM și informații fiscale disponibile.",
      dirPeople: "Persoane și conexiuni", dirPeopleText: "Fondatori, administratori, roluri, cote de participare și organizații asociate.",
      dirReports: "Rapoarte", dirReportsText: "Secțiuni tematice și exportul rezultatului verificării în PDF și Excel.",
      dirAttention: "Factori de atenție", dirAttentionText: "Verificarea existenței datelor despre datorii, litigii, executări, sancțiuni și alte secțiuni disponibile.",
      productEyebrow: "Produs funcțional", productTitle: "Interfața reală, nu o promisiune abstractă", productLead: "Cadrele de mai jos provin din produsul Credibil și demonstrează căutarea, cardul companiei și relațiile corporative.",
      gallerySearchTitle: "Căutare după denumire, IDNO sau nume", gallerySearchText: "Rezultatele sunt separate vizual între companii și persoane.",
      galleryCompanyTitle: "Cardul companiei", galleryCompanyText: "Datele de bază, persoanele responsabile și acțiunile principale sunt disponibile într-un singur ecran.",
      galleryRelationsTitle: "Relații corporative", galleryRelationsText: "Comparați rolurile și cotele în prezentarea Listă sau treceți la Schema disponibilă în produs.",
      connectionsEyebrow: "Cardul companiei și relațiile", connectionsTitle: "Înțelegeți cine conduce, deține și conectează compania",
      connectionsLead: "Credibil arată IDNO, statutul, fondatorii, administratorul, cotele de participare și organizațiile asociate. Relațiile pot fi analizate în modurile Listă și Schemă.",
      connectionItemOne: "Fondatori și cote de participare", connectionItemTwo: "Administratori și roluri în alte companii", connectionItemThree: "Companii active și lichidate în același context",
      checkCompany: "Verificați compania", listView: "Listă", schemeView: "Schemă",
      riskEyebrow: "Date disponibile și rapoarte", riskTitle: "Verificați existența informațiilor care pot necesita atenție",
      riskLead: "Prezența datelor diferă de la o companie la alta. Interfața trebuie să distingă între lipsa datelor, lipsa rezultatelor și o secțiune care încă nu a fost completată.",
      riskFinance: "Rapoarte financiare", riskSection: "Secțiune separată", riskCourt: "Dosare judiciare", riskAvailability: "Verificarea datelor disponibile", riskExecutions: "Proceduri de executare", riskActiveArchive: "Active și arhivate", riskProcurement: "Achiziții publice", riskAccreditations: "Acreditări", riskCompanySection: "Secțiune în cardul companiei", riskSanctions: "Sancțiuni", riskMatchCheck: "Verificarea coincidențelor disponibile",
      reportKicker: "Acțiuni confirmate în cardul companiei", reportTitle: "Exportați rezultatul în PDF sau Excel",
      example: "Exemplu", eventTitle: "Administratorul companiei s-a modificat", eventText: "Notificarea demonstrativă arată tipul schimbării și trimite utilizatorul la compania monitorizată. Nu reprezintă un eveniment real.",
      monitoringEyebrow: "Monitorizarea schimbărilor", monitoringTitle: "Nu repetați manual aceeași verificare", monitoringLead: "Adăugați compania în monitorizare, reveniți la lista urmărită și consultați notificările disponibile atunci când în sistem apar modificări.",
      monitorStepOneTitle: "Adăugați compania", monitorStepOneText: "Acțiunea este disponibilă direct în cardul companiei.", monitorStepTwoTitle: "Consultați lista urmărită", monitorStepTwoText: "Companiile monitorizate sunt grupate într-un singur compartiment.", monitorStepThreeTitle: "Gestionați monitorizarea", monitorStepThreeText: "Puteți deschide compania sau o puteți elimina din listă.",
      moldacEyebrow: "Acreditări MOLDAC", moldacTitle: "Compartiment separat pentru căutarea acreditărilor", moldacLead: "Produsul include filtrarea acreditărilor MOLDAC și o secțiune asociată în cardul companiei. Disponibilitatea și plenitudinea datelor trebuie confirmate înainte de publicare.", checkAccreditation: "Verificați acreditarea",
      howEyebrow: "Un scenariu clar", howTitle: "Cum funcționează verificarea", howOneTitle: "Găsiți", howOneText: "Introduceți denumirea companiei, IDNO sau numele persoanei asociate.", howTwoTitle: "Verificați", howTwoText: "Consultați datele de bază, rolurile, relațiile și secțiunile disponibile.", howThreeTitle: "Păstrați rezultatul", howThreeText: "Exportați raportul sau adăugați compania în monitorizare.",
      finalEyebrow: "Începeți cu un nume sau IDNO", finalTitle: "Verificați contrapartida înainte de următoarea decizie", finalText: "Cererea introdusă va fi păstrată și deschisă în căutarea Credibil după autentificare.",
      footerText: "Instrument pentru consultarea datelor disponibile despre companii și persoane asociate din Republica Moldova.", footerProduct: "Produs", footerAccount: "Cont", footerLegal: "Informații juridice", privacy: "Politica de confidențialitate", terms: "Condiții de utilizare", footerLegalNote: "Denumirea juridică și contactele proprietarului produsului se adaugă după confirmare."
    },
    en: {
      metaTitle: "Credibil - Company and related-person checks in Moldova",
      metaDescription: "Check a company or related person in Moldova and review available registration data, connections, reports, and change monitoring.",
      skip: "Skip to content",
      navCapabilities: "Capabilities", navProduct: "Product", navMonitoring: "Monitoring", navMoldac: "MOLDAC", navHow: "How it works",
      login: "Log in", startCheck: "Start a check",
      heroEyebrow: "Business counterparty checks in Moldova", heroTitle: "Check a counterparty <span>before a business decision</span>",
      heroLead: "Search for a company or related person and review registration details, founders, corporate connections, and available information that may require attention.",
      searchLabel: "Company name, IDNO, or full name", searchPlaceholder: "Enter a company name, IDNO, or full name", find: "Search",
      searchNote: "The query is retained through authentication and opened in Credibil search afterwards.", searchRequired: "Enter at least two characters.", searchRedirect: "Your query has been saved. Authentication is required to continue.",
      proofOne: "Search by name, IDNO, and full name", proofTwo: "PDF and Excel reports", proofThree: "Change monitoring",
      monitorCardLabel: "Monitoring", monitorCardTitle: "Track company changes", reportCardLabel: "Result", reportCardTitle: "Export to PDF and Excel",
      localEyebrow: "Local specialization", localTitle: "Data for checking companies in the Republic of Moldova", localLead: "Credibil brings together available company information, related people, roles, and corporate connections in one workflow. The service is not a government portal and does not replace legal advice.", seeProduct: "See the product",
      capEyebrow: "Four essential actions", capTitle: "From search to monitoring in one workflow",
      featureSearchTitle: "Unified search", featureSearchText: "Find companies and people by name or IDNO, with results separated by entity type.",
      featureDataTitle: "Data and connections", featureDataText: "Review founders, administrators, ownership shares, and companies connected through people and organizations.",
      featureReportTitle: "Structured report", featureReportText: "Retain the result of a check by exporting the available report to PDF or Excel.",
      featureMonitorTitle: "Company monitoring", featureMonitorText: "Add a company to your watchlist and review available notifications about changes.",
      directionsEyebrow: "Product areas", directionsTitle: "What you can check in Credibil",
      dirCompanies: "Companies", dirCompaniesText: "Registration and classification data, status, address, CAEM, and available tax information.",
      dirPeople: "People and connections", dirPeopleText: "Founders, administrators, roles, ownership shares, and connected organizations.",
      dirReports: "Reports", dirReportsText: "Thematic sections and export of the check result to PDF and Excel.",
      dirAttention: "Attention factors", dirAttentionText: "Check whether data is available on debts, litigation, enforcement, sanctions, and other sections.",
      productEyebrow: "Working product", productTitle: "A real interface, not an abstract promise", productLead: "The frames below come from the Credibil product and show search, the company card, and corporate connections.",
      gallerySearchTitle: "Search by name, IDNO, or full name", gallerySearchText: "Results are visually separated between companies and people.", galleryCompanyTitle: "Company card", galleryCompanyText: "Core details, responsible people, and primary actions are available in one screen.", galleryRelationsTitle: "Corporate connections", galleryRelationsText: "Compare roles and ownership in List view or switch to the Scheme available in the product.",
      connectionsEyebrow: "Company card and connections", connectionsTitle: "Understand who manages, owns, and connects the company", connectionsLead: "Credibil shows IDNO, status, founders, administrator, ownership shares, and connected organizations. Connections can be reviewed in List and Scheme views.",
      connectionItemOne: "Founders and ownership shares", connectionItemTwo: "Administrators and roles in other companies", connectionItemThree: "Active and liquidated companies in the same context", checkCompany: "Check a company", listView: "List", schemeView: "Scheme",
      riskEyebrow: "Available data and reports", riskTitle: "Check for information that may require attention", riskLead: "Data availability varies by company. The interface should distinguish between unavailable data, no results found, and a section that has not been populated yet.",
      riskFinance: "Financial reports", riskSection: "Dedicated section", riskCourt: "Court cases", riskAvailability: "Available-data check", riskExecutions: "Enforcement proceedings", riskActiveArchive: "Active and archived", riskProcurement: "Public procurement", riskAccreditations: "Accreditations", riskCompanySection: "Section in the company card", riskSanctions: "Sanctions", riskMatchCheck: "Available-match check",
      reportKicker: "Actions confirmed in the company card", reportTitle: "Export the result to PDF or Excel",
      example: "Example", eventTitle: "The company administrator changed", eventText: "This sample notification demonstrates the change type and links to the monitored company. It is not a real event.",
      monitoringEyebrow: "Change monitoring", monitoringTitle: "Do not repeat the same check manually", monitoringLead: "Add a company to monitoring, return to the watchlist, and review available notifications when changes appear in the system.",
      monitorStepOneTitle: "Add the company", monitorStepOneText: "The action is available directly in the company card.", monitorStepTwoTitle: "Review the watchlist", monitorStepTwoText: "Monitored companies are grouped in one section.", monitorStepThreeTitle: "Manage monitoring", monitorStepThreeText: "Open a company or remove it from the watchlist.",
      moldacEyebrow: "MOLDAC accreditations", moldacTitle: "A dedicated section for accreditation search", moldacLead: "The product includes MOLDAC accreditation filtering and an associated section in the company card. Data availability and completeness must be confirmed before publication.", checkAccreditation: "Check accreditation",
      howEyebrow: "A clear workflow", howTitle: "How the check works", howOneTitle: "Find", howOneText: "Enter a company name, IDNO, or the full name of a related person.", howTwoTitle: "Review", howTwoText: "Inspect core data, roles, connections, and available sections.", howThreeTitle: "Keep the result", howThreeText: "Export a report or add the company to monitoring.",
      finalEyebrow: "Start with a name or IDNO", finalTitle: "Check a counterparty before your next decision", finalText: "The entered query will be retained and opened in Credibil search after authentication.",
      footerText: "A tool for reviewing available information about companies and related people in the Republic of Moldova.", footerProduct: "Product", footerAccount: "Account", footerLegal: "Legal", privacy: "Privacy policy", terms: "Terms of use", footerLegalNote: "The legal owner name and contact details are added after confirmation."
    }
  };

  const root = document.documentElement;
  const menuButton = document.querySelector(".menu-button");
  const mobileMenu = document.getElementById("mobile-menu");
  const header = document.getElementById("header");
  const searchForm = document.getElementById("check");
  const searchInput = document.getElementById("company-search");
  const searchStatus = document.getElementById("search-status");
  const languageButtons = [...document.querySelectorAll("[data-lang]")];

  const pushEvent = (event, data = {}) => {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event, ...data });
  };

  const setLanguage = (language) => {
    const lang = translations[language] ? language : "ro";
    const dictionary = translations[lang];
    root.lang = lang;
    document.title = dictionary.metaTitle;
    document.querySelector('meta[name="description"]').setAttribute("content", dictionary.metaDescription);
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.dataset.i18n;
      if (dictionary[key]) element.textContent = dictionary[key];
    });
    document.querySelectorAll("[data-i18n-html]").forEach((element) => {
      const key = element.dataset.i18nHtml;
      if (dictionary[key]) element.innerHTML = dictionary[key];
    });
    searchInput.placeholder = dictionary.searchPlaceholder;
    languageButtons.forEach((button) => {
      const active = button.dataset.lang === lang;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    localStorage.setItem("credibilLanguage", lang);
  };

  const closeMenu = () => {
    mobileMenu.hidden = true;
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Deschide meniul");
    menuButton.querySelector("use").setAttribute("href", "#i-menu");
    document.body.classList.remove("menu-open");
  };

  menuButton.addEventListener("click", () => {
    const open = mobileMenu.hidden;
    mobileMenu.hidden = !open;
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.querySelector("use").setAttribute("href", open ? "#i-close" : "#i-menu");
    document.body.classList.toggle("menu-open", open);
  });

  mobileMenu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));

  languageButtons.forEach((button) => {
    button.addEventListener("click", () => {
      setLanguage(button.dataset.lang);
      pushEvent("language_select", { language: button.dataset.lang });
    });
  });

  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = searchInput.value.trim();
    const lang = root.lang;
    if (query.length < 2) {
      searchStatus.textContent = translations[lang].searchRequired;
      searchInput.setAttribute("aria-invalid", "true");
      searchInput.focus();
      return;
    }

    searchInput.removeAttribute("aria-invalid");
    sessionStorage.setItem("credibilSearchQuery", query);
    sessionStorage.setItem("credibilLandingLanguage", lang);
    searchStatus.textContent = translations[lang].searchRedirect;
    pushEvent("public_search_submit", { query_length: query.length, language: lang });

    const redirect = `/ru/login?returnTo=${encodeURIComponent("/ru/search")}&query=${encodeURIComponent(query)}`;
    if (window.location.protocol !== "file:") {
      window.setTimeout(() => { window.location.assign(redirect); }, 650);
    }
  });

  document.querySelectorAll("[data-track]").forEach((element) => {
    element.addEventListener("click", () => pushEvent("cta_click", { cta: element.dataset.track, language: root.lang }));
  });

  const updateHeader = () => header.classList.toggle("is-sticky", window.scrollY > 80);
  window.addEventListener("scroll", updateHeader, { passive: true });
  updateHeader();

  document.getElementById("year").textContent = new Date().getFullYear();
  setLanguage(localStorage.getItem("credibilLanguage") || "ro");
})();
