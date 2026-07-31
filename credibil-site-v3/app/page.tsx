"use client";

/* eslint-disable @next/next/no-img-element */

import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  Bell,
  Buildings,
  CaretDown,
  Check,
  CheckCircle,
  ClockCounterClockwise,
  FilePdf,
  FileXls,
  Gavel,
  IdentificationCard,
  List,
  MagnifyingGlass,
  Medal,
  SealCheck,
  ShieldCheck,
  ShieldWarning,
  TreeStructure,
  User,
  X,
} from "@phosphor-icons/react";
import { MoldovaTrustVisual } from "./MoldovaTrustVisual";

type Language = "ro" | "en";
type ProductView = "company" | "relations" | "search" | "monitoring";

const copy = {
  ro: {
    nav: ["Funcționalități", "Produs", "Monitorizare", "Acreditări"],
    login: "Autentificare",
    start: "Începeți verificarea",
    eyebrow: "Verificarea companiilor și a persoanelor asociate din Moldova",
    title: "Verificați partenerii din Moldova înainte de a decide",
    lead:
      "Căutați după denumire, IDNO ori nume. Analizați datele, legăturile și factorii care necesită atenție înainte de orice decizie.",
    searchLabel: "Denumire, IDNO sau nume",
    searchPlaceholder: "Introduceți denumirea, IDNO sau numele",
    searchButton: "Verificați partenerul",
    searchHint: "Selectați o companie sau o persoană din rezultate",
    companies: "Companii",
    people: "Persoane",
    evidence: ["Date de înregistrare", "PDF și Excel", "Monitorizare"],
    dossier: "DOSAR 01 / VERIFICARE",
    interfaceLabel: "Interfață reală Credibil",
    updated: "Date afișate conform capturii produsului",
    dialogEyebrow: "Pasul următor",
    dialogTitle: "Autentificarea este necesară",
    dialogText:
      "Solicitarea a fost păstrată. După autentificare, căutarea poate continua în Credibil.",
    continueLogin: "Continuați",
    back: "Reveniți",
    introTitle: "De la identificare la decizie documentată",
    trustEyebrow: "Verificarea partenerilor din Moldova",
    trustTitle: "Credibil - informația în care puteți avea",
    trustAccent: "încredere.",
    trustText:
      "Ajutăm companiile să ia decizii documentate, oferind informații structurate despre companii și întreprinzători individuali din Republica Moldova.",
    capabilitiesEyebrow: "Un singur spațiu de verificare",
    capabilitiesTitle: "Mai puține ferestre. Mai mult context.",
    capabilitiesLead:
      "Credibil reunește informația disponibilă despre companie, persoane asociate și evenimente într-un dosar ușor de parcurs.",
    capabilities: [
      {
        title: "Identificați entitatea corectă",
        text: "Căutați după denumire, IDNO sau nume și separați rapid companiile de persoanele asociate.",
        meta: "Căutare și sugestii",
      },
      {
        title: "Urmăriți relațiile relevante",
        text: "Vedeți fondatori, administratori, roluri și cote de participare acolo unde datele sunt disponibile.",
        meta: "Persoane și companii",
      },
      {
        title: "Documentați analiza",
        text: "Exportați informațiile disponibile în PDF sau Excel pentru evaluare internă și păstrarea traseului deciziei.",
        meta: "PDF și Excel",
      },
      {
        title: "Reveniți când apar schimbări",
        text: "Adăugați compania la monitorizare și consultați notificările privind modificările înregistrate.",
        meta: "Monitorizare",
      },
    ],
    productEyebrow: "Produsul, nu o ilustrație",
    productTitle: "Dosarul real al unei companii",
    productLead:
      "Schimbați perspectiva fără să pierdeți contextul. Fiecare vedere folosește capturi reale din Credibil.",
    productTabs: {
      company: "Profil",
      relations: "Relații",
      search: "Căutare",
      monitoring: "Monitorizare",
    },
    productViews: {
      company: {
        title: "Datele de bază înainte de analiză",
        text: "Statut, IDNO, adresă, formă juridică și persoane asociate într-o singură vedere.",
      },
      relations: {
        title: "Relațiile capătă structură",
        text: "Rolurile și participațiile sunt prezentate lângă entitățile cu care sunt conectate.",
      },
      search: {
        title: "Ajungeți repede la entitatea corectă",
        text: "Sugestiile diferențiază companiile și persoanele înainte de deschiderea dosarului.",
      },
      monitoring: {
        title: "Companiile urmărite rămân la vedere",
        text: "Lista de monitorizare și notificările sunt separate clar pentru o verificare rapidă.",
      },
    },
    anatomyEyebrow: "Anatomia verificării",
    anatomyTitle: "Faptele sunt separate de interpretare",
    anatomyText:
      "Credibil organizează datele disponibile pe niveluri: identitate, relații, evenimente și factori care pot necesita o analiză suplimentară.",
    anatomyFacts: [
      ["Identitate", "Denumire, IDNO, statut, adresă"],
      ["Control", "Fondatori, administratori, participații"],
      ["Evenimente", "Modificări și istoric disponibil"],
    ],
    coverageEyebrow: "Acoperire în dosar",
    coverageTitle: "Un tablou de control pentru întrebările importante",
    coverageLead:
      "Disponibilitatea și profunzimea informațiilor depind de entitate și de datele importate. Credibil indică transparent când o secțiune nu conține informații.",
    coverage: [
      ["Date financiare", "Rapoarte și indicatori disponibili"],
      ["Dosare judiciare", "Cauze identificate pentru entitate"],
      ["Executări", "Proceduri active sau arhivate"],
      ["Achiziții publice", "Participări și contracte disponibile"],
      ["Sancțiuni", "Verificarea informațiilor disponibile"],
      ["Acreditări", "Înregistrări importate din MOLDAC"],
    ],
    reportsEyebrow: "Ieșire documentată",
    reportsTitle: "Luați dosarul cu dumneavoastră",
    reportsText:
      "Generați PDF pentru citire și Excel pentru lucru intern, pe baza informațiilor disponibile în profil.",
    reportsCta: "Deschideți o verificare",
    monitoringEyebrow: "Monitorizare",
    monitoringTitle: "Verificarea nu se încheie după prima căutare",
    monitoringText:
      "Adăugați compania la monitorizare și reveniți la notificări când sunt înregistrate modificări.",
    monitoringSteps: [
      ["01", "Alegeți compania", "Porniți din profilul entității verificate."],
      ["02", "Adăugați la monitorizare", "Compania apare în lista dedicată."],
      ["03", "Consultați schimbările", "Deschideți notificarea și reevaluați contextul."],
    ],
    monitoringExample: "Exemplu de eveniment",
    monitoringEvent: "Actualizare în datele de înregistrare",
    monitoringMeta: "Compania urmărită · stare de verificat",
    moldacEyebrow: "Acreditări MOLDAC",
    moldacTitle: "Acreditările, în același flux de verificare",
    moldacText:
      "Consultați acreditările importate din MOLDAC atunci când acestea sunt disponibile. Filtrați lista și continuați evaluarea în contextul companiei.",
    moldacNote:
      "Disponibilitatea depinde de sincronizarea și conținutul sursei.",
    processEyebrow: "Fluxul de lucru",
    processTitle: "Trei pași de la întrebare la dosar",
    process: [
      ["Căutați", "Introduceți denumirea, IDNO sau numele persoanei."],
      ["Verificați", "Parcurgeți datele, relațiile și secțiunile disponibile."],
      ["Documentați", "Exportați rezultatul sau adăugați compania la monitorizare."],
    ],
    faqEyebrow: "Întrebări frecvente",
    faqTitle: "Înainte de prima verificare",
    faqs: [
      [
        "Ce pot căuta în Credibil?",
        "Puteți căuta companii după denumire sau IDNO și persoane după nume, folosind sugestiile pentru a identifica rezultatul corect.",
      ],
      [
        "Ce conține profilul unei companii?",
        "Profilul poate include date de înregistrare, statut, adresă, fondatori, administratori, participații, relații și alte secțiuni disponibile pentru entitatea respectivă.",
      ],
      [
        "Pot exporta informațiile?",
        "Da. Credibil oferă export în PDF și Excel pentru informațiile disponibile în dosar.",
      ],
      [
        "Cum funcționează monitorizarea?",
        "O companie poate fi adăugată la lista de monitorizare. Modificările înregistrate pot fi consultate în zona de notificări.",
      ],
      [
        "Sunt toate secțiunile completate pentru orice companie?",
        "Nu neapărat. Disponibilitatea datelor diferă în funcție de entitate și de informațiile importate. Interfața indică secțiunile fără date.",
      ],
      [
        "Credibil ia decizia în locul meu?",
        "Nu. Credibil structurează informația disponibilă și sprijină analiza. Decizia și verificările suplimentare rămân în responsabilitatea utilizatorului.",
      ],
    ],
    finalEyebrow: "Începeți cu o întrebare concretă",
    finalTitle: "Pe cine verificați astăzi?",
    finalText:
      "Introduceți compania, IDNO-ul sau numele. Credibil păstrează căutarea și continuă după autentificare.",
    footerClaim: "Informație structurată pentru decizii documentate.",
    footerNote:
      "Credibil prezintă informațiile disponibile și nu înlocuiește analiza juridică, financiară sau de conformitate.",
    footerNav: ["Funcționalități", "Produs", "Monitorizare", "Acreditări"],
  },
  en: {
    nav: ["Features", "Product", "Monitoring", "Accreditations"],
    login: "Sign in",
    start: "Start a check",
    eyebrow: "Company and related-person checks in Moldova",
    title: "Check Moldovan counterparties before making a decision",
    lead:
      "Search by company name, IDNO or full name. Review registration data, connections and factors requiring attention before you decide.",
    searchLabel: "Company name, IDNO or full name",
    searchPlaceholder: "Enter a company name, IDNO or full name",
    searchButton: "Check a counterparty",
    searchHint: "Choose a company or person from the results",
    companies: "Companies",
    people: "People",
    evidence: ["Registration data", "PDF and Excel", "Monitoring"],
    dossier: "DOSSIER 01 / CHECK",
    interfaceLabel: "Real Credibil interface",
    updated: "Data shown as captured in the product",
    dialogEyebrow: "Next step",
    dialogTitle: "Sign-in is required",
    dialogText:
      "Your query has been saved. After authentication, the search can continue in Credibil.",
    continueLogin: "Continue",
    back: "Go back",
    introTitle: "From identification to a documented decision",
    trustEyebrow: "Counterparty checks in Moldova",
    trustTitle: "Credibil - information you can",
    trustAccent: "trust.",
    trustText:
      "We help businesses make documented decisions with structured information about companies and individual entrepreneurs in the Republic of Moldova.",
    capabilitiesEyebrow: "One verification workspace",
    capabilitiesTitle: "Fewer windows. More context.",
    capabilitiesLead:
      "Credibil brings available company, related-person and event information into a dossier that is easy to review.",
    capabilities: [
      {
        title: "Identify the right entity",
        text: "Search by company name, IDNO or full name and quickly distinguish companies from related people.",
        meta: "Search and suggestions",
      },
      {
        title: "Follow relevant relationships",
        text: "See founders, administrators, roles and ownership shares where the data is available.",
        meta: "People and companies",
      },
      {
        title: "Document the review",
        text: "Export available information to PDF or Excel for internal assessment and a traceable decision path.",
        meta: "PDF and Excel",
      },
      {
        title: "Return when something changes",
        text: "Add a company to monitoring and review notifications about recorded changes.",
        meta: "Monitoring",
      },
    ],
    productEyebrow: "The product, not an illustration",
    productTitle: "A real company dossier",
    productLead:
      "Change perspective without losing context. Every view uses real captures from Credibil.",
    productTabs: {
      company: "Profile",
      relations: "Relationships",
      search: "Search",
      monitoring: "Monitoring",
    },
    productViews: {
      company: {
        title: "The basics before analysis",
        text: "Status, IDNO, address, legal form and related people in a single view.",
      },
      relations: {
        title: "Relationships gain structure",
        text: "Roles and ownership shares sit next to the entities they connect.",
      },
      search: {
        title: "Reach the right entity quickly",
        text: "Suggestions distinguish companies from people before the dossier opens.",
      },
      monitoring: {
        title: "Monitored companies stay visible",
        text: "The monitoring list and notifications are clearly separated for a fast review.",
      },
    },
    anatomyEyebrow: "Anatomy of a check",
    anatomyTitle: "Facts stay separate from interpretation",
    anatomyText:
      "Credibil organises available data into layers: identity, relationships, events and factors that may require further review.",
    anatomyFacts: [
      ["Identity", "Name, IDNO, status, address"],
      ["Control", "Founders, administrators, ownership"],
      ["Events", "Recorded changes and available history"],
    ],
    coverageEyebrow: "Dossier coverage",
    coverageTitle: "A control surface for important questions",
    coverageLead:
      "Information depth and availability depend on the entity and imported data. Credibil clearly indicates when a section contains no information.",
    coverage: [
      ["Financial data", "Available reports and indicators"],
      ["Court cases", "Cases identified for the entity"],
      ["Enforcement", "Active or archived proceedings"],
      ["Public procurement", "Available participation and contracts"],
      ["Sanctions", "Review of available information"],
      ["Accreditations", "Records imported from MOLDAC"],
    ],
    reportsEyebrow: "Documented output",
    reportsTitle: "Take the dossier with you",
    reportsText:
      "Generate a PDF for reading or Excel for internal work, based on the information available in the profile.",
    reportsCta: "Open a check",
    monitoringEyebrow: "Monitoring",
    monitoringTitle: "Verification does not end after the first search",
    monitoringText:
      "Add the company to monitoring and return to notifications when changes are recorded.",
    monitoringSteps: [
      ["01", "Choose the company", "Start from the verified entity profile."],
      ["02", "Add it to monitoring", "The company appears in the dedicated list."],
      ["03", "Review the changes", "Open the notification and reassess the context."],
    ],
    monitoringExample: "Example event",
    monitoringEvent: "Registration data updated",
    monitoringMeta: "Monitored company · review required",
    moldacEyebrow: "MOLDAC accreditations",
    moldacTitle: "Accreditations in the same verification flow",
    moldacText:
      "Review accreditations imported from MOLDAC when available. Filter the list and continue the assessment in the company context.",
    moldacNote: "Availability depends on source content and synchronisation.",
    processEyebrow: "Workflow",
    processTitle: "Three steps from question to dossier",
    process: [
      ["Search", "Enter a company name, IDNO or a person’s name."],
      ["Review", "Explore available data, relationships and sections."],
      ["Document", "Export the result or add the company to monitoring."],
    ],
    faqEyebrow: "Frequently asked questions",
    faqTitle: "Before your first check",
    faqs: [
      [
        "What can I search in Credibil?",
        "Search companies by name or IDNO and people by full name, using suggestions to identify the correct result.",
      ],
      [
        "What does a company profile contain?",
        "A profile may include registration data, status, address, founders, administrators, ownership shares, relationships and other sections available for that entity.",
      ],
      [
        "Can I export information?",
        "Yes. Credibil provides PDF and Excel export for information available in the dossier.",
      ],
      [
        "How does monitoring work?",
        "A company can be added to the monitoring list. Recorded changes can be reviewed in the notifications area.",
      ],
      [
        "Is every section complete for every company?",
        "Not necessarily. Data availability varies by entity and imported information. The interface indicates sections without data.",
      ],
      [
        "Does Credibil make the decision for me?",
        "No. Credibil structures available information and supports analysis. The decision and any additional checks remain the user’s responsibility.",
      ],
    ],
    finalEyebrow: "Start with a concrete question",
    finalTitle: "Who are you checking today?",
    finalText:
      "Enter the company, IDNO or name. Credibil saves the query and continues after sign-in.",
    footerClaim: "Structured information for documented decisions.",
    footerNote:
      "Credibil presents available information and does not replace legal, financial or compliance analysis.",
    footerNav: ["Features", "Product", "Monitoring", "Accreditations"],
  },
} as const;

const searchResults = [
  {
    type: "company",
    name: "Societatea cu Răspundere Limitată ABESVEB",
    idno: "1015602000935",
  },
  {
    type: "company",
    name: "Organizația de Creditare Nebancară ABESFIN S.R.L.",
    idno: "1017607003500",
  },
  { type: "person", name: "Bodjgua Abessalom", idno: "" },
  { type: "person", name: "BODJGUA ABESSALOM", idno: "" },
] as const;

const productAssets: Record<
  ProductView,
  { src: string; width: number; height: number; altRo: string; altEn: string }
> = {
  company: {
    src: "/assets/product-company.webp",
    width: 1350,
    height: 483,
    altRo: "Profilul unei companii în Credibil",
    altEn: "A company profile in Credibil",
  },
  relations: {
    src: "/assets/product-relations.webp",
    width: 1350,
    height: 761,
    altRo: "Relațiile corporative într-un profil Credibil",
    altEn: "Corporate relationships in a Credibil profile",
  },
  search: {
    src: "/assets/product-search.webp",
    width: 1080,
    height: 360,
    altRo: "Căutarea de companii și persoane în Credibil",
    altEn: "Company and person search in Credibil",
  },
  monitoring: {
    src: "/assets/product-monitoring.webp",
    width: 1200,
    height: 372,
    altRo: "Lista de monitorizare Credibil",
    altEn: "Credibil monitoring list",
  },
};

const navTargets = ["#capabilities", "#product", "#monitoring", "#moldac"];

function pushEvent(event: string, detail: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;
  const target = window as Window & {
    dataLayer?: Array<Record<string, unknown>>;
  };
  target.dataLayer = target.dataLayer || [];
  target.dataLayer.push({ event, ...detail });
}

export default function Home() {
  const [language, setLanguage] = useState<Language>("ro");
  const [query, setQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [activeProduct, setActiveProduct] = useState<ProductView>("company");
  const searchRef = useRef<HTMLInputElement>(null);
  const t = copy[language];
  const product = productAssets[activeProduct];

  useEffect(() => {
    const stored = window.localStorage.getItem("credibilLanguage");
    if (stored !== "ro" && stored !== "en") return;
    const frame = window.requestAnimationFrame(() => {
      setLanguage(stored);
      document.documentElement.lang = stored;
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSearchOpen(false);
        setMenuOpen(false);
        setAuthOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const changeLanguage = (next: Language) => {
    setLanguage(next);
    document.documentElement.lang = next;
    window.localStorage.setItem("credibilLanguage", next);
    pushEvent("language_select", { language: next });
  };

  const submitSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalized = query.trim();
    if (normalized.length < 2) {
      searchRef.current?.focus();
      return;
    }
    window.sessionStorage.setItem("credibilSearchQuery", normalized);
    pushEvent("public_search_submit", {
      language,
      query_length: normalized.length,
    });
    setSearchOpen(false);
    setAuthOpen(true);
  };

  const chooseResult = (name: string) => {
    setQuery(name);
    setSearchOpen(false);
    pushEvent("search_result_selected", { language });
  };

  const openAuth = () => {
    setAuthOpen(true);
    setMenuOpen(false);
  };

  return (
    <main>
      <a className="skip-link" href="#hero-search">
        {language === "ro" ? "Săriți la căutare" : "Skip to search"}
      </a>

      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="#top" aria-label="Credibil">
            <img
              src="/assets/credibil-logo-light.svg"
              alt="Credibil"
              width="187"
              height="54"
            />
          </a>

          <nav className="desktop-nav" aria-label="Primary navigation">
            {t.nav.map((item, index) => (
              <a key={item} href={navTargets[index]}>
                {item}
              </a>
            ))}
          </nav>

          <div className="header-actions">
            <div className="language-control" aria-label="Language">
              <button
                type="button"
                aria-pressed={language === "ro"}
                onClick={() => changeLanguage("ro")}
              >
                RO
              </button>
              <span aria-hidden="true">/</span>
              <button
                type="button"
                aria-pressed={language === "en"}
                onClick={() => changeLanguage("en")}
              >
                EN
              </button>
              <CaretDown size={13} weight="bold" aria-hidden="true" />
            </div>
            <button className="text-button desktop-action" type="button" onClick={openAuth}>
              {t.login}
            </button>
            <a className="outline-button desktop-action" href="#hero-search">
              {t.start}
            </a>
            <button
              className="menu-button"
              type="button"
              aria-expanded={menuOpen}
              aria-controls="mobile-menu"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              onClick={() => setMenuOpen((value) => !value)}
            >
              {menuOpen ? <X size={23} /> : <List size={23} />}
            </button>
          </div>
        </div>

        {menuOpen && (
          <nav className="mobile-menu" id="mobile-menu" aria-label="Mobile navigation">
            {t.nav.map((item, index) => (
              <a key={item} href={navTargets[index]} onClick={() => setMenuOpen(false)}>
                {item}
                <ArrowRight size={18} aria-hidden="true" />
              </a>
            ))}
            <button type="button" onClick={openAuth}>
              {t.login}
            </button>
          </nav>
        )}
      </header>

      <section className="hero" id="top">
        <div className="dossier-rail" aria-hidden="true">
          <span>{t.dossier}</span>
          <b>P. 01</b>
        </div>

        <div className="hero-grid">
          <div className="hero-copy">
            <p className="eyebrow">{t.eyebrow}</p>
            <h1>{t.title}</h1>
            <p className="hero-lead">{t.lead}</p>

            <form className="hero-search" id="hero-search" role="search" onSubmit={submitSearch}>
              <label htmlFor="counterparty-search">{t.searchLabel}</label>
              <div className="search-row">
                <div className="search-field">
                  <MagnifyingGlass size={26} aria-hidden="true" />
                  <input
                    ref={searchRef}
                    id="counterparty-search"
                    type="search"
                    value={query}
                    minLength={2}
                    autoComplete="off"
                    placeholder={t.searchPlaceholder}
                    onFocus={() => query.trim().length >= 2 && setSearchOpen(true)}
                    onChange={(event) => {
                      const value = event.target.value;
                      setQuery(value);
                      setSearchOpen(value.trim().length >= 2);
                    }}
                  />
                  <kbd>Enter</kbd>
                </div>
                <button className="primary-button" type="submit">
                  <span>{t.searchButton}</span>
                  <ArrowRight size={20} aria-hidden="true" />
                </button>
              </div>

              {searchOpen && (
                <div className="search-results" role="listbox" aria-label={t.searchHint}>
                  <p>{t.companies}</p>
                  {searchResults.slice(0, 2).map((result) => (
                    <button
                      key={result.name}
                      type="button"
                      role="option"
                      aria-selected={query === result.name}
                      onClick={() => chooseResult(result.name)}
                    >
                      <Buildings size={22} weight="duotone" aria-hidden="true" />
                      <span>
                        <b>{result.name}</b>
                        <small>IDNO: {result.idno}</small>
                      </span>
                      <ArrowRight size={17} aria-hidden="true" />
                    </button>
                  ))}
                  <p>{t.people}</p>
                  {searchResults.slice(2).map((result) => (
                    <button
                      key={result.name}
                      type="button"
                      role="option"
                      aria-selected={query === result.name}
                      onClick={() => chooseResult(result.name)}
                    >
                      <User size={22} weight="duotone" aria-hidden="true" />
                      <span>
                        <b>{result.name}</b>
                      </span>
                      <ArrowRight size={17} aria-hidden="true" />
                    </button>
                  ))}
                </div>
              )}
            </form>

            <div className="hero-evidence" aria-label="Confirmed product capabilities">
              {t.evidence.map((item, index) => (
                <span key={item}>
                  {index === 0 && <Check size={16} weight="bold" aria-hidden="true" />}
                  {index === 1 && <FilePdf size={16} weight="bold" aria-hidden="true" />}
                  {index === 2 && <Bell size={16} weight="bold" aria-hidden="true" />}
                  {item}
                </span>
              ))}
            </div>
          </div>

          <figure className="hero-product">
            <figcaption>
              <span>{t.interfaceLabel}</span>
              <span>
                <i aria-hidden="true" />
                MD / COMPANY
              </span>
            </figcaption>
            <div className="product-crop product-stack">
              <img
                className="company-shot"
                src="/assets/product-company.webp"
                width="1350"
                height="483"
                alt={
                  language === "ro"
                    ? "Profil Credibil cu statutul și datele unei companii"
                    : "Credibil profile with a company status and registration data"
                }
              />
              <img
                className="relations-shot"
                src="/assets/product-relations.webp"
                width="1350"
                height="761"
                alt={
                  language === "ro"
                    ? "Relații corporative cu persoane, roluri și participații"
                    : "Corporate relationships with people, roles and ownership shares"
                }
              />
            </div>
            <div className="product-meta">
              <span>{t.updated}</span>
              <span>
                PDF <FilePdf size={15} weight="fill" aria-hidden="true" />
              </span>
              <span>
                Excel <FileXls size={15} weight="fill" aria-hidden="true" />
              </span>
            </div>
          </figure>
        </div>
      </section>

      <section className="first-slice-note" id="capabilities">
        <p>01</p>
        <h2>{t.introTitle}</h2>
        <ArrowRight size={28} aria-hidden="true" />
      </section>

      <section className="trust-map-section" aria-labelledby="credibil-trust-title">
        <div className="trust-map-card">
          <div className="trust-map-copy">
            <p className="trust-map-eyebrow">{t.trustEyebrow}</p>
            <h2 id="credibil-trust-title">
              {t.trustTitle} <span>{t.trustAccent}</span>
            </h2>
            <p className="trust-map-lead">{t.trustText}</p>
          </div>

          <MoldovaTrustVisual />
        </div>
      </section>

      <section className="capabilities section">
        <div className="section-heading">
          <div>
            <p className="section-eyebrow">{t.capabilitiesEyebrow}</p>
            <h2>{t.capabilitiesTitle}</h2>
          </div>
          <p>{t.capabilitiesLead}</p>
        </div>

        <div className="capability-ledger">
          {t.capabilities.map((item, index) => (
            <article key={item.title}>
              <span className="ledger-index">0{index + 1}</span>
              <span className="ledger-icon" aria-hidden="true">
                {index === 0 && <MagnifyingGlass size={25} />}
                {index === 1 && <TreeStructure size={25} />}
                {index === 2 && <FilePdf size={25} />}
                {index === 3 && <Bell size={25} />}
              </span>
              <div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </div>
              <small>{item.meta}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="product-showcase section" id="product">
        <div className="section-heading product-heading">
          <div>
            <p className="section-eyebrow">{t.productEyebrow}</p>
            <h2>{t.productTitle}</h2>
          </div>
          <p>{t.productLead}</p>
        </div>

        <div className="product-workbench">
          <div className="product-tabs" role="tablist" aria-label={t.productTitle}>
            {(Object.keys(t.productTabs) as ProductView[]).map((view, index) => (
              <button
                key={view}
                type="button"
                role="tab"
                aria-selected={activeProduct === view}
                aria-controls="product-panel"
                onClick={() => {
                  setActiveProduct(view);
                  pushEvent("product_view_select", { language, view });
                }}
              >
                <span>0{index + 1}</span>
                {t.productTabs[view]}
              </button>
            ))}
          </div>

          <div className="product-panel" id="product-panel" role="tabpanel">
            <div className="product-panel-copy">
              <span>{activeProduct.toUpperCase()} / MD</span>
              <h3>{t.productViews[activeProduct].title}</h3>
              <p>{t.productViews[activeProduct].text}</p>
            </div>
            <div className={`product-panel-image image-${activeProduct}`}>
              <img
                key={product.src}
                src={product.src}
                width={product.width}
                height={product.height}
                alt={language === "ro" ? product.altRo : product.altEn}
              />
            </div>
          </div>
        </div>
      </section>

      <section className="anatomy">
        <div className="anatomy-inner">
          <div className="anatomy-copy">
            <p className="section-eyebrow light">{t.anatomyEyebrow}</p>
            <h2>{t.anatomyTitle}</h2>
            <p>{t.anatomyText}</p>
          </div>

          <div className="anatomy-list">
            {t.anatomyFacts.map((fact, index) => (
              <div key={fact[0]}>
                <span>0{index + 1}</span>
                <strong>{fact[0]}</strong>
                <p>{fact[1]}</p>
              </div>
            ))}
          </div>

          <div className="relation-sheet">
            <div className="relation-sheet-top">
              <span>VISPY / 1026023120722</span>
              <ShieldCheck size={21} weight="duotone" aria-hidden="true" />
            </div>
            <img
              src="/assets/product-relations.webp"
              width="1350"
              height="761"
              alt={
                language === "ro"
                  ? "Fragment real din lista de relații Credibil"
                  : "Real extract from the Credibil relationships list"
              }
            />
          </div>
        </div>
      </section>

      <section className="coverage section">
        <div className="coverage-intro">
          <p className="section-eyebrow">{t.coverageEyebrow}</p>
          <h2>{t.coverageTitle}</h2>
          <p>{t.coverageLead}</p>
        </div>

        <div className="coverage-ledger">
          {t.coverage.map((item, index) => (
            <article key={item[0]}>
              <span aria-hidden="true">
                {index === 0 && <FileXls size={23} />}
                {index === 1 && <Gavel size={23} />}
                {index === 2 && <ShieldWarning size={23} />}
                {index === 3 && <Buildings size={23} />}
                {index === 4 && <ShieldCheck size={23} />}
                {index === 5 && <Medal size={23} />}
              </span>
              <h3>{item[0]}</h3>
              <p>{item[1]}</p>
              <small>0{index + 1}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="reports-band">
        <div className="reports-inner">
          <div>
            <p className="section-eyebrow light">{t.reportsEyebrow}</p>
            <h2>{t.reportsTitle}</h2>
          </div>
          <p>{t.reportsText}</p>
          <div className="format-stamps" aria-label="Export formats">
            <span>
              <FilePdf size={28} weight="duotone" aria-hidden="true" />
              PDF
            </span>
            <span>
              <FileXls size={28} weight="duotone" aria-hidden="true" />
              Excel
            </span>
          </div>
          <a className="outline-button" href="#hero-search">
            {t.reportsCta}
            <ArrowRight size={18} aria-hidden="true" />
          </a>
        </div>
      </section>

      <section className="monitoring section" id="monitoring">
        <div className="monitoring-intro">
          <p className="section-eyebrow">{t.monitoringEyebrow}</p>
          <h2>{t.monitoringTitle}</h2>
          <p>{t.monitoringText}</p>
        </div>

        <div className="monitoring-stage">
          <figure>
            <figcaption>
              <span>MONITORING / MD</span>
              <span>
                <i aria-hidden="true" />
                ACTIVE
              </span>
            </figcaption>
            <img
              src="/assets/product-monitoring.webp"
              width="1200"
              height="372"
              alt={
                language === "ro"
                  ? "Interfața de monitorizare Credibil"
                  : "Credibil monitoring interface"
              }
            />
          </figure>

          <aside className="event-ticket">
            <span>{t.monitoringExample}</span>
            <Bell size={24} weight="duotone" aria-hidden="true" />
            <strong>{t.monitoringEvent}</strong>
            <p>{t.monitoringMeta}</p>
            <small>09:42 / MD</small>
          </aside>
        </div>

        <div className="monitoring-steps">
          {t.monitoringSteps.map((step) => (
            <article key={step[0]}>
              <span>{step[0]}</span>
              <h3>{step[1]}</h3>
              <p>{step[2]}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="moldac section" id="moldac">
        <div className="moldac-grid">
          <div className="moldac-copy">
            <div className="moldac-mark">
              <SealCheck size={28} weight="duotone" aria-hidden="true" />
              MOLDAC / MD
            </div>
            <p className="section-eyebrow">{t.moldacEyebrow}</p>
            <h2>{t.moldacTitle}</h2>
            <p>{t.moldacText}</p>
            <small>{t.moldacNote}</small>
          </div>
          <figure className="moldac-viewport">
            <figcaption>
              <span>ACCREDITATIONS</span>
              <span>FILTER / SEARCH</span>
            </figcaption>
            <img
              src="/assets/product-moldac.webp"
              width="1100"
              height="343"
              alt={
                language === "ro"
                  ? "Interfața acreditărilor MOLDAC în Credibil"
                  : "MOLDAC accreditations interface in Credibil"
              }
            />
          </figure>
        </div>
      </section>

      <section className="process section">
        <div className="process-title">
          <p className="section-eyebrow">{t.processEyebrow}</p>
          <h2>{t.processTitle}</h2>
        </div>
        <div className="process-list">
          {t.process.map((item, index) => (
            <article key={item[0]}>
              <span>0{index + 1}</span>
              <div>
                <h3>{item[0]}</h3>
                <p>{item[1]}</p>
              </div>
              {index === 0 && <MagnifyingGlass size={27} aria-hidden="true" />}
              {index === 1 && <IdentificationCard size={27} aria-hidden="true" />}
              {index === 2 && <CheckCircle size={27} aria-hidden="true" />}
            </article>
          ))}
        </div>
      </section>

      <section className="faq section">
        <div className="faq-heading">
          <p className="section-eyebrow">{t.faqEyebrow}</p>
          <h2>{t.faqTitle}</h2>
          <ClockCounterClockwise size={38} weight="duotone" aria-hidden="true" />
        </div>
        <div className="faq-list">
          {t.faqs.map((item, index) => (
            <details key={item[0]} open={index === 0}>
              <summary>
                <span>{item[0]}</span>
                <CaretDown size={20} aria-hidden="true" />
              </summary>
              <p>{item[1]}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="final-search">
        <div className="final-search-inner">
          <p className="section-eyebrow light">{t.finalEyebrow}</p>
          <h2>{t.finalTitle}</h2>
          <p>{t.finalText}</p>
          <form role="search" onSubmit={submitSearch}>
            <label htmlFor="final-query">{t.searchLabel}</label>
            <div className="final-field">
              <MagnifyingGlass size={25} aria-hidden="true" />
              <input
                id="final-query"
                type="search"
                minLength={2}
                value={query}
                placeholder={t.searchPlaceholder}
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
            <button className="primary-button" type="submit">
              {t.searchButton}
              <ArrowRight size={19} aria-hidden="true" />
            </button>
          </form>
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-main">
          <div>
            <img
              src="/assets/credibil-logo-light.svg"
              width="187"
              height="54"
              alt="Credibil"
            />
            <p>{t.footerClaim}</p>
          </div>
          <nav aria-label="Footer navigation">
            {t.footerNav.map((item, index) => (
              <a key={item} href={navTargets[index]}>
                {item}
              </a>
            ))}
          </nav>
          <button className="outline-button" type="button" onClick={openAuth}>
            {t.login}
          </button>
        </div>
        <div className="footer-bottom">
          <p>{t.footerNote}</p>
          <span>© {new Date().getFullYear()} Credibil</span>
        </div>
      </footer>

      {authOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => setAuthOpen(false)}>
          <section
            className="auth-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="auth-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <button
              className="modal-close"
              type="button"
              aria-label="Close"
              onClick={() => setAuthOpen(false)}
            >
              <X size={22} />
            </button>
            <p className="modal-eyebrow">{t.dialogEyebrow}</p>
            <h2 id="auth-title">{t.dialogTitle}</h2>
            <p>{t.dialogText}</p>
            <div className="modal-actions">
              <a
                className="primary-button"
                href={`/ru/login?returnTo=${encodeURIComponent("/ru/search")}&query=${encodeURIComponent(
                  query.trim(),
                )}`}
                onClick={() => pushEvent("login_continue", { language })}
              >
                {t.continueLogin}
                <ArrowRight size={19} />
              </a>
              <button className="text-button dark" type="button" onClick={() => setAuthOpen(false)}>
                {t.back}
              </button>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
