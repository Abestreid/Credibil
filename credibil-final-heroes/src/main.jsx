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
