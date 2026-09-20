import worker from "../terminal/worker/src/index.js";

const password = "route-test-password";
const keyBytes = new Uint8Array(32).fill(7);
const env = {
  DAN_LOGIN_PASSWORD: password,
  TERMINAL_COMMAND_KEY: Buffer.from(keyBytes).toString("base64"),
  GITHUB_DISPATCH_TOKEN: "route-test-token",
  AI: {
    async run(model, request) {
      if (model !== "@cf/zai-org/glm-4.7-flash") throw new Error("unexpected model");
      if (!Array.isArray(request?.messages) || request.messages.length !== 2) throw new Error("unexpected AI messages");
      const userMessage = String(request.messages[1]?.content || "");
      if (request?.max_tokens === 900) {
        return {
          response: {
            pass: true,
            issues: [],
            unsupported_claims: []
          },
          usage: { input_tokens: 10, output_tokens: 5 }
        };
      }
      if (userMessage.includes("NESTED_RESPONSE_TEST")) {
        return {
          response: {
            article: {
              title: "Nested AI članek",
              content: "Nested odgovor je bil pravilno razvit.",
              excerpt: "Nested preizkus.",
              seoDescription: "Nested preizkus.",
              category: "Aktualno",
              tags: ["test"],
              heroImage: null,
              gallery: [],
              video: null,
              sources: []
            }
          },
          usage: { input_tokens: 10, output_tokens: 10 }
        };
      }
      if (userMessage.includes("REPOSITORY CONTEXT")) {
        return {
          response: {
            summary: "Preizkus site editorja",
            edits: [{
              path: "src/Test.jsx",
              action: "replace",
              old: "Old",
              new: "New"
            }]
          },
          usage: { input_tokens: 10, output_tokens: 10 }
        };
      }
      return {
        response: {
          title: "Preizkus AI pisca",
          content: "To je preverjen testni odgovor.",
          excerpt: "Preizkus.",
          seoDescription: "Preizkus.",
          category: "Aktualno",
          tags: ["test"],
          heroImage: null,
          gallery: [],
          video: null,
          sources: []
        },
        usage: { input_tokens: 10, output_tokens: 10 }
      };
    }
  }
};

let dispatchedRequestId = "";
let publisherCatchupPayload = null;
let failDispatch = false;
let denyMediaWrite = false;
let workflowConclusion = "success";

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input, init = {}) => {
  const url = String(input);
  const method = String(init.method || "GET").toUpperCase();

  if (url.includes("/actions/workflows/operator-terminal.yml/dispatches") && method === "POST") {
    if (failDispatch) return new Response("dispatch denied", { status: 403 });
    const body = JSON.parse(String(init.body || "{}"));
    dispatchedRequestId = String(body?.inputs?.request_id || "");
    return new Response(null, { status: 204 });
  }

  if (url.includes("/actions/workflows/agent-blog-lab-publisher.yml/dispatches") && method === "POST") {
    publisherCatchupPayload = JSON.parse(String(init.body || "{}"));
    return new Response(null, { status: 204 });
  }

  if (url.includes("/contents/public/media/uploads/") && method === "PUT") {
    if (denyMediaWrite) return new Response("contents denied", { status: 403 });
    return new Response(JSON.stringify({ content: { path: "public/media/uploads/test.png" } }), {
      status: 201,
      headers: { "content-type": "application/json" }
    });
  }

  if (url.includes("/actions/workflows/operator-terminal.yml/runs")) {
    return new Response(JSON.stringify({
      workflow_runs: dispatchedRequestId ? [{
        id: 1,
        display_title: `Private Terminal · ${dispatchedRequestId}`,
        status: "completed",
        conclusion: workflowConclusion,
        html_url: "https://github.com/DDAY2301/blog-lab/actions/runs/1",
        created_at: "2026-09-18T15:59:00Z",
        updated_at: "2026-09-18T16:00:00Z"
      }] : []
    }), { status: 200, headers: { "content-type": "application/json" } });
  }

  if (url.includes("/actions/runs/1/jobs")) {
    return new Response(JSON.stringify({
      jobs: workflowConclusion === "failure" ? [{
        id: 99,
        name: "execute",
        conclusion: "failure",
        steps: [{
          name: "Execute private command with bounded recovery",
          conclusion: "failure"
        }]
      }] : []
    }), { status: 200, headers: { "content-type": "application/json" } });
  }

  if (url.includes("/actions/jobs/99/logs")) {
    return new Response(
      [
        "2026-09-19T19:20:57Z \\u001b[36;1m echo \\\"::error::Copilot policy denied this non-built-in site edit.\\\" \\u001b[0m",
        "2026-09-19T19:20:59Z NO_TOPIC_SOURCES",
        "2026-09-19T19:21:11Z ##[error]Operator request failed after 3 validated attempts."
      ].join("\n") + "\n",
      { status: 200, headers: { "content-type": "text/plain" } }
    );
  }

  if (url === "https://api.github.com/repos/DDAY2301/blog-lab") {
    return new Response(JSON.stringify({ permissions: { push: true } }), {
      status: 200,
      headers: { "content-type": "application/json" }
    });
  }

  if (url.includes("/contents/public/data/agent-status.json")) {
    const content = Buffer.from(JSON.stringify({
      status: "completed",
      enabled: true,
      category: "aktualno",
      posts_today: 2,
      last_run: "2026-09-18T18:00:00+02:00",
      last_success: "2026-09-18T18:00:00+02:00",
      message: "OK"
    }), "utf8").toString("base64");
    return new Response(JSON.stringify({ content }), {
      status: 200,
      headers: { "content-type": "application/json" }
    });
  }

  if (url.includes("/contents/data/agent-control.json")) {
    const content = Buffer.from(JSON.stringify({
      enabled: true,
      publish_mode: "automatic",
      schedule: {
        timezone: "Europe/Ljubljana",
        slots: [
          { time: "08:17", category: "sport" },
          { time: "13:27", category: "politika" },
          { time: "19:43", category: "aktualno" }
        ]
      }
    }), "utf8").toString("base64");
    return new Response(JSON.stringify({ content }), {
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

const writerPayload = JSON.stringify({
  system_prompt: "Piši profesionalno.",
  task_prompt: "Napiši test.",
  category: "aktualno",
  source_items: [{ title: "Vir", summary: "Podatek", url: "https://example.com" }]
});

response = await worker.fetch(new Request("https://example.test/api/scheduler/catch-up", {
  method: "POST"
}), env);
check(response.status === 401, "Scheduler catch-up probe must reject an unauthenticated internal request");

publisherCatchupPayload = null;
const schedulerHeaders = new Headers();
schedulerHeaders.set("authorization", "Bearer " + env.TERMINAL_COMMAND_KEY);
response = await worker.fetch(new Request("https://example.test/api/scheduler/catch-up", {
  method: "POST",
  headers: schedulerHeaders
}), env);
check(response.status === 202, "Scheduler catch-up probe must accept the internal service credential");
const schedulerProbe = await response.json();
check(schedulerProbe.ok === true && schedulerProbe.mode === "catch_up", "Scheduler catch-up probe must report dispatch success");
check(publisherCatchupPayload?.inputs?.catch_up === true, "Scheduler probe must dispatch publisher in catch_up mode");

response = await worker.fetch(new Request("https://example.test/api/ai/write", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: writerPayload
}), env);
check(response.status === 401, "Workers AI writer must reject an unauthenticated internal request");

const writerHeaders = new Headers({ "content-type": "application/json" });
writerHeaders.set("authorization", "Bearer " + env.TERMINAL_COMMAND_KEY);
response = await worker.fetch(new Request("https://example.test/api/ai/write", {
  method: "POST",
  headers: writerHeaders,
  body: writerPayload
}), env);
check(response.status === 200, "Workers AI writer must accept the internal service credential");
const writerResult = await response.json();
check(writerResult.ok === true, "Workers AI writer must report success");
check(writerResult.article?.title === "Preizkus AI pisca", "Workers AI writer must return parsed article JSON");

const nestedWriterPayload = JSON.stringify({
  system_prompt: "Vrni veljaven JSON članek.",
  task_prompt: "NESTED_RESPONSE_TEST",
  category: "aktualno",
  source_items: [{ title: "Vir", summary: "Podatek", url: "https://example.com/nested" }]
});
response = await worker.fetch(new Request("https://example.test/api/ai/write", {
  method: "POST",
  headers: writerHeaders,
  body: nestedWriterPayload
}), env);
check(response.status === 200, "Workers AI writer must accept a nested article object");
const nestedWriterResult = await response.json();
check(nestedWriterResult.article?.title === "Nested AI članek", "Workers AI writer must unwrap nested article payloads");

const reviewPayload = JSON.stringify({
  system_prompt: "Preveri trditve proti virom in vrni JSON.",
  user_prompt: "Članek in preverjeni viri."
});
response = await worker.fetch(new Request("https://example.test/api/ai/review", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: reviewPayload
}), env);
check(response.status === 401, "Workers AI review must reject an unauthenticated request");

response = await worker.fetch(new Request("https://example.test/api/ai/review", {
  method: "POST",
  headers: writerHeaders,
  body: reviewPayload
}), env);
check(response.status === 200, "Workers AI review must accept the internal credential");
const reviewResult = await response.json();
check(reviewResult.ok === true && reviewResult.review?.pass === true, "Workers AI review must return review JSON");

const sitePayload = JSON.stringify({
  system_prompt: "Vrni JSON edit plan.",
  request: "Spremeni Old v New.",
  context: [{
    path: "src/Test.jsx",
    complete: true,
    snippets: [{ label: "full", content: "Old" }]
  }]
});

response = await worker.fetch(new Request("https://example.test/api/ai/edit", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: sitePayload
}), env);
check(response.status === 401, "Workers AI site editor must reject an unauthenticated internal request");

const siteHeaders = new Headers({ "content-type": "application/json" });
siteHeaders.set("authorization", "Bearer " + env.TERMINAL_COMMAND_KEY);
response = await worker.fetch(new Request("https://example.test/api/ai/edit", {
  method: "POST",
  headers: siteHeaders,
  body: sitePayload
}), env);
check(response.status === 200, "Workers AI site editor must accept the internal service credential");
const siteResult = await response.json();
check(siteResult.ok === true, "Workers AI site editor must report success");
check(Array.isArray(siteResult.plan?.edits) && siteResult.plan.edits.length === 1, "Site editor must return an edit plan");

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

const scheduledPromises = [];
await worker.scheduled(
  { scheduledTime: Date.parse("2026-09-20T07:22:00Z"), cron: "7,22,37,52 * * * *" },
  env,
  { waitUntil(promise) { scheduledPromises.push(Promise.resolve(promise)); } }
);
await Promise.all(scheduledPromises);
check(publisherCatchupPayload?.ref === "main", "Cloudflare scheduled handler must dispatch publisher on main");
check(publisherCatchupPayload?.inputs?.catch_up === true, "Scheduled publisher dispatch must use catch_up mode");
check(publisherCatchupPayload?.inputs?.dry_run === false, "Scheduled publisher dispatch must not be dry-run");
check(publisherCatchupPayload?.inputs?.force === false, "Scheduled publisher dispatch must not force manual mode");

const cookie = await login();

// Missing runtime configuration must fail clearly after a valid login.
const noKeyEnv = {
  DAN_LOGIN_PASSWORD: password,
  GITHUB_DISPATCH_TOKEN: env.GITHUB_DISPATCH_TOKEN
};
const noKeyLogin = await worker.fetch(new Request("https://example.test/api/login", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ email: "dan.grmusa@gmail.com", password })
}), noKeyEnv);
const noKeyCookie = (noKeyLogin.headers.get("set-cookie") || "").split(";")[0];
response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie: noKeyCookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "Ustavi objavljanje" })
}), noKeyEnv);
check(response.status === 503, "Missing terminal command key must return 503");

const noTokenEnv = {
  DAN_LOGIN_PASSWORD: password,
  TERMINAL_COMMAND_KEY: env.TERMINAL_COMMAND_KEY
};
const noTokenLogin = await worker.fetch(new Request("https://example.test/api/login", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ email: "dan.grmusa@gmail.com", password })
}), noTokenEnv);
const noTokenCookie = (noTokenLogin.headers.get("set-cookie") || "").split(";")[0];
response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie: noTokenCookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "Ustavi objavljanje" })
}), noTokenEnv);
check(response.status === 503, "Missing GitHub dispatch token must return 503");


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

const beforeStatusDispatch = dispatchedRequestId;
response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "preveri status agenta", mode: "auto", category: "aktualno" })
}), env);
check(response.status === 200, "Agent status command must return immediately");
const directStatusData = await response.json();
check(directStatusData.local === true, "Agent status must be a local terminal result");
check(directStatusData.result?.enabled === true, "Agent status must report enabled state");
check(directStatusData.result?.publish_mode === "automatic", "Agent status must report publish mode");
check(String(directStatusData.result?.summary || "").includes("08:17 sport"), "Agent status must include schedule");
check(dispatchedRequestId === beforeStatusDispatch, "Agent status must not dispatch a workflow");

response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "Ustavi objavljanje", mode: "invalid", category: "invalid" })
}), env);
check(response.status === 202, "Valid authenticated command must dispatch");
const accepted = await response.json();
check(/^[0-9a-f-]{36}$/i.test(String(accepted.id || "")), "Dispatch must return request id");
check(dispatchedRequestId === accepted.id, "GitHub dispatch must use returned request id");

failDispatch = true;
response = await worker.fetch(new Request("https://example.test/api/command", {
  method: "POST",
  headers: { cookie, "content-type": "application/json" },
  body: JSON.stringify({ command: "Ustavi objavljanje", mode: "control", category: "aktualno" })
}), env);
check(response.status === 502, "GitHub dispatch failure must return 502");
failDispatch = false;

denyMediaWrite = true;
const deniedMedia = new FormData();
deniedMedia.append("file", new File([new Uint8Array([137,80,78,71])], "denied.png", { type: "image/png" }));
response = await worker.fetch(new Request("https://example.test/api/media", {
  method: "POST",
  headers: { cookie },
  body: deniedMedia
}), env);
check(response.status === 503, "GitHub media write denial must return 503");
const deniedMediaData = await response.json();
check(deniedMediaData.code === "GITHUB_CONTENTS_WRITE_REQUIRED", "Media denial must expose permission code");
denyMediaWrite = false;


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

workflowConclusion = "failure";
response = await worker.fetch(new Request(`https://example.test/api/status?id=${accepted.id}`, {
  headers: { cookie }
}), env);
check(response.status === 200, "Failed workflow status lookup must succeed");
const failedStatus = await response.json();
check(failedStatus.conclusion === "failure", "Failed workflow must report failure");
check(String(failedStatus.detail || "").includes("preverljivih virov"), "Terminal must surface the actual NO_TOPIC_SOURCES reason");
check(!String(failedStatus.detail || "").toLowerCase().includes("copilot"), "Terminal must ignore misleading shell source text");
workflowConclusion = "success";

response = await worker.fetch(new Request("https://example.test/api/history", {
  headers: { cookie }
}), env);
check(response.status === 200, "Cross-device history lookup must succeed");
const history = await response.json();
check(Array.isArray(history.runs), "History must return runs array");
check(history.runs.some((run) => run.id === accepted.id), "History must include dispatched terminal request");

response = await worker.fetch(new Request("https://example.test/api/logout", {
  method: "POST",
  headers: { cookie }
}), env);
check(response.status === 200, "Logout must succeed");
check((response.headers.get("set-cookie") || "").includes("Max-Age=0"), "Logout must clear cookie");

console.log("Worker terminal route matrix passed.");
