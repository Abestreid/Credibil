const ASSET_NAMES = [
  "credibil-logo.svg",
  "moldova-mask.svg",
  "moldova-regions.svg",
];

function deploymentBase(pathname = window.location.pathname) {
  if (pathname.includes("/credibil/dev/")) return "/credibil/dev";
  if (pathname === "/credibil/dev") return "/credibil/dev";
  if (pathname.includes("/credibil/")) return "/credibil";
  if (pathname === "/credibil") return "/credibil";
  if (pathname.includes("/final/")) return "/final";
  return "";
}

export function configureRuntimeAssets() {
  if (window.location.protocol === "file:") return;
  const base = deploymentBase();
  if (!base) return;

  window.__CREDIBIL_ASSETS__ = {
    ...(window.__CREDIBIL_ASSETS__ || {}),
    ...Object.fromEntries(ASSET_NAMES.map((name) => [name, `${base}/assets/${name}`])),
  };
}

function waitForLanding(maxFrames = 180) {
  return new Promise((resolve) => {
    let frames = 0;
    const check = () => {
      const landing = document.querySelector(".landing");
      if (landing || frames >= maxFrames) {
        resolve(landing);
        return;
      }
      frames += 1;
      window.requestAnimationFrame(check);
    };
    check();
  });
}

function waitForGsap(maxFrames = 180) {
  return new Promise((resolve) => {
    let frames = 0;
    const check = () => {
      if (window.gsap && window.ScrollTrigger) {
        resolve({ gsap: window.gsap, ScrollTrigger: window.ScrollTrigger });
        return;
      }
      if (frames >= maxFrames) {
        resolve(null);
        return;
      }
      frames += 1;
      window.requestAnimationFrame(check);
    };
    check();
  });
}

function animateStoryStage(gsap, figure) {
  if (!figure || figure.dataset.stageAnimated === "true") return;
  figure.dataset.stageAnimated = "true";

  const stage = figure.querySelector(".story-ui");
  if (!stage) return;

  const timeline = gsap.timeline({ defaults: { ease: "power3.out" } });
  timeline.fromTo(stage, { filter: "blur(7px)", scale: 0.985 }, { filter: "blur(0px)", scale: 1, duration: 0.48 }, 0);

  if (stage.classList.contains("story-identity")) {
    timeline
      .from(stage.querySelector(".ui-toolbar"), { y: -16, opacity: 0, duration: 0.34 }, 0.04)
      .from(stage.querySelector(".ui-entity"), { y: 24, opacity: 0, duration: 0.42 }, 0.12)
      .from(stage.querySelectorAll(".ui-data-grid > div"), { y: 18, opacity: 0, stagger: 0.08, duration: 0.36 }, 0.2)
      .from(stage.querySelectorAll(".ui-lines i"), { scaleX: 0, transformOrigin: "left center", stagger: 0.07, duration: 0.42 }, 0.28);
    return;
  }

  if (stage.classList.contains("story-network")) {
    timeline
      .from(stage.querySelector(".network-core"), { scale: 0.72, opacity: 0, duration: 0.46 }, 0.06)
      .from(stage.querySelectorAll(".network-rule"), { scaleX: 0, transformOrigin: "left center", stagger: 0.08, duration: 0.4 }, 0.16)
      .from(stage.querySelectorAll(".network-card"), { y: 22, scale: 0.9, opacity: 0, stagger: 0.08, duration: 0.42 }, 0.18);
    return;
  }

  if (stage.classList.contains("story-events")) {
    timeline
      .from(stage.querySelector(".ui-toolbar"), { y: -14, opacity: 0, duration: 0.32 }, 0.05)
      .from(stage.querySelectorAll(".event-row"), { x: 34, opacity: 0, stagger: 0.11, duration: 0.42 }, 0.14);
    return;
  }

  if (stage.classList.contains("story-history")) {
    timeline
      .from(stage.querySelector(".ui-toolbar"), { y: -14, opacity: 0, duration: 0.32 }, 0.05)
      .from(stage.querySelectorAll(".history-row"), { y: 22, opacity: 0, stagger: 0.12, duration: 0.42 }, 0.14)
      .from(stage.querySelectorAll(".history-row > i"), { scale: 0, stagger: 0.12, duration: 0.24 }, 0.2);
    return;
  }

  timeline
    .from(stage.querySelector(".report-card-pdf"), { xPercent: 28, rotate: 0, opacity: 0, duration: 0.55 }, 0.08)
    .from(stage.querySelector(".report-card-xlsx"), { xPercent: -28, rotate: 0, opacity: 0, duration: 0.55 }, 0.12)
    .from(stage.querySelectorAll(".sheet-cells i"), { scale: 0.4, opacity: 0, stagger: { amount: 0.35, grid: "auto", from: "start" }, duration: 0.22 }, 0.28);
}

function observeStoryStages(gsap, root) {
  const story = root.querySelector(".story");
  if (!story) return () => {};

  const animateActive = () => {
    story.querySelectorAll(".story-visual figure.active, .story-mobile article.is-visible .story-mobile-stage").forEach((node) => {
      const figure = node.matches("figure") ? node : node.closest("article")?.querySelector(".story-mobile-stage");
      animateStoryStage(gsap, figure || node);
    });
  };

  animateActive();
  const observer = new MutationObserver(animateActive);
  observer.observe(story, { subtree: true, attributes: true, attributeFilter: ["class"] });
  return () => observer.disconnect();
}

function setupDesktopStory(gsap, ScrollTrigger, root) {
  const story = root.querySelector(".story");
  if (!story) return;

  const progressBar = story.querySelector(".story-progress b");
  const visual = story.querySelector(".story-visual");
  const heading = story.querySelector(".story-heading");
  const copy = story.querySelector(".story-copy");

  gsap.set(progressBar, { height: "0%" });
  gsap.timeline({
    scrollTrigger: {
      trigger: story,
      start: "top top",
      end: "bottom bottom",
      scrub: 0.45,
      invalidateOnRefresh: true,
    },
  })
    .to(progressBar, { height: "100%", ease: "none", duration: 1 }, 0)
    .fromTo(visual, { yPercent: 2, rotateY: -1.2 }, { yPercent: -2, rotateY: 1.2, ease: "none", duration: 1 }, 0)
    .fromTo(heading, { yPercent: 4 }, { yPercent: -4, ease: "none", duration: 1 }, 0)
    .fromTo(copy, { yPercent: 3 }, { yPercent: -3, ease: "none", duration: 1 }, 0);
}

function setupMobileStory(gsap, ScrollTrigger, root) {
  root.querySelectorAll(".story-mobile article").forEach((card) => {
    const stage = card.querySelector(".story-mobile-stage");
    gsap.fromTo(card, { opacity: 0, y: 44 }, {
      opacity: 1,
      y: 0,
      duration: 0.75,
      ease: "power3.out",
      scrollTrigger: { trigger: card, start: "top 84%", once: true },
      onStart: () => animateStoryStage(gsap, stage),
    });
  });
}

function setupChecksStory(gsap, ScrollTrigger, root) {
  const section = root.querySelector(".connections-section");
  if (!section) return;
  const buttons = [...section.querySelectorAll(".checks-index button")];
  if (!buttons.length) return;

  let selected = -1;
  ScrollTrigger.create({
    trigger: section,
    start: "top 72%",
    end: "bottom 32%",
    scrub: true,
    onUpdate: ({ progress }) => {
      const next = Math.min(buttons.length - 1, Math.floor(progress * buttons.length));
      if (next === selected) return;
      selected = next;
      buttons[next]?.click();
    },
  });

  const preview = section.querySelector(".check-preview");
  if (preview) {
    const observer = new MutationObserver(() => {
      const rows = preview.querySelectorAll(".preview-row");
      gsap.fromTo(rows, { x: 24, opacity: 0 }, { x: 0, opacity: 1, stagger: 0.07, duration: 0.36, ease: "power2.out", overwrite: true });
    });
    observer.observe(preview, { childList: true, subtree: true });
    ScrollTrigger.create({ trigger: section, start: "top 80%", onLeaveBack: () => observer.disconnect() });
  }
}

function setupGlobalScenes(gsap, ScrollTrigger, root) {
  gsap.timeline({ defaults: { ease: "power3.out" } })
    .from(".site-header", { y: -28, opacity: 0, duration: 0.55 })
    .from(".hero-content > .eyebrow", { y: 22, opacity: 0, duration: 0.45 }, 0.08)
    .from(".kinetic-title", { y: 46, opacity: 0, duration: 0.68 }, 0.14)
    .from(".word-window", { y: 38, opacity: 0, clipPath: "inset(0 0 100% 0)", duration: 0.72 }, 0.2)
    .from(".hero-lead", { y: 24, opacity: 0, duration: 0.5 }, 0.34)
    .from(".hero .search-block", { y: 28, opacity: 0, duration: 0.55 }, 0.42)
    .from(".hero-proof span", { y: 12, opacity: 0, stagger: 0.06, duration: 0.32 }, 0.52)
    .from(".hero .map-field", { xPercent: 14, scale: 0.94, opacity: 0, duration: 1.05 }, 0.12);

  gsap.timeline({
    scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: 0.5 },
  })
    .to(".hero-content", { yPercent: -7, opacity: 0.72, ease: "none" }, 0)
    .to(".hero .map-field", { yPercent: 12, scale: 1.06, rotate: 1.3, ease: "none" }, 0)
    .to(".hero-grid", { yPercent: 8, opacity: 0.12, ease: "none" }, 0);

  gsap.from(".proof-grid article", {
    y: 54,
    opacity: 0,
    stagger: 0.12,
    duration: 0.72,
    ease: "power3.out",
    scrollTrigger: { trigger: ".proof-strip", start: "top 82%", once: true },
  });

  gsap.from(".product-heading > *", {
    y: 46,
    opacity: 0,
    stagger: 0.1,
    duration: 0.72,
    scrollTrigger: { trigger: ".product-section", start: "top 76%", once: true },
  });
  gsap.from(".product-tile", {
    y: 64,
    opacity: 0,
    rotateX: 4,
    stagger: { amount: 0.72, from: "start" },
    duration: 0.78,
    ease: "power3.out",
    scrollTrigger: { trigger: ".product-bento", start: "top 82%", once: true },
  });
  gsap.to(".product-tile > svg", {
    y: -5,
    rotate: 5,
    stagger: 0.08,
    duration: 1.6,
    ease: "sine.inOut",
    repeat: -1,
    yoyo: true,
  });

  gsap.from(".connections-heading > *", {
    y: 42,
    opacity: 0,
    stagger: 0.12,
    duration: 0.72,
    scrollTrigger: { trigger: ".connections-section", start: "top 78%", once: true },
  });
  gsap.from(".checks-index button", {
    x: -34,
    opacity: 0,
    stagger: 0.09,
    duration: 0.5,
    scrollTrigger: { trigger: ".checks-layout", start: "top 82%", once: true },
  });
  gsap.from(".check-preview", {
    x: 52,
    opacity: 0,
    rotateY: -3,
    duration: 0.82,
    ease: "power3.out",
    scrollTrigger: { trigger: ".checks-layout", start: "top 82%", once: true },
  });

  gsap.from(".monitoring-section .section-copy > *", {
    y: 42,
    opacity: 0,
    stagger: 0.1,
    duration: 0.68,
    scrollTrigger: { trigger: ".monitoring-section", start: "top 76%", once: true },
  });
  gsap.fromTo(".event-line", { scaleY: 0, transformOrigin: "top center" }, {
    scaleY: 1,
    ease: "none",
    scrollTrigger: { trigger: ".event-feed", start: "top 78%", end: "bottom 42%", scrub: 0.45 },
  });
  gsap.from(".event-feed article", {
    x: 54,
    opacity: 0,
    stagger: 0.15,
    duration: 0.68,
    scrollTrigger: { trigger: ".event-feed", start: "top 80%", once: true },
  });
  gsap.to(".event-dot", { scale: 1.25, duration: 0.85, stagger: 0.14, repeat: -1, yoyo: true, ease: "sine.inOut" });

  gsap.from(".report-stack", {
    y: 70,
    opacity: 0,
    duration: 0.9,
    scrollTrigger: { trigger: ".reports-section", start: "top 78%", once: true },
  });
  gsap.from(".sheet-back", {
    xPercent: 18,
    yPercent: 8,
    rotate: 0,
    duration: 0.9,
    ease: "power3.out",
    scrollTrigger: { trigger: ".report-stack", start: "top 82%", once: true },
  });
  gsap.from(".sheet-middle", {
    xPercent: -18,
    yPercent: 8,
    rotate: 0,
    duration: 0.9,
    ease: "power3.out",
    scrollTrigger: { trigger: ".report-stack", start: "top 82%", once: true },
  });
  gsap.from(".report-bars i", {
    scaleY: 0,
    transformOrigin: "bottom center",
    stagger: 0.08,
    duration: 0.62,
    ease: "back.out(1.4)",
    scrollTrigger: { trigger: ".report-bars", start: "top 86%", once: true },
  });
  gsap.from(".report-copy-lines span", {
    scaleX: 0,
    transformOrigin: "left center",
    stagger: 0.08,
    duration: 0.5,
    scrollTrigger: { trigger: ".report-copy-lines", start: "top 88%", once: true },
  });
  gsap.from(".reports-copy > *", {
    x: 44,
    opacity: 0,
    stagger: 0.1,
    duration: 0.68,
    scrollTrigger: { trigger: ".reports-copy", start: "top 80%", once: true },
  });

  gsap.from(".final-layout > div", {
    y: 58,
    opacity: 0,
    stagger: 0.16,
    duration: 0.84,
    ease: "power3.out",
    scrollTrigger: { trigger: ".final-section", start: "top 76%", once: true },
  });
  gsap.to(".final-section", {
    backgroundPosition: "50% 75%",
    ease: "none",
    scrollTrigger: { trigger: ".final-section", start: "top bottom", end: "bottom top", scrub: true },
  });

  gsap.from("footer .footer-grid > div, footer .footer-note", {
    y: 30,
    opacity: 0,
    stagger: 0.1,
    duration: 0.6,
    scrollTrigger: { trigger: "footer", start: "top 88%", once: true },
  });
}

export async function initializeStorytelling() {
  if (window.__CREDIBIL_STORYTELLING_INITIALIZED__) return;
  window.__CREDIBIL_STORYTELLING_INITIALIZED__ = true;

  const [root, animationRuntime] = await Promise.all([waitForLanding(), waitForGsap()]);
  if (!root) return;

  if (!animationRuntime || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.documentElement.classList.add("motion-fallback");
    root.querySelectorAll("[data-reveal]").forEach((node) => node.classList.add("is-visible"));
    return;
  }

  const { gsap, ScrollTrigger } = animationRuntime;
  gsap.registerPlugin(ScrollTrigger);
  document.documentElement.classList.add("storytelling-ready");

  const context = gsap.context(() => {
    setupGlobalScenes(gsap, ScrollTrigger, root);
    setupChecksStory(gsap, ScrollTrigger, root);

    const media = gsap.matchMedia();
    media.add("(min-width: 901px)", () => setupDesktopStory(gsap, ScrollTrigger, root));
    media.add("(max-width: 900px)", () => setupMobileStory(gsap, ScrollTrigger, root));
  }, root);

  const disconnectStageObserver = observeStoryStages(gsap, root);
  const refresh = () => ScrollTrigger.refresh();
  window.addEventListener("load", refresh, { once: true });
  document.fonts?.ready?.then(refresh).catch(() => {});

  window.__CREDIBIL_STORYTELLING_CLEANUP__ = () => {
    disconnectStageObserver();
    context.revert();
    window.removeEventListener("load", refresh);
  };
}
