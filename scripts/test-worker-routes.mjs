import worker from "../terminal/worker/src/index.js";

const password = "route-test-password";
const keyBytes = new Uint8Array(32).fill(7);
const env = {
  DAN_LOGIN_PASSWORD: password,
  TERMINAL_COMMAND_KEY: Buffer.from(keyBytes).toString("base64"),
  GITHUB_DISPATCH_TOKEN: "route-test-token"
};

let dispatchedRequestId = "";

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input, init = {}) => {
  const url = String(input);
  const method = String(init.method || "GET").toUpperCase();

  if (url.includes("/actions/workflows/operator-terminal.yml/dispatches") && method === "POST") {
    const body = JSON.parse(String(init.body || "{}"));
    dispatchedRequestId = String(body?.inputs?.request_id || "");
    return new Response(null, { status: 204 });
  }

  if (url.includes("/actions/workflows/operator-terminal.yml/runs")) {
    return new Response(JSON.stringify({
      workflow_runs: dispatchedRequestId ? [{
        display_title: `Private Terminal · ${dispatchedRequestId}`,
        status: "completed",
        conclusion: "success",
        html_url: "https://github.com/DDAY2301/blog-lab/actions/runs/1",
        updated_at: "2026-09-18T16:00:00Z"
      }] : []
    }), { status: 200, headers: { "content-type": "application/json" } });
  }

  if (url === "https://api.github.com/repos/DDAY2301/blog-lab") {
    return new Response(JSON.stringify({ permissions: { push: true } }), {
      status: 200,
      headers: { "content-type": "application/json" }
    });
  }

  return nativeFetch(input, init);
};

function check(value, message) {
  if (!value) throw new Error(message);
}

async function login() {
  const response = await worker.fetch(new Request("https://example.test/api/login", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email: "dan.grmusa@gmail.com", password })
  }), env);
  check(response.status === 200, "Valid login must succeed");
  const cookie = (response.headers.get("set-cookie") || "").split(";")[0];
  check(cookie.startsWith("bloglab_session="), "Login must issue session cookie");
  return cookie;
}

let response = await worker.fetch(new Request("https://example.test/api/me"), env);
check(response.status === 401, "Anonymous /api/me must return 401");

response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ command: "Ustavi objavljanje" })
}), env);
check(response.status === 401, "Anonymous command must return 401");

response = await worker.fetch(new Request("https://example.test/?fresh=1", {
  headers: { cookie: "bloglab_session=old-session" }
}), env);
check(response.status === 200, "Fresh-login page must render");
check((response.headers.get("set-cookie") || "").includes("Max-Age=0"), "Fresh-login must clear cookie");


// Bad login cases
response = await worker.fetch(new Request("https://example.test/api/login", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ email: "unknown@example.com", password })
}), env);
check(response.status === 401, "Unknown email must be rejected");

response = await worker.fetch(new Request("https://example.test/api/login", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ email: "dan.grmusa@gmail.com", password: "wrong-password" })
}), env);
check(response.status === 401, "Wrong password must be rejected");

const missingLoginEnv = {
  TERMINAL_COMMAND_KEY: env.TERMINAL_COMMAND_KEY,
  GITHUB_DISPATCH_TOKEN: env.GITHUB_DISPATCH_TOKEN
};
response = await worker.fetch(new Request("https://example.test/api/login", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ email: "dan.grmusa@gmail.com", password })
}), missingLoginEnv);
check(response.status === 503, "Missing login secret must return 503");

// Anonymous media upload must fail
const anonymousForm = new FormData();
anonymousForm.append("file", new File([new Uint8Array([1,2,3])], "x.png", { type: "image/png" }));
response = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  body: anonymousForm
}), env);
check(response.status === 401, "Anonymous media upload must return 401");

const cookie = await login();


response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: "{"
}), env);
check(response.status === 400, "Invalid command JSON must return 400");

response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "   " })
}), env);
check(response.status === 400, "Empty command must return 400");

response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "x".repeat(4001) })
}), env);
check(response.status === 400, "Overlong command must return 400");

response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "Ustavi objavljanje", mode: "invalid", category: "invalid" })
}), env);
check(response.status === 202, "Valid authenticated command must dispatch");
const accepted = await response.json();
check(/^[0-9a-f-]{36}$/i.test(String(accepted.id || "")), "Dispatch must return request id");
check(dispatchedRequestId === accepted.id, "GitHub dispatch must use returned request id");


const badMedia = new FormData();
badMedia.append("file", new File([new Uint8Array([1,2,3])], "bad.txt", { type: "text/plain" }));
response = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  headers: { cookie },
  body: badMedia
}), env);
check(response.status === 415, "Unsupported media type must return 415");

const tooLarge = new FormData();
tooLarge.append("file", new File([new Uint8Array(5 * 1024 * 1024 + 1)], "big.png", { type: "image/png" }));
response = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  headers: { cookie },
  body: tooLarge
}), env);
check(response.status === 413, "Oversized media must return 413");

const noFile = new FormData();
response = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  headers: { cookie },
  body: noFile
}), env);
check(response.status === 400, "Missing media file must return 400");

response = await worker.fetch(new Request("https://example.test/api/status", {
  headers: { cookie }
}), env);
check(response.status === 400, "Missing status id must return 400");

response = await worker.fetch(new Request("https://example.test/api/status?id=not-a-uuid", {
  headers: { cookie }
}), env);
check(response.status === 400, "Invalid status id must return 400");

response = await worker.fetch(new Request(`https://example.test/api/status?id=${accepted.id}`, {
  headers: { cookie }
}), env);
check(response.status === 200, "Valid status lookup must succeed");
const status = await response.json();
check(status.status === "completed" && status.conclusion === "success", "Status must map workflow result");

response = await worker.fetch(new Request("https://example.test/api/logout", {
  method: "POST",
  headers: { cookie }
}), env);
check(response.status === 200, "Logout must succeed");
check((response.headers.get("set-cookie") || "").includes("Max-Age=0"), "Logout must clear cookie");

console.log("Worker terminal route matrix passed.");
