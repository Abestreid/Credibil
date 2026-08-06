#!/usr/bin/env node
import { appendFileSync, copyFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const client = path.join(root, "dist", "client");
const index = path.join(client, "index.html");
const companyStyles = path.join(
  client,
  "ru",
  "companies",
  "1004600034130",
  "styles.css",
);

if (!existsSync(index)) throw new Error("Missing Vite build output: " + index);

mkdirSync(path.join(client, "ru"), { recursive: true });
copyFileSync(index, path.join(client, "ru", "index.html"));

if (!existsSync(companyStyles)) {
  throw new Error("Missing company page stylesheet: " + companyStyles);
}

appendFileSync(
  companyStyles,
  `

/* Dev refinement: compact, uniform company metrics typography. */
#main-content > .metrics-wrap .metric-label {
  font-size: 10px;
}

#main-content > .metrics-wrap .metric-value {
  font-size: 20px;
  line-height: 1.2;
  letter-spacing: -0.025em;
}

#main-content > .metrics-wrap .metric-note {
  font-size: 10px;
}
`,
);

console.log("Prepared Apache build: dist/client/ru/index.html");
console.log("Applied compact typography to company metrics.");
