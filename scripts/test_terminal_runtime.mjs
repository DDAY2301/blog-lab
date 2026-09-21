import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const workerPath = path.join(root, "terminal", "worker", "src", "index.js");
const suitePath = path.join(root, "data", "terminal-command-test-suite.json");
const source = await fs.readFile(workerPath, "utf8");
const suite = JSON.parse(await fs.readFile(suitePath, "utf8"));

const hookNames = [
  "foldCommandText",
  "normalizedCommandIntent",
  "localCommandIntent",
  "isAgentStatusCommand",
  "shouldUsePublicationOperationalCheck",
  "shouldUseTerminalDiagnostics",
  "shouldUseDomainOperationalAnswer",
  "cleanTerminalChatAnswer",
  "terminalChatFallback",
  "safeFailureText",
  "withTimeout",
  "isHelpCommand",
  "terminalCommandHelp",
  "storeUploadedMedia",
  "safeMediaStem",
];

for (const name of hookNames) {
  if (!source.includes(`function ${name}`) && !source.includes(`async function ${name}`)) {
    throw new Error(`Runtime test hook missing after hardening overlay: ${name}`);
  }
}

const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "bloglab-terminal-test-"));
const tempModule = path.join(tempDir, "worker-under-test.mjs");
const exportLine = `
export const __terminalTestHooks = { ${hookNames.join(", ")} };
`;
await fs.writeFile(tempModule, source + exportLine, "utf8");
const mod = await import(pathToFileURL(tempModule).href + `?v=${Date.now()}`);
const h = mod.__terminalTestHooks;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function routeFor(text) {
  if (h.isHelpCommand(text)) return { path: "local_command_help" };
  if (h.shouldUsePublicationOperationalCheck(text)) return { path: "operational_publication_check" };
  if (h.shouldUseDomainOperationalAnswer(text)) return { path: "operational_domain_dns" };
  if (h.shouldUseTerminalDiagnostics(text)) return { path: "operational_terminal_diagnostics" };
  const intent = h.localCommandIntent(text);
  if (intent.mode === "control" && h.isAgentStatusCommand(text)) {
    return { path: "local_agent_status", intent };
  }
  return { path: "github_workflow_dispatch", intent };
}

const failures = [];
for (const item of suite.commands || []) {
  const actual = routeFor(item.text);
  const problems = [];
  if (actual.path !== item.expected_path) {
    problems.push(`path expected=${item.expected_path} actual=${actual.path}`);
  }
  if (item.expected_mode && actual.intent?.mode !== item.expected_mode) {
    problems.push(`mode expected=${item.expected_mode} actual=${actual.intent?.mode}`);
  }
  if (item.expected_action && actual.intent?.action !== item.expected_action) {
    problems.push(`action expected=${item.expected_action} actual=${actual.intent?.action}`);
  }
  if (problems.length) failures.push({ name: item.name, text: item.text, problems, actual });
}

// Verify redaction never leaks common token shapes into terminal failure details.
const secretSample = "failure " + "ghp_" + "abcdefghijklmnopqrstuvwxyz123456" + " Bearer abc.def.ghi " + "github_pat_" + "abcdefghijklmnopqrstuvwxyz_123456789";
const redacted = h.safeFailureText(secretSample);
assert(!redacted.includes("ghp_"), "GitHub classic token was not redacted");
assert(!redacted.includes("github_pat_"), "GitHub fine-grained token was not redacted");
assert(!redacted.includes("abc.def.ghi"), "Bearer token was not redacted");

// Verify model scratch/planning text is replaced by the deterministic safe fallback.
const cleaned = h.cleanTerminalChatAnswer("Draft 1\\nRefining the Response\\nOpening: internal planning", "preveri terminal");
assert(!/Draft 1|Refining the Response|Opening:/i.test(cleaned), "Planning/scratch text leaked through chatbot sanitizer");
assert(cleaned.includes("Pomočnik je prejel vprašanje"), "Planning leak did not fall back to deterministic response");

// Unicode/diacritic folding and typo correction must remain stable.
assert(h.foldCommandText("ČLANEK – ŽE") === "clanek ze", "Diacritic folding regression");
assert(h.normalizedCommandIntent("wrtie artcle") === "napisi clanek", "Typo normalization regression");

const help = h.terminalCommandHelp();
assert(help?.mode === "terminal_command_help", "Terminal help mode changed");
assert(Array.isArray(help?.catalog) && help.catalog.length >= 10, "Terminal command catalog is incomplete");
assert(String(help?.text || "").includes("Nadzor"), "Terminal help text is missing command groups");

const unsafeName = h.safeMediaStem("../../<script>alert(1)</script>.png");
assert(!/[<>/\\]/.test(unsafeName), "Unsafe media filename characters survived sanitization");
assert(unsafeName.length > 0 && unsafeName.length <= 50, "Sanitized media stem length is invalid");

const unsupportedMedia = await h.storeUploadedMedia({}, {
  type: "text/html",
  size: 128,
  name: "payload.html",
  async arrayBuffer() { return new ArrayBuffer(128); }
});
assert(unsupportedMedia?.status === 415 && unsupportedMedia?.code === "UNSUPPORTED_MEDIA_TYPE", "Unsupported media type guard failed");

const oversizedMedia = await h.storeUploadedMedia({}, {
  type: "image/png",
  size: 5 * 1024 * 1024 + 1,
  name: "huge.png",
  async arrayBuffer() { return new ArrayBuffer(1); }
});
assert(oversizedMedia?.status === 413 && oversizedMedia?.code === "MEDIA_TOO_LARGE", "Oversized media guard failed");

// A stalled dependency must be bounded instead of hanging the chatbot indefinitely.
let timeoutGuard = false;
const timeoutStarted = Date.now();
try {
  await h.withTimeout(new Promise(() => {}), 10, "runtime_timeout_guard");
} catch (error) {
  timeoutGuard = String(error?.message || error).includes("runtime_timeout_guard");
}
assert(timeoutGuard, "withTimeout did not reject a stalled dependency");
assert(Date.now() - timeoutStarted < 1800, "withTimeout exceeded the bounded runtime window");

if (failures.length) {
  console.error(JSON.stringify({ ok:false, failures }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({
  ok: true,
  behavioral_cases: suite.commands.length,
  suite_version: suite.version,
  redaction: "ok",
  planning_leak_sanitizer: "ok",
  typo_normalization: "ok",
  command_help_catalog: "ok",
  media_filename_sanitizer: "ok",
  media_type_guard: "ok",
  media_size_guard: "ok",
  timeout_guard: "ok"
}, null, 2));
