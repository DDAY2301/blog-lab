import fs from "node:fs";
import worker from "../terminal/worker/src/index.js";

const sharedPassword = "test-shared-password";
const danPassword = "test-dan-password";
const majPassword = "test-maj-password";
const workerSource = fs.readFileSync(new URL("../terminal/worker/src/index.js", import.meta.url), "utf8");
const versionMatch = workerSource.match(/version:\s*"([^"]+)"/);
if (!versionMatch) throw new Error("Worker version marker not found");
const expectedVersion = versionMatch[1];

const terminalKeyBytes = new Uint8Array(32);
for (let i = 0; i < terminalKeyBytes.length; i += 1) terminalKeyBytes[i] = i + 1;
const terminalKey = Buffer.from(terminalKeyBytes).toString("base64");

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input, init = {}) => {
  const url = String(input);
  if (url.startsWith("https://api.github.com/repos/DDAY2301/blog-lab")) {
    if (String(init.method || "GET").toUpperCase() === "PUT") {
      return new Response(JSON.stringify({ content: { path: "public/media/uploads/test.png" } }), {
        status: 201,
        headers: { "content-type": "application/json" }
      });
    }
    return new Response(JSON.stringify({ permissions: { push: true, pull: true } }), {
      status: 200,
      headers: { "content-type": "application/json" }
    });
  }
  return nativeFetch(input, init);
};

async function loginAndVerify(env, email, password) {
  const login = await worker.fetch(new Request("https://example.test/api/login", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password })
  }), env);

  if (login.status !== 200) {
    throw new Error(`Login failed for ${email}: HTTP ${login.status} ${await login.text()}`);
  }

  const setCookie = login.headers.get("set-cookie") || "";
  const cookie = setCookie.split(";")[0];
  if (!cookie.startsWith("bloglab_session=")) {
    throw new Error(`No session cookie returned for ${email}`);
  }

  const me = await worker.fetch(new Request("https://example.test/api/me", {
    headers: { cookie }
  }), env);
  if (me.status !== 200) {
    throw new Error(`Session verification failed for ${email}: HTTP ${me.status}`);
  }
  const data = await me.json();
  if (data.email !== email) throw new Error(`Wrong authenticated identity for ${email}`);
  return cookie;
}

async function expectLoginRejected(env, email, password) {
  const response = await worker.fetch(new Request("https://example.test/api/login", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password })
  }), env);
  if (response.status !== 401) {
    throw new Error(`Expected login rejection for ${email}, got HTTP ${response.status}`);
  }
}

async function verifyHealth(name, env) {
  const health = await worker.fetch(new Request("https://example.test/health"), env);
  const data = await health.json();
  if (!data.auth_ready || data.authorized_users_ready !== 2 || data.auth_self_test_ok !== true) {
    throw new Error(`${name}: unexpected health auth state: ${JSON.stringify(data)}`);
  }
  if (data.version !== expectedVersion) {
    throw new Error(`${name}: expected ${expectedVersion}, got ${data.version}`);
  }
  if (data.media_upload_ready !== true) throw new Error(`${name}: media upload should be ready`);
  if (data.ai_writer_ready !== false || data.ai_review_ready !== false || data.site_editor_ready !== false || data.self_heal_ai_ready !== false) {
    throw new Error(`${name}: AI binding should be absent in isolated auth test`);
  }
  if (data.publisher_scheduler_ready !== true) throw new Error(`${name}: scheduler should be ready`);
}

// Legacy/shared configuration: both users authenticate with LOGIN_PASSWORD,
// even if stale dedicated secrets still exist.
const sharedEnv = {
  LOGIN_PASSWORD: sharedPassword,
  DAN_LOGIN_PASSWORD: "stale-dan-password",
  MAJ_LOGIN_PASSWORD: "stale-maj-password",
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
};
await loginAndVerify(sharedEnv, "dan.grmusa@gmail.com", sharedPassword);
await loginAndVerify(sharedEnv, "maj@klemenc.org", sharedPassword);
await verifyHealth("shared fallback", sharedEnv);

// Preferred configuration: every authorized user has a dedicated password.
const dedicatedEnv = {
  DAN_LOGIN_PASSWORD: danPassword,
  MAJ_LOGIN_PASSWORD: majPassword,
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
};
await loginAndVerify(dedicatedEnv, "dan.grmusa@gmail.com", danPassword);
await loginAndVerify(dedicatedEnv, "maj@klemenc.org", majPassword);
await expectLoginRejected(dedicatedEnv, "dan.grmusa@gmail.com", majPassword);
await expectLoginRejected(dedicatedEnv, "maj@klemenc.org", danPassword);
await verifyHealth("dedicated passwords", dedicatedEnv);

// Media upload remains usable with a fresh session.
const cookie = await loginAndVerify(sharedEnv, "dan.grmusa@gmail.com", sharedPassword);
const form = new FormData();
form.append("file", new File([new Uint8Array([137, 80, 78, 71])], "terminal-test.png", { type: "image/png" }));
const upload = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  headers: { cookie },
  body: form
}), sharedEnv);
const uploadData = await upload.json();
if (upload.status !== 201 || !String(uploadData.url || "").includes("/media/uploads/")) {
  throw new Error(`Media upload flow failed: HTTP ${upload.status} ${JSON.stringify(uploadData)}`);
}

console.log("Fresh-device cross-browser auth, dedicated/shared secrets and media upload passed.");
