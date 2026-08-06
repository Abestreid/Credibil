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

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

window.requestAnimationFrame(async () => {
  document.querySelector(".landing .hero .map-field")?.classList.add("live-territory-pending");

  const storytelling = initializeStorytelling();
  initializeLiveTerritory();

  await storytelling;
  initializeMonitoringTimeline();
});
