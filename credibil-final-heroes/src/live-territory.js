const SVG_NS = "http://www.w3.org/2000/svg";
const TARGET_SELECTOR = ".landing .hero .map-field";

function waitForTarget(timeout = 8000) {
  return new Promise((resolve) => {
    const existing = document.querySelector(TARGET_SELECTOR);
    if (existing) {
      resolve(existing);
      return;
    }

    const startedAt = performance.now();
    const observer = new MutationObserver(() => {
      const target = document.querySelector(TARGET_SELECTOR);
      if (target) {
        observer.disconnect();
        resolve(target);
        return;
      }
      if (performance.now() - startedAt > timeout) {
        observer.disconnect();
        resolve(null);
      }
    });

    observer.observe(document.documentElement, { childList: true, subtree: true });
  });
}

function createSvgElement(name, attributes = {}) {
  const element = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, String(value));
  });
  return element;
}

function prepareSvg(svg) {
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  svg.classList.add("live-territory-svg");
  svg.querySelectorAll("style").forEach((style) => style.remove());
  svg.querySelectorAll(".region-lines, #cursor-halo, #particle-layer, #effect-layer, #region-layer")
    .forEach((element) => element.remove());

  let defs = svg.querySelector("defs");
  if (!defs) {
    defs = createSvgElement("defs");
    svg.prepend(defs);
  }
  const sourcePaths = [...svg.querySelectorAll("#md-shape path")];

  const clip = createSvgElement("clipPath", {
    id: "md-live-clip",
    clipPathUnits: "userSpaceOnUse",
  });
  sourcePaths.forEach((path) => clip.appendChild(path.cloneNode(false)));

  const cursorGradient = createSvgElement("radialGradient", { id: "cursorHaloLive" });
  cursorGradient.append(
    createSvgElement("stop", { offset: "0", "stop-color": "#61d2a2", "stop-opacity": ".24" }),
    createSvgElement("stop", { offset: ".48", "stop-color": "#61d2a2", "stop-opacity": ".08" }),
    createSvgElement("stop", { offset: "1", "stop-color": "#61d2a2", "stop-opacity": "0" }),
  );

  const sweepGradient = createSvgElement("linearGradient", {
    id: "sweepGradLive",
    x1: "0",
    x2: "1",
  });
  sweepGradient.append(
    createSvgElement("stop", { offset: "0", "stop-color": "#61d2a2", "stop-opacity": "0" }),
    createSvgElement("stop", { offset: ".48", "stop-color": "#61d2a2", "stop-opacity": ".42" }),
    createSvgElement("stop", { offset: ".58", "stop-color": "#d4f8e8", "stop-opacity": ".62" }),
    createSvgElement("stop", { offset: "1", "stop-color": "#61d2a2", "stop-opacity": "0" }),
  );

  defs.append(clip, cursorGradient, sweepGradient);

  let silhouette = svg.querySelector(".country-silhouette");
  if (!silhouette) {
    silhouette = createSvgElement("use", {
      class: "country-silhouette",
      href: "#md-shape",
    });
    svg.appendChild(silhouette);
  }

  const particleLayer = createSvgElement("g", {
    id: "particle-layer",
    "clip-path": "url(#md-live-clip)",
  });

  const effectLayer = createSvgElement("g", {
    id: "effect-layer",
    "clip-path": "url(#md-live-clip)",
  });
  effectLayer.appendChild(createSvgElement("rect", {
    id: "sweep-band",
    class: "sweep",
    x: "-120",
    y: "-180",
    width: "130",
    height: "1160",
    fill: "url(#sweepGradLive)",
  }));

  const regionLayer = createSvgElement("g", { id: "region-layer" });
  const cursorHalo = createSvgElement("circle", {
    id: "cursor-halo",
    class: "cursor-halo",
    cx: "0",
    cy: "0",
    r: "74",
    "clip-path": "url(#md-live-clip)",
  });

  svg.append(particleLayer, effectLayer, regionLayer, cursorHalo);

  return {
    svg,
    sourcePaths,
    particleLayer,
    regionLayer,
    cursorHalo,
  };
}

async function mountLiveTerritory(target) {
  if (!target || target.dataset.liveTerritoryMounted === "true") return () => {};

  const image = target.querySelector(":scope > img");
  const source = image?.currentSrc || image?.src;
  if (!source) return () => {};

  let svgText;
  try {
    const response = await fetch(source, { credentials: "same-origin" });
    if (!response.ok) throw new Error(`Moldova SVG request failed: ${response.status}`);
    svgText = await response.text();
  } catch (error) {
    console.error("Credibil live territory could not load the Moldova SVG", error);
    return () => {};
  }

  const parsed = new DOMParser().parseFromString(svgText, "image/svg+xml");
  if (parsed.querySelector("parsererror")) {
    console.error("Credibil live territory received invalid SVG");
    return () => {};
  }

  const importedSvg = document.importNode(parsed.documentElement, true);
  const {
    svg,
    sourcePaths,
    particleLayer,
    regionLayer,
    cursorHalo,
  } = prepareSvg(importedSvg);

  if (!sourcePaths.length) {
    console.error("Credibil live territory SVG has no Moldova region paths");
    return () => {};
  }

  target.dataset.liveTerritoryMounted = "true";
  target.classList.add("live-territory-mounted");
  target.querySelectorAll(":scope > img, :scope > canvas").forEach((node) => {
    node.hidden = true;
    node.setAttribute("aria-hidden", "true");
  });

  const host = document.createElement("div");
  host.className = "live-territory-host";
  host.setAttribute("aria-hidden", "true");
  host.appendChild(svg);

  const label = document.createElement("div");
  label.className = "live-territory-label";
  const updateLabel = () => {
    label.textContent = document.documentElement.lang === "ro"
      ? "Republica Moldova"
      : "Республика Молдова";
  };
  updateLabel();

  target.append(host, label);

  const languageObserver = new MutationObserver(updateLabel);
  languageObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["lang"],
  });

  const particles = [];
  const pointer = { x: -9999, y: -9999, active: false };
  const regionPaths = [];
  const startedAt = performance.now();
  let animationFrame = 0;
  let lastFrame = 0;

  const pointInCountry = (x, y) => {
    const point = new DOMPoint(x, y);
    return sourcePaths.some((path) => path.isPointInFill(point));
  };

  const toSvgPoint = (event) => {
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    return point.matrixTransform(svg.getScreenCTM().inverse());
  };

  const randomInside = () => {
    for (let index = 0; index < 250; index += 1) {
      const x = -28 + Math.random() * 668;
      const y = -24 + Math.random() * 818;
      if (pointInCountry(x, y)) return { x, y };
    }
    return { x: 306, y: 390 };
  };

  const buildRegions = () => {
    sourcePaths.forEach((sourcePath, index) => {
      const path = createSvgElement("path", {
        d: sourcePath.getAttribute("d"),
        class: "region-path",
      });
      path.dataset.index = String(index);
      regionLayer.appendChild(path);

      const length = Math.max(1, path.getTotalLength());
      const box = path.getBBox();
      path.style.strokeDasharray = String(length);
      path.style.strokeDashoffset = String(length);

      regionPaths.push({
        element: path,
        centerX: box.x + box.width / 2,
        centerY: box.y + box.height / 2,
      });
    });

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        regionPaths.forEach((region, index) => {
          region.element.style.transition = [
            `stroke-dashoffset ${1.45 + index * 0.018}s cubic-bezier(.2,.72,.2,1) ${index * 0.018}s`,
            "fill .35s ease",
            "stroke .35s ease",
            "opacity .35s ease",
          ].join(", ");
          region.element.style.strokeDashoffset = "0";
        });
      });
    });
  };

  const buildParticles = (count = 340) => {
    for (let index = 0; index < count; index += 1) {
      const targetPoint = randomInside();
      const circle = createSvgElement("circle", {
        cx: targetPoint.x,
        cy: targetPoint.y,
        r: index % 17 === 0 ? 3 : index % 6 === 0 ? 2.15 : 1.45,
        class: "particle",
        fill: index % 9 === 0 ? "#9be7c8" : index % 3 === 0 ? "#61d2a2" : "#2a9c6f",
        opacity: 0,
      });
      particleLayer.appendChild(circle);

      particles.push({
        element: circle,
        targetX: targetPoint.x,
        targetY: targetPoint.y,
        phase: Math.random() * Math.PI * 2,
        delay: Math.random() * 1.65,
      });
    }
  };

  const introValue = (particle, time) => {
    const progress = Math.max(0, Math.min(1, (time - 0.35 - particle.delay) / 1.15));
    return 1 - (1 - progress) ** 3;
  };

  const pointerOn = (event) => {
    const point = toSvgPoint(event);
    pointer.x = point.x;
    pointer.y = point.y;
    pointer.active = true;
    cursorHalo.setAttribute("cx", String(point.x));
    cursorHalo.setAttribute("cy", String(point.y));
    target.classList.add("is-pointer-active");
  };

  const pointerOff = () => {
    pointer.active = false;
    pointer.x = -9999;
    pointer.y = -9999;
    target.classList.remove("is-pointer-active");
  };

  svg.addEventListener("pointermove", pointerOn);
  svg.addEventListener("pointerenter", pointerOn);
  svg.addEventListener("pointerleave", pointerOff);

  buildRegions();
  buildParticles();

  const animate = (now) => {
    animationFrame = requestAnimationFrame(animate);
    if (document.hidden || now - lastFrame < 32) return;
    lastFrame = now;

    const time = (now - startedAt) / 1000;
    const cycle = (Math.max(0, time - 2.7) % 8.2) / 8.2;
    const wave = -120 + 980 * cycle;
    const searchBoost = target.classList.contains("is-active") ? 1.12 : 1;

    if (time > 2.7) target.classList.add("map-ready");

    particles.forEach((particle) => {
      const intro = introValue(particle, time);
      const coordinate = particle.targetY + particle.targetX * 0.22;
      const glow = Math.max(0, 1 - Math.abs(coordinate - wave) / 72);
      let deltaX = 0;
      let deltaY = 0;
      let scale = (0.25 + 0.75 * intro) * (1 + glow * 0.18) * searchBoost;
      let alpha = (0.72 + 0.1 * Math.sin(time * 0.9 + particle.phase) + glow * 0.26) * intro;

      if (pointer.active) {
        const vectorX = particle.targetX - pointer.x;
        const vectorY = particle.targetY - pointer.y;
        const distance = Math.hypot(vectorX, vectorY);

        if (distance < 82) {
          const force = 1 - distance / 82;
          deltaX = (vectorX / (distance || 1)) * force * 7;
          deltaY = (vectorY / (distance || 1)) * force * 7;
          scale *= 1 + force * 0.22;
          alpha = Math.min(1, alpha + force * 0.28);
        }
      }

      particle.element.setAttribute("cx", String(particle.targetX + deltaX));
      particle.element.setAttribute("cy", String(particle.targetY + deltaY));
      particle.element.setAttribute("opacity", String(Math.max(0, Math.min(1, alpha))));
      particle.element.style.transform = `scale(${scale})`;
    });

    regionPaths.forEach((region) => {
      const glow = Math.max(
        0,
        1 - Math.abs(region.centerY + region.centerX * 0.22 - wave) / 105,
      );
      const near = pointer.active
        ? Math.max(0, 1 - Math.hypot(region.centerX - pointer.x, region.centerY - pointer.y) / 115)
        : 0;

      region.element.style.stroke = `rgba(157,225,196,${0.38 + glow * 0.42 + near * 0.2})`;
      region.element.style.fill = `rgba(42,156,111,${glow * 0.055 + near * 0.04})`;
    });
  };

  animationFrame = requestAnimationFrame(animate);

  return () => {
    cancelAnimationFrame(animationFrame);
    languageObserver.disconnect();
    svg.removeEventListener("pointermove", pointerOn);
    svg.removeEventListener("pointerenter", pointerOn);
    svg.removeEventListener("pointerleave", pointerOff);
    host.remove();
    label.remove();
    delete target.dataset.liveTerritoryMounted;
    target.classList.remove(
      "live-territory-mounted",
      "is-pointer-active",
      "map-ready",
    );
    target.querySelectorAll(":scope > img, :scope > canvas").forEach((node) => {
      node.hidden = false;
      node.removeAttribute("aria-hidden");
    });
  };
}

export async function initializeLiveTerritory() {
  if (window.__CREDIBIL_LIVE_TERRITORY_INITIALIZED__) return;
  window.__CREDIBIL_LIVE_TERRITORY_INITIALIZED__ = true;

  const target = await waitForTarget();
  if (!target) return;

  const cleanup = await mountLiveTerritory(target);
  window.__CREDIBIL_LIVE_TERRITORY_CLEANUP__ = cleanup;
}
