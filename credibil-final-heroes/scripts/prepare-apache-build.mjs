#!/usr/bin/env node
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const client = path.join(root, "dist", "client");
const index = path.join(client, "index.html");

if (!existsSync(index)) throw new Error("Missing Vite build output: " + index);

mkdirSync(path.join(client, "ru"), { recursive: true });
copyFileSync(index, path.join(client, "ru", "index.html"));

console.log("Prepared Apache build: dist/client/ru/index.html");

