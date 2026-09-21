import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const workerPath = path.join(root, "terminal", "worker", "src", "index.js");
const source = await fs.readFile(workerPath, "utf8");

const hooks = [
  "localCommandIntent",
  "normalizedCommandIntent",
  "safeFailureText",
  "isHelpCommand",
  "withTimeout",
];
for (const name of hooks) {
  if (!source.includes(`function ${name}`) && !source.includes(`async function ${name}`)) {
    throw new Error(`Missing stress-test hook: ${name}`);
  }
}

const dir = await fs.mkdtemp(path.join(os.tmpdir(), "bloglab-stress-"));
const modulePath = path.join(dir, "worker.mjs");
await fs.writeFile(modulePath, source + `\nexport const __stress = { ${hooks.join(", ")} };\n`, "utf8");
const mod = await import(pathToFileURL(modulePath).href + `?v=${Date.now()}`);
const h = mod.__stress;

function assert(value, message) {
  if (!value) throw new Error(message);
}

const base = [
  ["control", "ustavi agenta in objavljanje"],
  ["control", "nadaljuj objavljanje in vklopi agenta"],
  ["control", "preklopi objavljanje na automatic mode"],
  ["control", "preveri status agenta"],
  ["article", "objavi članek o tehnologiji v Sloveniji"],
  ["article", "write an article about renewable energy"],
  ["site", "izboljšaj dizajn in mobile layout strani"],
  ["site", "dodaj galerijo fotografij na stran"],
  ["site", "spremeni barvno temo strani v modro"],
  ["site", "izboljšaj SEO in meta opis strani"],
];

const wrappers = [
  (x) => x,
  (x) => "prosim " + x,
  (x) => "nujno: " + x,
  (x) => "please " + x,
  (x) => "molim " + x,
  (x) => x + " hvala",
];

const started = Date.now();
let routingChecks = 0;
for (let round = 0; round < 40; round += 1) {
  for (const [expected, original] of base) {
    for (const wrap of wrappers) {
      const command = wrap(original);
      const result = h.localCommandIntent(command);
      assert(["article", "site", "control"].includes(result.mode), "Invalid mode under stress");
      assert(result.mode === expected, `Routing drift: ${command} => ${result.mode}, expected ${expected}`);
      assert(Number.isFinite(result.confidence), "Non-numeric confidence");
      assert(typeof result.normalized === "string", "Normalized command missing");
      routingChecks += 1;
    }
  }
}
const elapsed = Date.now() - started;
assert(elapsed < 12000, `Routing stress suite too slow: ${elapsed}ms`);

// Maximum accepted command size must remain computationally safe for local routing.
const longCommand = ("izboljšaj stran " + "x ".repeat(2500)).slice(0, 4000);
const longResult = h.localCommandIntent(longCommand);
assert(["article", "site", "control"].includes(longResult.mode), "4000-char command crashed routing");
assert(h.normalizedCommandIntent(longCommand).length <= 4000, "Normalization expanded command unexpectedly");

// Help commands should stay local even when phrased naturally.
for (const help of ["pomoč", "pokaži vse komande", "kaj znaš", "help commands", "what can you do"]) {
  assert(h.isHelpCommand(help), `Help command not recognized: ${help}`);
}

// Failure output must redact credentials repeatedly and deterministically.
for (let i = 0; i < 200; i += 1) {
  const value = h.safeFailureText(
    `error ghp_abcdefghijklmnopqrstuvwxyz123456 github_pat_abcdefghijklmnopqrstuvwxyz_123456789 Bearer abc.def.ghi run=${i}`
  );
  assert(!value.includes("ghp_"), "Classic GitHub token leaked");
  assert(!value.includes("github_pat_"), "Fine-grained GitHub token leaked");
  assert(!value.includes("abc.def.ghi"), "Bearer token leaked");
}

// Timeout guard must terminate a dead dependency.
let timeoutOk = false;
try {
  await h.withTimeout(new Promise(() => {}), 1000, "stress_timeout");
} catch (error) {
  timeoutOk = String(error?.message || error).includes("stress_timeout");
}
assert(timeoutOk, "Dead dependency was not bounded by timeout guard");

console.log(JSON.stringify({
  ok: true,
  routing_checks: routingChecks,
  routing_ms: elapsed,
  max_command_length: longCommand.length,
  credential_redaction_checks: 200,
  help_variants: 5,
  timeout_guard: "ok",
}, null, 2));
