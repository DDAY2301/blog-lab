import worker from "../terminal/worker/src/index.js";

const sharedPassword = "test-shared-password";
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

async function loginAndVerify(env, email) {
  const login = await worker.fetch(new Request("https://example.test/api/login", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password: sharedPassword })
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
  if (data.email !== email) {
    throw new Error(`Wrong authenticated identity for ${email}`);
  }
  return cookie;
}

async function runScenario(name, env) {
  await loginAndVerify(env, "dan.grmusa@gmail.com");
  await loginAndVerify(env, "maj@klemenc.org");

  const health = await worker.fetch(new Request("https://example.test/health"), env);
  const healthData = await health.json();
  if (!healthData.auth_ready || healthData.authorized_users_ready !== 2) {
    throw new Error(`${name}: unexpected health auth state: ${JSON.stringify(healthData)}`);
  }
  if (healthData.version !== "auth-v6.6-diagnostics") {
    throw new Error(`${name}: unexpected auth version: ${healthData.version}`);
  }
  if (healthData.media_upload_ready !== true) {
    throw new Error(`${name}: media upload capability should be ready in test`);
  }
  if (healthData.ai_writer_ready !== false) {
    throw new Error(`${name}: AI binding should be absent in this isolated auth test`);
  }
  if (healthData.site_editor_ready !== false) {
    throw new Error(`${name}: site-editor binding should be absent in this isolated auth test`);
  }
}

const mediaEnv = {
  DAN_LOGIN_PASSWORD: sharedPassword,
  MAJ_LOGIN_PASSWORD: "intentionally-wrong-secondary-secret",
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
};

await runScenario("Dan secret valid, Maj legacy secret wrong", mediaEnv);

await runScenario("Maj secret valid, Dan legacy secret wrong", {
  DAN_LOGIN_PASSWORD: "intentionally-wrong-primary-secret",
  MAJ_LOGIN_PASSWORD: sharedPassword,
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
});

const cookie = await loginAndVerify(mediaEnv, "dan.grmusa@gmail.com");
const form = new FormData();
form.append("file", new File([new Uint8Array([137, 80, 78, 71])], "terminal-test.png", { type: "image/png" }));
const upload = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  headers: { cookie },
  body: form
}), mediaEnv);
const uploadData = await upload.json();
if (upload.status !== 201 || !String(uploadData.url || "").includes("/media/uploads/")) {
  throw new Error(`Media upload flow failed: HTTP ${upload.status} ${JSON.stringify(uploadData)}`);
}

console.log("Fresh-device auth and terminal media upload logic passed.");
