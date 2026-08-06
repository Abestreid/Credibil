import { useEffect, useMemo, useRef, useState } from "react";
import {
  BellRinging, Buildings, FileText, IdentificationCard,
  MagnifyingGlass, ShareNetwork, ShieldWarning,
} from "@phosphor-icons/react";

const legacyWords = ["статус", "владельцев", "связи", "риски"];

const copy = {
  ro: {
    lang: "RO",
    altLang: "RU",
    metaTitle: "Credibil - verificarea companiilor și partenerilor din Moldova",
    metaDescription: "Verificați companii și persoane asociate după denumire, IDNO sau nume. Analizați date, legături, riscuri disponibile, rapoarte și schimbări în Moldova.",
    ogTitle: "Credibil - date pentru verificarea partenerilor din Moldova",
    ogDescription: "Găsiți o companie sau o persoană, analizați datele de înregistrare și legăturile, generați un raport sau activați monitorizarea.",
    skip: "Treceți la conținut",
    nav: [
      ["Produs", "product"], ["Legături", "connections"], ["Monitorizare", "monitoring"], ["Rapoarte", "reports"],
    ],
    login: "Autentificare",
    primary: "Începeți verificarea",
    hero: {
      eyebrow: "Verificarea companiilor și a persoanelor asociate din Moldova",
      action: "Verificați",
      words: ["statutul", "proprietarii", "legăturile", "riscurile"],
      h1: "Verificați partenerii din Moldova înainte de a decide",
      lead: "Găsiți o companie sau o persoană asociată după denumire, IDNO ori nume. Analizați datele de înregistrare, legăturile și factorii de risc disponibili.",
      proof: ["Date de înregistrare", "Persoane asociate", "Evenimente", "Monitorizare"],
    },
    search: {
      label: "Denumire, IDNO sau nume",
      button: "Verificați",
      empty: "Introduceți denumirea, IDNO sau numele.",
      loading: "Se efectuează căutarea. Vă rugăm să așteptați.",
      found: "Înregistrare demonstrativă găsită",
      open: "Vedeți raportul demonstrativ",
      company: "Companie",
      person: "Persoană",
      demo: "Date demonstrative",
    },
    proof: [
      ["Căutare", "Companii și persoane după denumire, IDNO sau nume."],
      ["Raport", "Date disponibile structurate pentru PDF și Excel."],
      ["Control", "Monitorizarea companiilor și a schimbărilor."],
      ["Moldova", "Surse disponibile pentru Republica Moldova."],
    ],
    story: {
      eyebrow: "De la solicitare la decizie",
      title: "O verificare. O imagine coerentă.",
      intro: "Credibil transformă înregistrările disponibile într-un traseu clar de verificare.",
      steps: [
        ["Identificați înregistrarea corectă", "Denumirea, IDNO, statutul și data înregistrării vă ajută să lucrați cu entitatea potrivită.", "identity"],
        ["Vedeți cine conduce și cine deține", "Profilul reunește administratorii, fondatorii, rolurile și cotele disponibile.", "owners"],
        ["Analizați legăturile corporative", "Persoanele asociate conduc către alte organizații, cu roluri și statute vizibile în același context.", "connections"],
        ["Observați datele care necesită atenție", "Evenimentele și celelalte secțiuni disponibile sunt prezentate cu sursa și actualitatea lor.", "attention"],
        ["Înțelegeți ce s-a schimbat", "Cronologia grupează modificările disponibile și păstrează contextul fiecărui eveniment.", "history"],
        ["Transformați datele într-un rezultat", "Exportați datele disponibile sau adăugați înregistrarea la monitorizare pentru verificări ulterioare.", "report"],
      ],
      ui: ["Înregistrare selectată", "Statut activ", "Identificator", "Data înregistrării", "Administrator", "Fondator", "Persoană asociată", "Înregistrare asociată", "Necesită atenție", "Verificare finalizată", "Cronologia modificărilor", "Raport structurat"],
    },
    product: {
      eyebrow: "Produs funcțional",
      title: "Nu promisiuni. Interfața reală.",
      text: "Utilizați registrul companiilor, profilurile detaliate, exportul rapoartelor și monitorizarea schimbărilor. Interfața prezintă scenarii reale disponibile în Credibil.",
      cards: [
        ["Căutare", "Sugestii separate pentru companii și persoane asociate.", "search", "large"],
        ["Profil", "Statut, identificator, adresă și date de înregistrare.", "profile", ""],
        ["Proprietari și legături", "Roluri, cote disponibile și înregistrări asociate.", "connections", "wide"],
        ["Factori de atenție", "Evenimente disponibile, prezentate cu context.", "attention", ""],
        ["Monitorizare", "O singură listă pentru schimbările importante.", "monitoring", "green"],
        ["Rapoarte", "Export structurat în PDF și XLSX.", "reports", ""],
      ],
    },
    connections: {
      eyebrow: "Legături corporative",
      title: "Priviți dincolo de o singură companie.",
      text: "Analizați persoanele și organizațiile asociate, rolurile acestora, cotele de participare și statutul companiilor.",
      points: ["Fondatori și administratori", "Companii asociate și roluri", "Organizații active sau lichidate"],
      cta: "Analizați legăturile",
      alt: "Lista persoanelor și companiilor asociate, cu roluri, cote de participare și statut activ sau lichidat.",
      preview: "Raport demonstrativ", selected: "Înregistrare selectată", active: "Activă",
      checks: [
        ["Înregistrare și statut", "Identificator, adresă, formă și clasificare", [["Identificator", "Date disponibile"], ["Statut", "Activ"], ["Adresă", "Înregistrare disponibilă"]]],
        ["Proprietari și conducere", "Fondatori, cote și administratori", [["Administrator", "Persoană asociată A"], ["Fondator", "Persoană asociată B"], ["Cotă", "Valoare disponibilă"]]],
        ["Legături corporative", "Roluri și înregistrări asociate", [["Legătură directă", "Înregistrare asociată A"], ["Rol", "Administrator"], ["Statut", "Activ"]]],
        ["Evenimente și atenție", "Schimbări și factori disponibili", [["Eveniment", "Necesită atenție"], ["Verificare", "Finalizată"], ["Context", "Sursă disponibilă"]]],
        ["Surse și actualitate", "Data și starea verificării", [["Sursă", "Registru disponibil"], ["Actualitate", "Data verificării"], ["Stare", "Date structurate"]]],
      ],
    },
    monitoring: {
      eyebrow: "Monitorizare continuă",
      title: "Verificare astăzi. Control mâine.",
      text: "Adăugați o companie la monitorizare și primiți notificări atunci când sistemul identifică schimbări în datele disponibile.",
      cta: "Adăugați la monitorizare",
      events: [
        ["Necesită atenție", "Administrator schimbat", "Valoarea anterioară și cea nouă sunt păstrate în eveniment."],
        ["Schimbare informativă", "Adresă juridică actualizată", "Data schimbării și sursa sunt disponibile în profil."],
        ["Actualizare date", "Date fiscale verificate", "Sistemul păstrează data ultimei verificări."],
      ],
      alt: "Secțiunea de monitorizare Credibil cu lista companiilor urmărite și zona notificărilor despre schimbări.",
    },
    reports: {
      eyebrow: "Rezultatul verificării",
      title: "Exportați rezultatul verificării.",
      text: "Generați un raport structurat pentru compania selectată și exportați datele disponibile în PDF sau Excel pentru analiză internă, aprobare și arhivare.",
      pdf: "Un document lizibil pentru verificarea la o anumită dată.",
      xlsx: "Date structurate pentru filtrare și analiză ulterioară.",
      stepsTitle: "Verificare în trei pași",
      steps: ["Găsiți compania sau persoana.", "Analizați datele și legăturile.", "Descărcați raportul sau activați monitorizarea."],
    },
    final: {
      eyebrow: "Următoarea decizie începe cu datele",
      title: "Verificați datele înaintea următoarei decizii.",
      text: "Găsiți partenerul, analizați datele disponibile și păstrați rezultatul într-un raport.",
      report: "Vedeți structura raportului",
    },
    footer: {
      text: "Credibil - serviciu pentru verificarea partenerilor din Moldova.",
      product: "Produs",
      info: "Informații",
      links: ["Contacte", "Politica de confidențialitate", "Condiții de utilizare"],
      note: "Prototip demonstrativ. Disponibilitatea datelor depinde de sursele conectate.",
    },
    modal: {
      title: "Mod demonstrativ",
      text: "Autentificarea și datele reale vor fi conectate după confirmarea adreselor de producție.",
      close: "Închideți",
    },
  },
  ru: {
    lang: "RU",
    altLang: "RO",
    metaTitle: "Credibil - проверка компаний и контрагентов в Молдове",
    metaDescription: "Проверяйте компании и связанных лиц по названию, IDNO или ФИО. Изучайте сведения, связи, доступные риски, отчёты и изменения в Молдове.",
    ogTitle: "Credibil - данные для проверки контрагентов в Молдове",
    ogDescription: "Найдите компанию или лицо, изучите регистрационные сведения и связи, сформируйте отчёт или включите мониторинг.",
    skip: "Перейти к содержанию",
    nav: [["Продукт", "product"], ["Связи", "connections"], ["Мониторинг", "monitoring"], ["Отчёты", "reports"]],
    login: "Войти",
    primary: "Начать проверку",
    hero: {
      eyebrow: "Проверка компаний и связанных лиц в Молдове",
      action: "Проверьте",
      words: ["статус", "владельцев", "связи", "риски"],
      h1: "Проверяйте контрагентов в Молдове до принятия решения",
      lead: "Найдите компанию или связанное лицо по названию, IDNO или ФИО. Изучите регистрационные сведения, связи и доступные факторы риска.",
      proof: ["Регистрационные сведения", "Связанные лица", "События", "Мониторинг"],
    },
    search: {
      label: "Название, IDNO или ФИО", button: "Проверить", empty: "Введите название, IDNO или ФИО.",
      loading: "Идёт поиск. Пожалуйста, подождите.", found: "Демонстрационная запись найдена", open: "Посмотреть демо-отчёт",
      company: "Компания", person: "Лицо", demo: "Демонстрационные данные",
    },
    proof: [
      ["Поиск", "Компании и лица по названию, IDNO или ФИО."], ["Отчёт", "Доступные данные в PDF и Excel."],
      ["Контроль", "Мониторинг компаний и изменений."], ["Молдова", "Доступные источники по Республике Молдова."],
    ],
    story: {
      eyebrow: "От запроса к решению", title: "Одна проверка. Единая картина.",
      intro: "Credibil превращает доступные записи в понятный сценарий проверки.",
      steps: [
        ["Найдите точную запись", "Название, IDNO, статус и дата регистрации помогают выбрать нужную запись.", "identity"],
        ["Узнайте, кто управляет и владеет", "Карточка объединяет администраторов, учредителей, роли и доступные доли.", "owners"],
        ["Изучите корпоративные связи", "Связанные лица приводят к другим записям, их ролям и статусам.", "connections"],
        ["Заметьте факторы внимания", "События и другие доступные разделы показываются с источником и актуальностью.", "attention"],
        ["Поймите, что изменилось", "Хронология объединяет доступные изменения и сохраняет контекст каждого события.", "history"],
        ["Соберите данные в результат", "Экспортируйте доступные сведения или добавьте запись в мониторинг.", "report"],
      ],
      ui: ["Выбранная запись", "Активный статус", "Идентификатор", "Дата регистрации", "Администратор", "Учредитель", "Связанное лицо", "Связанная запись", "Требует внимания", "Проверка завершена", "Хронология изменений", "Структурированный отчёт"],
    },
    product: {
      eyebrow: "Рабочий продукт", title: "Не обещания. Реальный интерфейс.",
      text: "Используйте реестр компаний, детальные карточки, экспорт отчётов и мониторинг изменений. Здесь показаны реальные сценарии Credibil.",
      cards: [
        ["Поиск", "Раздельные подсказки для компаний и связанных лиц.", "search", "large"],
        ["Карточка", "Статус, идентификатор, адрес и регистрационные сведения.", "profile", ""],
        ["Владельцы и связи", "Роли, доступные доли и связанные записи.", "connections", "wide"],
        ["Факторы внимания", "Доступные события с понятным контекстом.", "attention", ""],
        ["Мониторинг", "Единая лента значимых изменений.", "monitoring", "green"],
        ["Отчёты", "Структурированный экспорт в PDF и XLSX.", "reports", ""],
      ],
    },
    connections: {
      eyebrow: "Корпоративные связи", title: "Смотрите дальше одной компании.",
      text: "Изучайте связанных лиц и организации, их роли, доли владения и статусы компаний.",
      points: ["Учредители и администраторы", "Связанные компании и роли", "Активные и ликвидированные организации"],
      cta: "Изучить связи", alt: "Список связанных лиц и компаний с ролями, долями владения и статусами организаций.",
      preview: "Демонстрационный отчёт", selected: "Выбранная запись", active: "Активна",
      checks: [
        ["Регистрация и статус", "Идентификатор, адрес, форма и классификация", [["Идентификатор", "Данные доступны"], ["Статус", "Активна"], ["Адрес", "Запись доступна"]]],
        ["Владельцы и руководство", "Учредители, доли и администраторы", [["Администратор", "Связанное лицо A"], ["Учредитель", "Связанное лицо B"], ["Доля", "Значение доступно"]]],
        ["Корпоративные связи", "Роли и связанные записи", [["Прямая связь", "Связанная запись A"], ["Роль", "Администратор"], ["Статус", "Активна"]]],
        ["События и внимание", "Изменения и доступные факторы", [["Событие", "Требует внимания"], ["Проверка", "Завершена"], ["Контекст", "Источник доступен"]]],
        ["Источники и актуальность", "Дата и состояние проверки", [["Источник", "Доступный реестр"], ["Актуальность", "Дата проверки"], ["Состояние", "Данные структурированы"]]],
      ],
    },
    monitoring: {
      eyebrow: "Постоянное наблюдение", title: "Проверка сегодня. Контроль завтра.",
      text: "Добавьте компанию в мониторинг и получайте уведомления, когда система фиксирует изменения в доступных данных.",
      cta: "Добавить в мониторинг",
      events: [
        ["Требует внимания", "Изменён администратор", "Старое и новое значение фиксируются в событии."],
        ["Информационное изменение", "Обновлён юридический адрес", "Дата изменения и источник доступны в карточке."],
        ["Обновление данных", "Налоговые сведения проверены", "Система сохраняет дату последней проверки."],
      ],
      alt: "Раздел мониторинга Credibil со списком компаний и уведомлениями об изменениях.",
    },
    reports: {
      eyebrow: "Результат проверки", title: "Экспортируйте результат проверки.",
      text: "Сформируйте структурированный отчёт и экспортируйте доступные данные в PDF или Excel для анализа, согласования и хранения.",
      pdf: "Читаемый документ с результатом проверки на выбранную дату.",
      xlsx: "Структурированные данные для фильтрации и анализа.",
      stepsTitle: "Проверка в три шага",
      steps: ["Найдите компанию или лицо.", "Изучите сведения и связи.", "Скачайте отчёт или включите мониторинг."],
    },
    final: {
      eyebrow: "Следующее решение начинается с данных", title: "Проверьте данные до следующего решения.",
      text: "Найдите контрагента, изучите доступные сведения и зафиксируйте результат в отчёте.",
      report: "Посмотреть структуру отчёта",
    },
    footer: {
      text: "Credibil - сервис проверки контрагентов в Молдове.", product: "Продукт", info: "Информация",
      links: ["Контакты", "Политика конфиденциальности", "Условия использования"],
      note: "Демонстрационный прототип. Доступность данных зависит от подключённых источников.",
    },
    modal: {
      title: "Демонстрационный режим",
      text: "Авторизация и реальные данные будут подключены после подтверждения production-адресов.",
      close: "Закрыть",
    },
  },
};

const suggestions = {
  ro: [
    { name: "Înregistrare companie A", meta: "Identificator demonstrativ", type: "company" },
    { name: "Înregistrare companie B", meta: "Date demonstrative", type: "company" },
    { name: "Persoană asociată A", meta: "Rol demonstrativ", type: "person" },
  ],
  ru: [
    { name: "Запись компании A", meta: "Демонстрационный идентификатор", type: "company" },
    { name: "Запись компании B", meta: "Демонстрационные данные", type: "company" },
    { name: "Связанное лицо A", meta: "Демонстрационная роль", type: "person" },
  ],
};

function getFinalBase() {
  const path = window.location.pathname;
  if (window.location.protocol === "file:") return /\/ru(?:\/|$)/.test(path) ? ".." : ".";
  if (path.startsWith("/final")) return "/final";
  if (path.includes("/credibil/credibil-final-heroes")) return "/credibil/credibil-final-heroes";
  return ".";
}

function asset(name, fullLanding = true) {
  const embedded = window.__CREDIBIL_ASSETS__?.[name];
  if (embedded) return embedded;
  if (fullLanding) return `${getFinalBase()}/assets/${name}`;
  return `./assets/${name}`;
}

function ensureMeta(selector, property, value) {
  let element = document.head.querySelector(selector);
  if (!element) {
    element = document.createElement("meta");
    const [key, attrValue] = property;
    element.setAttribute(key, attrValue);
    document.head.append(element);
  }
  element.setAttribute("content", value);
}

function useLocale() {
  const getLocale = () => /\/ru(?:\/|$)/.test(window.location.pathname) ? "ru" : "ro";
  const [locale, setLocale] = useState(getLocale);
  useEffect(() => {
    const onPopState = () => setLocale(getLocale());
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);
  const changeLocale = () => {
    const next = locale === "ro" ? "ru" : "ro";
    if (window.location.protocol === "file:") {
      window.location.assign(next === "ro" ? "../index.html" : "./ru/index.html");
      return;
    }
    const base = getFinalBase();
    const nextPath = next === "ro" ? `${base}/` : `${base}/ru/`;
    window.history.pushState({}, "", nextPath);
    setLocale(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  return [locale, changeLocale];
}

function useReveal() {
  useEffect(() => {
    const nodes = [...document.querySelectorAll("[data-reveal]")];
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      nodes.forEach((node) => node.classList.add("is-visible"));
      return undefined;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.16 });
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  });
}

function DataField({ active = false, mode = 2, alt, fullLanding = true }) {
  const canvasRef = useRef(null);
  const pointer = useRef({ x: -999, y: -999, inside: false });
  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const points = Array.from({ length: mode === 1 ? 115 : 155 }, (_, index) => ({
      x: ((index * 73) % 997) / 997, y: ((index * 181 + 37) % 991) / 991,
      size: index % 19 === 0 ? 2.8 : index % 7 === 0 ? 1.8 : 1.05, phase: index * 0.61,
    }));
    let frame = 0, last = 0;
    const resize = () => {
      const box = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 1.25);
      canvas.width = Math.max(1, Math.round(box.width * ratio));
      canvas.height = Math.max(1, Math.round(box.height * ratio));
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
    };
    const draw = (now = 0) => {
      const width = canvas.clientWidth, height = canvas.clientHeight, time = now / 1000;
      context.clearRect(0, 0, width, height);
      points.forEach((point) => {
        const x = point.x * width, y = point.y * height;
        const distance = Math.hypot(x - pointer.current.x, y - pointer.current.y);
        const near = pointer.current.inside ? Math.max(0, 1 - distance / 140) : 0;
        const pulse = reduceMotion ? .55 : .55 + .45 * Math.sin(time * .72 + point.phase);
        context.beginPath();
        context.arc(x, y, point.size * (1 + near * .7 + (active ? .2 : 0)), 0, Math.PI * 2);
        context.fillStyle = `rgba(104,226,177,${.22 + pulse * .58 + near * .2})`;
        context.fill();
      });
      if (!reduceMotion) {
        const scanY = (((time * (active ? 1.7 : 1)) % 10.5) / 10.5) * height;
        const scan = context.createLinearGradient(0, scanY - 70, 0, scanY + 70);
        scan.addColorStop(0, "rgba(97,210,162,0)");
        scan.addColorStop(.5, "rgba(97,210,162,.34)");
        scan.addColorStop(1, "rgba(97,210,162,0)");
        context.fillStyle = scan;
        context.fillRect(0, scanY - 70, width, 140);
      }
    };
    const loop = (now) => {
      frame = requestAnimationFrame(loop);
      if (document.hidden || now - last < 32) return;
      last = now;
      draw(now);
    };
    resize();
    if (reduceMotion) draw(0); else frame = requestAnimationFrame(loop);
    window.addEventListener("resize", resize, { passive: true });
    return () => { cancelAnimationFrame(frame); window.removeEventListener("resize", resize); };
  }, [active, mode]);
  return <div className={`map-field map-field-${mode} ${active ? "is-active" : ""}`}
    style={{ "--map-mask": `url("${asset("moldova-mask.svg", fullLanding)}")` }}
    onPointerMove={(event) => { const box = event.currentTarget.getBoundingClientRect(); pointer.current = { x: event.clientX - box.left, y: event.clientY - box.top, inside: true }; }}
    onPointerLeave={() => { pointer.current.inside = false; }}>
    <img src={asset("moldova-regions.svg", fullLanding)} alt={alt} />
    <canvas ref={canvasRef} aria-hidden="true" />
  </div>;
}

function DemoSearch({ text, items = suggestions.ru, onActiveChange = () => {}, id = "hero-search" }) {
  const [query, setQuery] = useState("");
  const [state, setState] = useState("idle");
  const filtered = useMemo(() => {
    if (!query.trim()) return items;
    const value = query.toLocaleLowerCase();
    return items.filter((item) => `${item.name} ${item.meta}`.toLocaleLowerCase().includes(value));
  }, [items, query]);
  const select = (item) => { setQuery(item.name); setState("ready"); };
  const submit = (event) => {
    event.preventDefault();
    if (!query.trim()) { setState("empty"); event.currentTarget.querySelector("input")?.focus(); return; }
    setState("loading"); onActiveChange(true);
    window.setTimeout(() => { setState("done"); onActiveChange(false); }, 900);
  };
  const showSuggestions = query && !["loading", "done"].includes(state);
  return <div className="search-block">
    <form className={`search-form ${state}`} onSubmit={submit} role="search">
      <label className="sr-only" htmlFor={id}>{text.label}</label>
      <input id={id} value={query} onChange={(event) => { setQuery(event.target.value); setState("typing"); }}
        onFocus={() => setState((value) => value === "idle" ? "typing" : value)}
        placeholder={text.label} autoComplete="off" aria-expanded={Boolean(showSuggestions)} aria-controls={`${id}-suggestions`} />
      <button type="submit">{text.button}</button>
      {showSuggestions && <div className="search-suggestions" id={`${id}-suggestions`} role="listbox">
        <span className="suggestion-title">{text.demo}</span>
        {filtered.length ? filtered.map((item) => <button key={item.name} type="button" role="option" onClick={() => select(item)}>
          <span className="suggestion-mark">{item.type === "company" ? "C" : "P"}</span>
          <span><strong>{item.name}</strong><small>{item.meta}</small></span>
          <em>{item.type === "company" ? text.company : text.person}</em>
        </button>) : <p className="no-suggestion">{text.empty}</p>}
      </div>}
    </form>
    <div className={`search-state ${state}`} aria-live="polite">
      {state === "empty" && text.empty}
      {state === "loading" && text.loading}
      {state === "done" && <><b>{query}</b><span>{text.found}</span><a href="#reports">{text.open}</a></>}
    </div>
  </div>;
}

function Header({ text, onLocale, onLogin }) {
  const [menu, setMenu] = useState(false);
  return <header className="site-header">
    <a className="brand" href="#top" aria-label="Credibil"><img src={asset("credibil-logo.svg")} alt="Credibil" /></a>
    <nav aria-label="Primary navigation">{text.nav.map(([label, target]) => <a key={target} href={`#${target}`}>{label}</a>)}</nav>
    <div className="header-actions">
      <button className="language" type="button" onClick={onLocale} aria-label={`Switch to ${text.altLang}`}>{text.lang}<span>{text.altLang}</span></button>
      <button className="login" type="button" onClick={onLogin}>{text.login}</button>
      <a className="header-cta" href="#final-search">{text.primary}</a>
      <button className="menu-toggle" type="button" aria-expanded={menu} aria-controls="mobile-nav" onClick={() => setMenu(!menu)}>
        <span /><span /><span className="sr-only">Menu</span>
      </button>
    </div>
    <div className="mobile-nav" id="mobile-nav" hidden={!menu}>
      {text.nav.map(([label, target]) => <a key={target} href={`#${target}`} onClick={() => setMenu(false)}>{label}</a>)}
      <button type="button" onClick={onLogin}>{text.login}</button>
    </div>
  </header>;
}

function StoryStage({ type, labels }) {
  const [selected, active, id, date, admin, founder, person, linked, attention, complete, history, report] = labels;
  if (type === "identity") return <div className="story-ui story-identity" aria-hidden="true">
    <div className="ui-toolbar"><span>{selected}</span><b>{active}</b></div>
    <div className="ui-entity"><small>{selected}</small><strong>••••••••••</strong></div>
    <div className="ui-data-grid"><div><span>{id}</span><b>••••••••</b></div><div><span>{date}</span><b>•• / •• / ••••</b></div></div>
    <div className="ui-lines"><i /><i /><i /></div>
  </div>;
  if (type === "owners") return <div className="story-ui story-network" aria-hidden="true">
    <div className="network-core"><small>{selected}</small><strong>••••••••</strong></div>
    <div className="network-card owner-card-a"><small>{admin}</small><strong>{person} A</strong></div>
    <div className="network-card owner-card-b"><small>{founder}</small><strong>{person} B</strong></div>
    <i className="network-rule rule-a" /><i className="network-rule rule-b" />
  </div>;
  if (type === "connections") return <div className="story-ui story-network expanded" aria-hidden="true">
    <div className="network-core"><small>{selected}</small><strong>••••••••</strong></div>
    {["A", "B", "C", "D"].map((key, index) => <div key={key} className={`network-card link-card link-${index + 1}`}><small>{index < 2 ? person : linked}</small><strong>{index < 2 ? `${person} ${key}` : `${linked} ${key}`}</strong></div>)}
  </div>;
  if (type === "attention") return <div className="story-ui story-events" aria-hidden="true">
    <div className="ui-toolbar"><span>{attention}</span><b>{complete}</b></div>
    {[attention, complete, complete].map((item, index) => <div className="event-row" key={`${item}-${index}`}><i className={index === 0 ? "warn" : "ok"} /><div><small>0{index + 1}</small><strong>{item}</strong></div><span>•• / •• / ••••</span></div>)}
  </div>;
  if (type === "history") return <div className="story-ui story-history" aria-hidden="true">
    <div className="ui-toolbar"><span>{history}</span><b>03</b></div>
    {[complete, attention, selected].map((item, index) => <div className="history-row" key={`${item}-${index}`}><time>0{index + 1}</time><i /><div><strong>{item}</strong><span>••••••••••••••</span></div></div>)}
  </div>;
  return <div className="story-ui story-report" aria-hidden="true">
    <div className="report-card report-card-pdf"><span>PDF</span><small>Credibil</small><strong>{report}</strong><i /><i /><i /></div>
    <div className="report-card report-card-xlsx"><span>XLSX</span><small>Credibil</small><strong>{report}</strong><div className="sheet-cells">{Array.from({ length: 20 }, (_, index) => <i key={index} />)}</div></div>
  </div>;
}

function Story({ text }) {
  const sectionRef = useRef(null);
  const [active, setActive] = useState(0);
  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      if (!sectionRef.current || window.innerWidth < 900) return;
      const rect = sectionRef.current.getBoundingClientRect();
      const distance = Math.max(1, sectionRef.current.offsetHeight - window.innerHeight);
      const progress = Math.min(1, Math.max(0, -rect.top / distance));
      setActive(Math.min(text.steps.length - 1, Math.floor(progress * text.steps.length)));
    };
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(update); };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => { cancelAnimationFrame(frame); window.removeEventListener("scroll", onScroll); window.removeEventListener("resize", onScroll); };
  }, [text.steps.length]);
  return <section className="story" ref={sectionRef} id="story">
    <div className="story-sticky">
      <div className="story-heading">
        <p className="eyebrow">{text.eyebrow}</p><h2>{text.title}</h2><p>{text.intro}</p>
        <div className="story-progress" aria-hidden="true"><span>{String(active + 1).padStart(2, "0")}</span><i><b style={{ height: `${((active + 1) / text.steps.length) * 100}%` }} /></i><span>{String(text.steps.length).padStart(2, "0")}</span></div>
      </div>
      <div className="story-copy">
        {text.steps.map((step, index) => <article key={step[0]} className={index === active ? "active" : ""} aria-hidden={index !== active}>
          <span>{String(index + 1).padStart(2, "0")}</span><h3>{step[0]}</h3><p>{step[1]}</p>
        </article>)}
      </div>
      <div className="story-visual">
        {text.steps.map((step, index) => <figure key={step[2]} className={index === active ? "active" : ""}>
          <div className="browser-bar"><span /><span /><span /><small>app.credibil.md</small></div>
          <StoryStage type={step[2]} labels={text.ui} />
        </figure>)}
      </div>
    </div>
    <div className="story-mobile">
      {text.steps.map((step, index) => <article key={step[0]} data-reveal>
        <span>{String(index + 1).padStart(2, "0")}</span><h3>{step[0]}</h3><p>{step[1]}</p><div className="story-mobile-stage"><StoryStage type={step[2]} labels={text.ui} /></div>
      </article>)}
    </div>
  </section>;
}

const productIcons = {
  search: MagnifyingGlass, profile: IdentificationCard, connections: ShareNetwork,
  attention: ShieldWarning, monitoring: BellRinging, reports: FileText,
};

function ProductShowcase({ text }) {
  return <section className="product-section" id="product">
    <div className="section-shell product-layout">
      <div className="section-copy product-heading" data-reveal><p className="eyebrow">{text.eyebrow}</p><h2>{text.title}</h2><p>{text.text}</p></div>
      <div className="product-bento">{text.cards.map((card, index) => {
        const Icon = productIcons[card[2]];
        return <article key={card[0]} className={`product-tile ${card[3] ? `tile-${card[3]}` : ""}`} data-reveal>
          <Icon size={29} weight="regular" aria-hidden="true" /><span>{String(index + 1).padStart(2, "0")}</span><h3>{card[0]}</h3><p>{card[1]}</p>
        </article>;
      })}</div>
    </div>
  </section>;
}

function Checks({ text }) {
  const [active, setActive] = useState(0);
  const current = text.checks[active];
  const onKeyDown = (event) => {
    if (!["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) return;
    event.preventDefault();
    const direction = ["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1;
    setActive((value) => (value + direction + text.checks.length) % text.checks.length);
  };
  return <section className="connections-section" id="connections"><div className="section-shell">
    <div className="connections-heading" data-reveal><div className="dark-copy"><p className="eyebrow">{text.eyebrow}</p><h2>{text.title}</h2></div><p>{text.text}</p></div>
    <div className="checks-layout">
      <div className="checks-index" role="tablist" onKeyDown={onKeyDown}>{text.checks.map((check, index) => <button key={check[0]} type="button" role="tab" aria-selected={index === active} onClick={() => setActive(index)}><span>{String(index + 1).padStart(2, "0")}</span><b>{check[0]}</b><em>{check[1]}</em></button>)}</div>
      <div className="check-preview" data-reveal>
        <div className="preview-toolbar"><span>{text.preview}</span><small>Credibil</small></div>
        <div className="preview-entity"><div><small>{text.selected}</small><strong>••••••••••</strong></div><b>{text.active}</b></div>
        <div className="preview-content" key={current[0]}>{current[2].map(([label, value]) => <div className="preview-row" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
      </div>
    </div>
  </div></section>;
}

function Modal({ text, onClose }) {
  const closeRef = useRef(null);
  useEffect(() => { closeRef.current?.focus(); const onKey = (event) => event.key === "Escape" && onClose(); window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey); }, [onClose]);
  return <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><p className="eyebrow">Credibil</p><h2 id="modal-title">{text.title}</h2><p>{text.text}</p><button ref={closeRef} type="button" onClick={onClose}>{text.close}</button></div>
  </div>;
}

function Landing() {
  const [locale, changeLocale] = useLocale();
  const [word, setWord] = useState(0);
  const [searchActive, setSearchActive] = useState(false);
  const [modal, setModal] = useState(false);
  const text = copy[locale];
  useReveal();
  useEffect(() => {
    document.documentElement.lang = locale;
    document.title = text.metaTitle;
    ensureMeta('meta[name="description"]', ["name", "description"], text.metaDescription);
    ensureMeta('meta[property="og:title"]', ["property", "og:title"], text.ogTitle);
    ensureMeta('meta[property="og:description"]', ["property", "og:description"], text.ogDescription);
  }, [locale, text]);
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return undefined;
    const timer = window.setInterval(() => setWord((value) => (value + 1) % text.hero.words.length), 2200);
    return () => window.clearInterval(timer);
  }, [text.hero.words.length, locale]);
  return <div className="landing">
    <a className="skip-link" href="#main">{text.skip}</a>
    <Header text={text} onLocale={changeLocale} onLogin={() => setModal(true)} />
    <main id="main">
      <section className="hero" id="top">
        <div className="hero-grid" aria-hidden="true" />
        <DataField active={searchActive} alt={locale === "ro" ? "Harta Republicii Moldova" : "Карта Республики Молдова"} />
        <div className="hero-content">
          <p className="eyebrow">{text.hero.eyebrow}</p>
          <h1 className="kinetic-title" aria-label={text.hero.h1}><span aria-hidden="true">{text.hero.action}</span></h1>
          <div className="word-window" aria-hidden="true">{text.hero.words.map((item, index) => {
            const offset = (index - word + text.hero.words.length) % text.hero.words.length;
            return <span key={item} className={offset === 0 ? "active" : offset === 1 ? "next" : offset === text.hero.words.length - 1 ? "previous" : "hidden"}>{item}</span>;
          })}</div>
          <p className="hero-lead">{text.hero.lead}</p>
          <DemoSearch text={text.search} items={suggestions[locale]} onActiveChange={setSearchActive} />
          <div className="hero-proof">{text.hero.proof.map((item) => <span key={item}>{item}</span>)}</div>
        </div>
      </section>

      <section className="proof-strip" aria-label="Credibil"><div className="section-shell proof-grid">
        {text.proof.map(([title, body], index) => <article key={title} data-reveal><span>{String(index + 1).padStart(2, "0")}</span><h2>{title}</h2><p>{body}</p></article>)}
      </div></section>

      <Story text={text.story} />
      <ProductShowcase text={text.product} />
      <Checks text={text.connections} />

      <section className="monitoring-section" id="monitoring"><div className="section-shell monitoring-layout">
        <div className="section-copy" data-reveal><p className="eyebrow">{text.monitoring.eyebrow}</p><h2>{text.monitoring.title}</h2><p>{text.monitoring.text}</p><button className="primary-button" type="button" onClick={() => setModal(true)}>{text.monitoring.cta}</button></div>
        <div className="event-feed" data-reveal><i className="event-line" aria-hidden="true" />{text.monitoring.events.map((event, index) => <article key={event[1]}><time>{["14:32", "11:08", "09:15"][index]}</time><i className={`event-dot dot-${index}`} aria-hidden="true" /><div><span>{event[0]}</span><h3>{event[1]}</h3><p>{event[2]}</p></div></article>)}</div>
      </div></section>

      <section className="reports-section" id="reports"><div className="section-shell reports-layout">
        <div className="report-stack" data-reveal aria-hidden="true"><div className="report-sheet sheet-back" /><div className="report-sheet sheet-middle" /><div className="report-sheet sheet-front"><div className="report-sheet-head"><span>Credibil</span><b>REPORT</b></div><strong>••••••••••••</strong><small>•••••••• / ••••••••</small><em>{text.reports.eyebrow}</em><div className="report-bars"><i /><i /><i /><i /><i /></div><div className="report-copy-lines"><span /><span /><span /><span /></div><b className="format-badge badge-pdf">PDF</b><b className="format-badge badge-xlsx">XLSX</b></div></div>
        <div className="section-copy dark-copy reports-copy" data-reveal><p className="eyebrow">{text.reports.eyebrow}</p><h2>{text.reports.title}</h2><p>{text.reports.text}</p><div className="report-options"><div><strong>PDF</strong><span>{text.reports.pdf}</span></div><div><strong>XLSX</strong><span>{text.reports.xlsx}</span></div></div></div>
      </div></section>

      <section className="final-section" id="final-search"><div className="section-shell final-layout">
        <div data-reveal><p className="eyebrow">{text.final.eyebrow}</p><h2>{text.final.title}</h2><p>{text.final.text}</p></div>
        <div data-reveal><DemoSearch text={text.search} items={suggestions[locale]} id="final-company-search" /><a className="final-report-link" href="#reports">{text.final.report}</a></div>
      </div></section>
    </main>
    <footer><div className="section-shell footer-grid"><div><img src={asset("credibil-logo.svg")} alt="Credibil" /><p>{text.footer.text}</p></div><div><strong>{text.footer.product}</strong>{text.nav.map(([label, target]) => <a key={target} href={`#${target}`}>{label}</a>)}</div><div><strong>{text.footer.info}</strong>{text.footer.links.map((item) => <button key={item} type="button" onClick={() => setModal(true)}>{item}</button>)}</div></div><div className="section-shell footer-note"><span>© 2026 Credibil</span><span>{text.footer.note}</span></div></footer>
    {modal && <Modal text={text.modal} onClose={() => setModal(false)} />}
  </div>;
}

function LegacyHeader({ second = false }) {
  return <header className="legacy-header"><a className="brand" href="#top"><img src={asset("credibil-logo.svg", false)} alt="Credibil" /></a><nav><a href="#capabilities">Возможности</a><a href="#monitoring">Мониторинг</a><a href="#pricing">Тарифы</a></nav><a className="login" href="#login">Войти</a>{second && <a className="header-cta" href="#contact">Связаться с нами</a>}</header>;
}

function LegacyHero({ second = false }) {
  const [active, setActive] = useState(false), [word, setWord] = useState(0);
  useEffect(() => { if (!second) return undefined; const timer = window.setInterval(() => setWord((value) => (value + 1) % legacyWords.length), 2200); return () => window.clearInterval(timer); }, [second]);
  return <main className={`legacy-page ${second ? "legacy-two" : "legacy-one"}`} id="top"><LegacyHeader second={second} /><section className="legacy-layout"><DataField active={active} mode={second ? 2 : 1} fullLanding={false} alt="Карта Республики Молдова" /><div className="legacy-copy">
    <p className="eyebrow">{second ? "Credibil · единая картина бизнеса" : "Проверка контрагентов в Молдове"}</p>
    {second ? <><div className="legacy-kinetic"><h1>Проверьте</h1><div className="word-window">{legacyWords.map((item, index) => { const offset = (index - word + legacyWords.length) % legacyWords.length; return <span key={item} className={offset === 0 ? "active" : offset === 1 ? "next" : offset === legacyWords.length - 1 ? "previous" : "hidden"}>{item}</span>; })}</div></div><p className="legacy-lead">До договора. До оплаты. До риска.</p></> : <><h1>Moldova в вашей <em>проверке.</em></h1><p className="legacy-lead">Проверьте контрагента до принятия решения</p></>}
    <DemoSearch text={copy.ru.search} items={suggestions.ru} onActiveChange={setActive} />
  </div></section></main>;
}

export function App() {
  const path = window.location.pathname;
  if (path.includes("final-2")) return <LegacyHero second />;
  if (path.includes("final-1")) return <LegacyHero />;
  return <Landing />;
}

