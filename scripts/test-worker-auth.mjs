import worker from "../terminal/worker/src/index.js";

const sharedPassword = "test-shared-password";
const terminalKeyBytes = new Uint8Array(32);
for (let i = 0; i < terminalKeyBytes.length; i += 1) terminalKeyBytes[i] = i + 1;
const terminalKey = Buffer.from(terminalKeyBytes).toString("base64");

const env = {
  DAN_LOGIN_PASSWORD: sharedPassword,
  MAJ_LOGIN_PASSWORD: "intentionally-wrong-secondary-secret",
  TERMINAL_COMMAND_KEY: terminalKey,
  GITHUB_DISPATCH_TOKEN: "test-token"
};

async function loginAndVerify(email) {
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

await loginAndVerify("dan.grmusa@gmail.com");
await loginAndVerify("maj@klemenc.org");

const health = await worker.fetch(new Request("https://example.test/health"), env);
const healthData = await health.json();
if (!healthData.auth_ready || healthData.authorized_users_ready !== 2) {
  throw new Error(`Unexpected health auth state: ${JSON.stringify(healthData)}`);
}

console.log("Cross-device Worker auth logic passed for both authorized users.");
