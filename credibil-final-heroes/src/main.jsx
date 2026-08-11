import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App.jsx";
import { initializeLiveTerritory } from "./live-territory.js";
import { initializeMonitoringTimeline } from "./monitoring-timeline.js";
import { configureRuntimeAssets, initializeStorytelling } from "./storytelling.js";
import "./styles.css";
import "./storytelling.css";
import "./live-territory.css";

configureRuntimeAssets();

const productionBase = "/credibil/credibil-final-heroes";
if (
  window.location.pathname === productionBase
  || window.location.pathname.startsWith(`${productionBase}/`)
) {
  window.__CREDIBIL_ASSETS__ = {
    ...(window.__CREDIBIL_ASSETS__ || {}),
    "credibil-logo.svg": `${productionBase}/assets/credibil-logo.svg`,
    "moldova-mask.svg": `${productionBase}/assets/moldova-mask.svg`,
    "moldova-regions.svg": `${productionBase}/assets/moldova-regions.svg`,
  };
}

const searchMarkupSelector = [
  "title",
  'meta[name="description"]',
  'meta[name="keywords"]',
  'meta[name="robots"]',
  'meta[name="googlebot"]',
  'meta[name="bingbot"]',
  'meta[property^="og:"]',
  'meta[name^="twitter:"]',
  'link[rel="canonical"]',
  'link[rel="alternate"][hreflang]',
  'link[hreflang]',
  'link[rel~="icon"]',
  'script[type="application/ld+json"]',
].join(",");

function neutralizeSearchMarkup(root = document) {
  if (root.nodeType === Node.ELEMENT_NODE && root.matches?.(searchMarkupSelector)) {
    root.remove();
    return;
  }

  root.querySelectorAll?.(searchMarkupSelector).forEach((node) => node.remove());

  const structuredNodes = [];
  if (root.nodeType === Node.ELEMENT_NODE) structuredNodes.push(root);
  root.querySelectorAll?.("*").forEach((node) => structuredNodes.push(node));
  structuredNodes.forEach((node) => {
    ["itemscope", "itemtype", "itemprop", "itemid", "itemref", "data-nosnippet"].forEach((name) => {
      if (node.hasAttribute?.(name)) node.removeAttribute(name);
    });
  });
}

neutralizeSearchMarkup(document);
const searchMarkupObserver = new MutationObserver((records) => {
  records.forEach((record) => record.addedNodes.forEach((node) => neutralizeSearchMarkup(node)));
});
searchMarkupObserver.observe(document.documentElement, { childList: true, subtree: true });

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

window.requestAnimationFrame(async () => {
  neutralizeSearchMarkup(document);
  document.querySelector(".landing .hero .map-field")?.classList.add("live-territory-pending");

  const storytelling = initializeStorytelling();
  initializeLiveTerritory();

  await storytelling;
  initializeMonitoringTimeline();
  neutralizeSearchMarkup(document);
});
