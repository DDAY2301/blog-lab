import worker from "../terminal/worker/src/index.js";

const sharedPassword = "test-shared-password";
const terminalKeyBytes = new Uint8Array(32);
for (let i = 0; i < terminalKeyBytes.length; i += 1) terminalKeyBytes[i] = i + 1;
const terminalKey = Buffer.from(terminalKeyBytes).toString("base64");

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
}

async function runScenario(name, env) {
  await loginAndVerify(env, "dan.grmusa@gmail.com");
  await loginAndVerify(env, "maj@klemenc.org");

  const health = await worker.fetch(new Request("https://example.test/health"), env);
  const healthData = await health.json();
  if (!healthData.auth_ready || healthData.authorized_users_ready !== 2) {
    throw new Error(`${name}: unexpected health auth state: ${JSON.stringify(healthData)}`);
  }
  if (healthData.version !== "auth-v5-dual-secret-compat") {
    throw new Error(`${name}: unexpected auth version: ${healthData.version}`);
  }
}

await runScenario("Dan secret valid, Maj legacy secret wrong", {
  DAN_LOGIN_PASSWORD: sharedPassword,
  MAJ_LOGIN_PASSWORD: "intentionally-wrong-secondary-secret",
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
});

await runScenario("Maj secret valid, Dan legacy secret wrong", {
  DAN_LOGIN_PASSWORD: "intentionally-wrong-primary-secret",
  MAJ_LOGIN_PASSWORD: sharedPassword,
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
});

console.log("Fresh-device Worker auth passed with either configured shared secret.");
