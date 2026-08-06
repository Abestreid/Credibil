import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App.jsx";
import { configureRuntimeAssets, initializeStorytelling } from "./storytelling.js";
import "./styles.css";
import "./storytelling.css";

configureRuntimeAssets();

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

window.requestAnimationFrame(() => {
  initializeStorytelling();
});
