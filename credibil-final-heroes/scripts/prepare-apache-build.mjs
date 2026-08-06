#!/usr/bin/env node
import {
  appendFileSync,
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
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

const baseCompanyCss = readFileSync(companyStyles, "utf8");
const baseMetricValueRule =
  ".metric-value { display: block; margin-top: 13px;";

if (!baseCompanyCss.includes(baseMetricValueRule)) {
  throw new Error("Missing base .metric-value margin declaration");
}

writeFileSync(
  companyStyles,
  baseCompanyCss.replace(
    baseMetricValueRule,
    ".metric-value { display: block; /* margin-top: 13px; */",
  ),
  "utf8",
);

appendFileSync(
  companyStyles,
  `

/* Dev refinement: compact company metrics. */
#main-content > .metrics-wrap .metric {
  min-height: 108px;
  padding: 15px 18px;
}

#main-content > .metrics-wrap .metric-label {
  min-height: 28px;
  font-size: 10px;
  line-height: 1.35;
}

#main-content > .metrics-wrap .metric-value {
  /* margin-top: 8px; */
  font-size: 20px;
  line-height: 1.2;
  letter-spacing: -0.025em;
}

#main-content > .metrics-wrap .metric-note {
  margin-top: 5px;
  font-size: 10px;
  line-height: 1.35;
}

@media (max-width: 640px) {
  #main-content > .metrics-wrap .metric {
    min-height: 100px;
    padding: 13px 15px;
  }
}
`,
);

console.log("Prepared Apache build: dist/client/ru/index.html");
console.log("Applied compact sizing and removed metric value top margins.");
