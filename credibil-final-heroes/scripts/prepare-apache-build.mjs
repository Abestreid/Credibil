#!/usr/bin/env node
import {
  appendFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const client = path.join(root, "dist", "client");
const index = path.join(client, "index.html");
const ruDirectory = path.join(client, "ru");
const ruIndex = path.join(ruDirectory, "index.html");
const companyStyles = path.join(
  client,
  "ru",
  "companies",
  "1004600034130",
  "styles.css",
);

if (!existsSync(index)) throw new Error("Missing Vite build output: " + index);

function neutralizeHeadingSelectors(css) {
  return css.replace(
    /(^|[,{>+~\s])h([1-6])(?=[.#:\[\s,{>+~]|$)/gm,
    (_match, prefix, level) => `${prefix}[data-heading-level="${level}"]`,
  );
}

function stripSearchMarkup(html) {
  let output = html;

  output = output.replace(/\s*<title\b[^>]*>[\s\S]*?<\/title>\s*/gi, "\n");
  output = output.replace(
    /\s*<meta\b(?=[^>]*(?:name\s*=\s*["'](?:description|keywords|robots|googlebot|bingbot)["']|property\s*=\s*["']og:[^"']+["']|name\s*=\s*["']twitter:[^"']+["']))[^>]*>\s*/gi,
    "\n",
  );
  output = output.replace(
    /\s*<link\b(?=[^>]*(?:rel\s*=\s*["'](?:canonical|icon|shortcut icon)["']|hreflang\s*=))[^>]*>\s*/gi,
    "\n",
  );
  output = output.replace(
    /\s*<script\b[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>[\s\S]*?<\/script>\s*/gi,
    "\n",
  );

  output = output.replace(
    /\s(?:itemscope|itemtype|itemprop|itemid|itemref|data-nosnippet)\b(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?/gi,
    "",
  );

  output = output.replace(
    /<style\b([^>]*)>([\s\S]*?)<\/style>/gi,
    (_match, attributes, css) => `<style${attributes}>${neutralizeHeadingSelectors(css)}</style>`,
  );

  output = output.replace(
    /<h([1-6])(\b[^>]*)>/gi,
    (_match, level, attributes) => `<div data-heading-level="${level}"${attributes}>`,
  );
  output = output.replace(/<\/h[1-6]\s*>/gi, "</div>");

  return output;
}

function walk(directory, callback) {
  for (const entry of readdirSync(directory)) {
    const absolute = path.join(directory, entry);
    if (statSync(absolute).isDirectory()) walk(absolute, callback);
    else callback(absolute);
  }
}

const rootIndexHtml = readFileSync(index, "utf8");
const ruIndexHtml = rootIndexHtml
  .replaceAll('href="./assets/', 'href="../assets/')
  .replaceAll('src="./assets/', 'src="../assets/');

mkdirSync(ruDirectory, { recursive: true });
writeFileSync(ruIndex, ruIndexHtml, "utf8");

walk(client, (file) => {
  if (file.endsWith(".html")) {
    writeFileSync(file, stripSearchMarkup(readFileSync(file, "utf8")), "utf8");
  } else if (file.endsWith(".css")) {
    writeFileSync(file, neutralizeHeadingSelectors(readFileSync(file, "utf8")), "utf8");
  }
});

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

/* Compact company metrics. */
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
console.log("Adjusted nested RU asset paths.");
console.log("Removed search metadata, structured data, icons, and heading semantics from all built pages.");
console.log("Applied compact sizing and removed metric value top margins.");
