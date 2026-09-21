from pathlib import Path

path = Path("terminal/worker/src/index.js")
text = path.read_text(encoding="utf-8")
text = text.replace("auth-v6.20-resilience", "auth-v6.23-command-idempotency")\ntext = text.replace("auth-v6.22-terminal-stability", "auth-v6.23-command-idempotency")


github_old = r'''async function github(path, env, init = {}) {
  const token = String(env.GITHUB_DISPATCH_TOKEN || "").trim();
  if (!token) throw new Error("GITHUB_DISPATCH_TOKEN missing");
  const headers = new Headers(init.headers || {});
  headers.set("accept", "application/vnd.github+json");
  headers.set("x-github-api-version", "2022-11-28");
  headers.set("user-agent", "BlogLabPrivateTerminal/3.0");
  headers.set("authorization", `Bearer ${token}`);
  return fetch(`https://api.github.com${path}`, { ...init, headers });
}'''
github_current = r'''async function github(path, env, init = {}) {
  const token = String(env.GITHUB_DISPATCH_TOKEN || "").trim();
  if (!token) throw new Error("GITHUB_DISPATCH_TOKEN missing");
  const headers = new Headers(init.headers || {});
  headers.set("accept", "application/vnd.github+json");
  headers.set("x-github-api-version", "2022-11-28");
  headers.set("user-agent", "BlogLabPrivateTerminal/3.1");
  headers.set("authorization", `Bearer ${token}`);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), GITHUB_API_TIMEOUT_MS);
  try {
    return await fetch(`https://api.github.com${path}`, { ...init, headers, signal: controller.signal });
  } catch (error) {
    if (controller.signal.aborted) {
      throw new Error(`GitHub API timeout after ${GITHUB_API_TIMEOUT_MS}ms for ${path}`);
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}'''
github_new = r'''async function github(path, env, init = {}) {
  const token = String(env.GITHUB_DISPATCH_TOKEN || "").trim();
  if (!token) {
    return new Response(JSON.stringify({ message: "GITHUB_DISPATCH_TOKEN missing", code: "GITHUB_TOKEN_MISSING" }), {
      status: 503,
      headers: { "content-type": "application/json" }
    });
  }
  const headers = new Headers(init.headers || {});
  headers.set("accept", "application/vnd.github+json");
  headers.set("x-github-api-version", "2022-11-28");
  headers.set("user-agent", "BlogLabPrivateTerminal/3.2");
  headers.set("authorization", `Bearer ${token}`);
  const method = String(init.method || "GET").toUpperCase();
  const maxAttempts = method === "GET" || method === "HEAD" ? 2 : 1;
  let lastError = "";
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), GITHUB_API_TIMEOUT_MS);
    try {
      const response = await fetch(`https://api.github.com${path}`, { ...init, headers, signal: controller.signal });
      if (
        response.ok
        || attempt >= maxAttempts
        || ![429, 500, 502, 503, 504].includes(response.status)
      ) {
        return response;
      }
      await response.arrayBuffer().catch(() => null);
      await new Promise((resolve) => setTimeout(resolve, 250 * attempt));
    } catch (error) {
      lastError = controller.signal.aborted
        ? `GitHub API timeout after ${GITHUB_API_TIMEOUT_MS}ms for ${path}`
        : String(error?.message || error || "GitHub request failed").slice(0, 240);
      if (attempt < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 250 * attempt));
        continue;
      }
    } finally {
      clearTimeout(timer);
    }
  }
  return new Response(JSON.stringify({
    message: lastError || "GitHub request failed",
    code: "GITHUB_NETWORK_TIMEOUT"
  }), {
    status: 599,
    headers: { "content-type": "application/json" }
  });
}'''
if "GITHUB_NETWORK_TIMEOUT" not in text:
    if github_old in text:
        text = text.replace(github_old, github_new, 1)
    elif github_current in text:
        text = text.replace(github_current, github_new, 1)
    else:
        raise SystemExit("GitHub helper marker not found")


health_old = r'''      let mediaUploadReady = false;
      if (String(env.GITHUB_DISPATCH_TOKEN || "").trim()) {
        try {
          const repoResponse = await github(`/repos/${OWNER}/${REPO}`, env);
          if (repoResponse.ok) {
            const repoInfo = await repoResponse.json();
            mediaUploadReady = Boolean(repoInfo?.permissions?.push);
          }
        } catch {}
      }'''
health_new = r'''      const mediaUploadReady = Boolean(String(env.GITHUB_DISPATCH_TOKEN || "").trim());'''
if health_old in text:
    text = text.replace(health_old, health_new, 1)

insert_after = '''function terminalChatFallback(message, error = null) {
  const question = String(message || "").trim();
  const lower = question.toLowerCase();
  const parts = [];
  parts.push("Pomočnik je prejel vprašanje: " + question);
  if (lower.includes("domena") || lower.includes("bloglab.eu") || lower.includes("neoserv") || lower.includes("dns")) {
    parts.push("Domena pri Neoservi sama po sebi ne poganja agenta 24/7. Domena samo usmeri promet. Za ta sistem mora bloglab.eu kazati na Cloudflare Worker za terminal in na GitHub Pages oziroma ustrezen host za javni blog.");
    parts.push("Za terminal uporabi DNS zapis proti Cloudflare Worker custom domainu. Za javni blog uporabi GitHub Pages custom domain ali Cloudflare proxy do obstoječe strani. Neoserv naj ostane registrar/DNS ali pa DNS prenesi na Cloudflare.");
  }
  if (lower.includes("objav") || lower.includes("član") || lower.includes("clan") || lower.includes("urnik")) {
    parts.push("Za objave preveri tri sloje: Publisher Agent, Publisher Guardian in 24h Article Learning. Če ni objave, najprej glej zadnji workflow run in data/agent-state.json. Guardian mora popraviti missed/deferred slot brez ročnega posega.");
  }
  if (lower.includes("worker") || lower.includes("cloudflare") || lower.includes("502") || lower.includes("ai")) {
    parts.push("Za Worker/AI težave preveri /health, /api/ai/diagnostics in zadnji Deploy Blog Lab Worker run. Če Workers AI pade, sistem mora uporabiti model fallback ali lokalni evidence fallback.");
  }
  parts.push("Ukaz, ki ga lahko pošlješ terminalu: opiši cilj jasno, npr. 'preveri zakaj ni današnje objave in popravi', ali 'pripravi DNS navodila za bloglab.eu'.");
  if (error) parts.push("Opomba: AI model trenutno ni vrnil odgovora, zato je prikazan varni fallback odgovor.");
  return parts.join("\\n\\n");
}
'''

operational_block = r'''
function withTimeout(promise, ms, label = "timeout") {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(label)), Math.max(1000, Number(ms) || 10000));
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

function terminalIntentWords(message) {
  return String(message || "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "");
}

function shouldUsePublicationOperationalCheck(message) {
  const lower = terminalIntentWords(message);
  const explicitExecution = /napisi vse|napiši vse|write all|publish all|catch ?up|nadoknad|objavi vse|izvedi objav/.test(lower)
    && /clan|article|post|objav|novic/.test(lower);
  if (explicitExecution) return false;
  const hasPublication = /objav|clan|article|post|publish|publisher|guardian|learning|urnik|raspored|schedule|slot|samodejn|automatic/.test(lower);
  const hasAction = /preglej|preveri|provjer|prover|check|verify|resi|resit|repair|fix|popravi|problem|zakaj|why|delovanje|status|test|diagnos/.test(lower);
  return hasPublication && hasAction;
}

function shouldUseDomainOperationalAnswer(message) {
  const lower = terminalIntentWords(message);
  return /(dns|domain|domena|bloglab\.eu|neoserv|github pages|cname|a zapis|a record|terminal\.bloglab)/.test(lower);
}

function shouldUseTerminalDiagnostics(message) {
  const lower = terminalIntentWords(message);
  return /(terminal|chatbot|pomocnik|assistant|worker|cloudflare|github|dispatch|workflow|komand|ukaz|command|api|health|timeout|502|test)/.test(lower)
    && /(preveri|provjer|prover|check|verify|test|diagnos|status|delovanje|working|popravi|fix|repair|resi|problem)/.test(lower);
}

function ljubljanaNowParts() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Ljubljana",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).formatToParts(new Date()).reduce((acc, part) => {
    acc[part.type] = part.value;
    return acc;
  }, {});
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    time: `${parts.hour}:${parts.minute}`
  };
}

function slotId(date, slot) {
  return `${date}|${slot.time}|${slot.category}`;
}

function defaultSchedule() {
  return {
    timezone: "Europe/Ljubljana",
    slots: [
      { time: "08:17", category: "sport" },
      { time: "13:27", category: "politika" },
      { time: "19:43", category: "aktualno" }
    ]
  };
}

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

function publicationOperationalText({ state, status, learning, control, dueSlots, missingSlots, dispatched, dispatchError, now }) {
  const done = safeArray(state?.scheduled_slots_done);
  const deferred = safeArray(state?.scheduled_slots_deferred);
  const schedule = control?.schedule || defaultSchedule();
  const lines = [];
  lines.push("Operativni pregled objav je izveden neposredno iz repozitorija.");
  lines.push(`Čas Ljubljana: ${now.date} ${now.time}`);
  lines.push(`Agent: ${control?.enabled === false ? "ustavljen" : "aktiven"} · način: ${control?.publish_mode || "automatic"}`);
  lines.push(`Status: ${status?.status || state?.last_error || "unknown"} · pisec: ${status?.writer_mode || state?.writer_mode || "unknown"}`);
  lines.push(`Danes: skupaj ${state?.posts_today ?? status?.posts_today ?? "?"}, samodejno ${state?.scheduled_posts_today ?? status?.scheduled_posts_today ?? "?"}, ročno ${state?.manual_posts_today ?? status?.manual_posts_today ?? "?"}.`);
  lines.push(`Urnik: ${safeArray(schedule.slots).map((slot) => `${slot.time} ${slot.category}`).join(" · ")}`);
  lines.push(`Zapadli sloti: ${dueSlots.length ? dueSlots.map((slot) => `${slot.time} ${slot.category}`).join(" · ") : "še ni zapadlih slotov"}.`);
  lines.push(`Opravljeni sloti: ${done.length ? done.join(" · ") : "nič"}.`);
  if (deferred.length) lines.push(`Deferred: ${deferred.join(" · ")}.`);
  lines.push(`Learning: ${learning?.status || "unknown"}${learning?.updated_at ? ` · ${learning.updated_at}` : ""}.`);
  if (missingSlots.length || deferred.length || status?.status === "failed" || state?.last_error) {
    if (dispatched) {
      lines.push("Popravek: sprožil sem publisher catch-up/guardian pot. Če je GitHub v queue, počakaj nekaj minut in ponovno preveri status.");
    } else if (dispatchError) {
      lines.push("Popravek ni bil sprožen: " + dispatchError);
    } else {
      lines.push("Popravek ni potreben ali trenutno ni varnega missed/deferred slota za catch-up.");
    }
  } else {
    lines.push("Rezultat: ni zaznane blokade objav. Naslednji zapadli slot bo prevzel Publisher/Guardian.");
  }
  return lines.join("\n");
}

async function terminalPublicationOperationalAnswer(env) {
  const now = ljubljanaNowParts();
  const [state, status, learning, control] = await Promise.all([
    readRepoJson("data/agent-state.json", env),
    readRepoJson("public/data/agent-status.json", env),
    readRepoJson("public/data/article-learning-status.json", env),
    readRepoJson("data/agent-control.json", env)
  ]);
  const schedule = control?.schedule || defaultSchedule();
  const dueSlots = safeArray(schedule.slots).filter((slot) => String(slot.time || "") <= now.time);
  const done = safeArray(state?.scheduled_slots_done);
  const deferred = safeArray(state?.scheduled_slots_deferred);
  const missingSlots = dueSlots.filter((slot) => !done.includes(slotId(now.date, slot)));
  let dispatched = false;
  let dispatchError = "";
  const shouldDispatch = Boolean(missingSlots.length || deferred.length || status?.status === "failed" || state?.last_error);
  if (shouldDispatch) {
    try {
      await withTimeout(dispatchPublisherCatchup(env), 9000, "publisher_catchup_dispatch_timeout");
      dispatched = true;
    } catch (error) {
      dispatchError = sanitizeAiError(error).message || String(error || "dispatch failed");
    }
  }
  return {
    mode: "operational_publication_check",
    text: publicationOperationalText({ state: state || {}, status: status || {}, learning: learning || {}, control: control || {}, dueSlots, missingSlots, dispatched, dispatchError, now })
  };
}

async function terminalDiagnosticsAnswer(env) {
  const [snapshot, runs] = await Promise.all([
    readAgentSnapshot(env).catch(() => null),
    recentRuns(env).catch(() => [])
  ]);
  const latest = safeArray(runs).slice(0, 5).map((run) => `${run.status}/${run.conclusion || "-"} ${run.created_at || ""}`).join(" · ");
  return {
    mode: "operational_terminal_diagnostics",
    text: [
      "Terminal diagnostika:",
      `Setup: ${setupState(env).ready ? "ready" : "missing " + setupState(env).missing.join(", ")}`,
      snapshot?.summary ? `Agent: ${snapshot.summary}` : "Agent: snapshot ni na voljo",
      latest ? `Zadnji terminal runi: ${latest}` : "Zadnji terminal runi: ni podatkov",
      "Varovalke: /api/chat ima lokalni fallback, /api/command vrača GitHub dispatch status/detail/hint, publisher ima catch-up pot."
    ].join("\n")
  };
}

function terminalDomainAnswer() {
  return {
    mode: "operational_domain_dns",
    text: [
      "DNS za obstoječo GitHub Pages stran:",
      "A @ 185.199.108.153",
      "A @ 185.199.109.153",
      "A @ 185.199.110.153",
      "A @ 185.199.111.153",
      "CNAME www dday2301.github.io",
      "V GitHub Pages mora biti custom domain bloglab.eu. Ko DNS check uspe, vklopi Enforce HTTPS.",
      "Terminal ostane na Cloudflare Workerju; za terminal.bloglab.eu bomo dodali ločen Worker custom domain, ko javni blog stabilno deluje."
    ].join("\n")
  };
}

async function terminalOperationalAnswer(env, message, email) {
  if (shouldUsePublicationOperationalCheck(message)) return terminalPublicationOperationalAnswer(env, message, email);
  if (shouldUseDomainOperationalAnswer(message)) return terminalDomainAnswer(env, message, email);
  if (shouldUseTerminalDiagnostics(message)) return terminalDiagnosticsAnswer(env, message, email);
  return null;
}
'''

if "function terminalOperationalAnswer(" not in text:
    if insert_after not in text:
        raise SystemExit("terminalChatFallback marker not found")
    text = text.replace(insert_after, insert_after + operational_block + "\n", 1)

old = '''async function terminalChatAssistant(env, message, email) {
  const system = ['''
new = '''async function terminalChatAssistant(env, message, email) {
  let operational = null;
  try {
    operational = await withTimeout(
      terminalOperationalAnswer(env, message, email),
      12000,
      "terminal_operational_timeout"
    );
  } catch (error) {
    return {
      mode: "fallback",
      text: terminalChatFallback(message, error),
      error: sanitizeAiError(error)
    };
  }
  if (operational) return operational;
  const system = ['''
if old in text and "const operational = await terminalOperationalAnswer" not in text:
    text = text.replace(old, new, 1)
elif "terminal_operational_timeout" not in text:
    raise SystemExit("terminalChatAssistant marker not found")

old_ai = '''    const result = await runWorkersAiWithRetry(env, request, 2, {
      purpose: "terminal_chat",
      cacheKey: "terminal-chat-" + b64urlText(String(message || "").slice(0, 400)).slice(0, 80)
    });'''
new_ai = '''    const result = await withTimeout(runWorkersAiWithRetry(env, request, 2, {
      purpose: "terminal_chat",
      cacheKey: "terminal-chat-" + b64urlText(String(message || "").slice(0, 400)).slice(0, 80)
    }), 14000, "terminal_chat_ai_timeout");'''
if old_ai in text:
    text = text.replace(old_ai, new_ai, 1)
elif "terminal_chat_ai_timeout" not in text:
    raise SystemExit("terminal AI timeout marker not found")

old_dispatch = 'return json({ error: "GitHub workflow se ni zagnal.", status: dispatch.status, detail: text.slice(0, 300) }, 502);'
new_dispatch = '''const detail = text.slice(0, 900);
        const hint = dispatch.status === 401 || dispatch.status === 403
          ? "GITHUB_DISPATCH_TOKEN nima dovoljenja za Actions workflow dispatch ali repo write."
          : dispatch.status === 404
          ? "Workflow operator-terminal.yml ali repozitorij ni dostopen s tem tokenom."
          : dispatch.status === 422
          ? "GitHub je zavrnil workflow_dispatch payload/ref; preveri main branch in workflow inputs."
          : "GitHub dispatch endpoint je vrnil napako.";
        return json({ error: "GitHub workflow se ni zagnal.", code: "GITHUB_WORKFLOW_DISPATCH_FAILED", status: dispatch.status, detail, hint, workflow: WORKFLOW, request_id: requestId }, 502);'''
if old_dispatch in text:
    text = text.replace(old_dispatch, new_dispatch, 1)
elif "GITHUB_WORKFLOW_DISPATCH_FAILED" not in text:
    raise SystemExit("dispatch diagnostic marker not found")


ai_retry_old = r'''    || text.includes("invalid request")
    || text.includes("authentication")'''
ai_retry_new = r'''    || text.includes("authentication")'''
if ai_retry_old in text:
    text = text.replace(ai_retry_old, ai_retry_new, 1)

ai_deadline_old = r'''  const gatewayOptions = aiGatewayOptions(env, purpose, cacheKey);
  for (const model of workersAiModelCandidates(env)) {
    for (let attempt = 1; attempt <= total; attempt += 1) {
      try {
        const result = await env.AI.run(model, request, gatewayOptions);'''
ai_deadline_new = r'''  const gatewayOptions = aiGatewayOptions(env, purpose, cacheKey);
  const deadline = Date.now() + Math.max(5000, Math.min(Number(options.timeoutMs || 30000) || 30000, 45000));
  for (const model of workersAiModelCandidates(env)) {
    for (let attempt = 1; attempt <= total; attempt += 1) {
      const remaining = deadline - Date.now();
      if (remaining <= 1000) break;
      try {
        const result = await withTimeout(
          env.AI.run(model, request, gatewayOptions),
          Math.min(12000, Math.max(1000, remaining)),
          "workers_ai_model_timeout"
        );'''
if "workers_ai_model_timeout" not in text:
    if ai_deadline_old not in text:
        raise SystemExit("Workers AI retry marker not found")
    text = text.replace(ai_deadline_old, ai_deadline_new, 1)

recent_runs_old = r'''    for (const run of data.workflow_runs || []) {'''
recent_runs_new = r'''    for (const run of (data.workflow_runs || []).slice(0, 12)) {'''
if recent_runs_old in text:
    text = text.replace(recent_runs_old, recent_runs_new, 1)

failure_detail_old = r'''        detail: run.conclusion === "failure" ? await runFailureDetail(run.id, env) : ""'''
failure_detail_new = r'''        detail: run.conclusion === "failure"
          ? (out.length < 4 ? await runFailureDetail(run.id, env) : "GitHub run failed.")
          : ""'''
if failure_detail_old in text:
    text = text.replace(failure_detail_old, failure_detail_new, 1)

poll_old = r'''async function refreshRow(x){if(!x.id||x.status==='completed')return x;try{const r=await fetch('/api/status?id='+encodeURIComponent(x.id),{cache:'no-store'});if(r.status===401){location.replace('/');return x}if(r.ok){const s=await r.json();return {...x,...s}}}catch{}return x}'''
poll_new = r'''async function refreshRow(x){if(!x.id||x.status==='completed'||x.status==='unknown')return x;try{const r=await fetch('/api/status?id='+encodeURIComponent(x.id),{cache:'no-store'});if(r.status===401){location.replace('/');return x}if(r.ok){const s=await r.json();const age=Date.now()-Date.parse(x.created_at||0);if(s.status==='queued'&&!s.run_url&&Number.isFinite(age)&&age>12*60*1000){return {...x,...s,status:'unknown',detail:'GitHub run po 12 minutah ni bil najden. Ukaz lahko varno pošlješ ponovno.'}}return {...x,...s}}}catch{}return x}'''
if poll_old in text:
    text = text.replace(poll_old, poll_new, 1)


# Restore retry-safe command idempotency if a future Worker edit removes it.
idempotency_header_old = r'''const $=s=>document.querySelector(s),KEY='bloglab-private-terminal-v3';
async function fetchTimed'''
idempotency_header_new = r'''const $=s=>document.querySelector(s),KEY='bloglab-private-terminal-v3',PENDING_KEY='bloglab-terminal-pending-v1';
function pendingRequests(){try{const now=Date.now(),x=JSON.parse(localStorage.getItem(PENDING_KEY)||'[]');return Array.isArray(x)?x.filter(v=>v&&v.id&&v.sig&&now-Number(v.at||0)<20*60*1000).slice(-10):[]}catch{return []}}
function requestSignature(body){return JSON.stringify([body.command,body.mode,body.category])}
function requestIdForBody(body){const sig=requestSignature(body),items=pendingRequests(),found=items.find(x=>x.sig===sig);if(found){localStorage.setItem(PENDING_KEY,JSON.stringify(items));return found.id}const id=crypto.randomUUID(),next=[...items,{id,sig,at:Date.now()}].slice(-10);localStorage.setItem(PENDING_KEY,JSON.stringify(next));return id}
function clearPendingRequest(id){try{localStorage.setItem(PENDING_KEY,JSON.stringify(pendingRequests().filter(x=>x.id!==id)))}catch{}}
async function fetchTimed'''
if "PENDING_KEY='bloglab-terminal-pending-v1'" not in text:
    if idempotency_header_old not in text:
        raise SystemExit("terminal idempotency header marker not found")
    text = text.replace(idempotency_header_old, idempotency_header_new, 1)

idempotency_send_old = r'''$('#send').onclick=async()=>{const command=$('#command').value.trim();if(!command)return;$('#send').disabled=true;try{const body={command,mode:$('#mode').value,category:$('#category').value};const r='''
idempotency_send_new = r'''$('#send').onclick=async()=>{const command=$('#command').value.trim();if(!command)return;$('#send').disabled=true;let clientRequestId='';try{const body={command,mode:$('#mode').value,category:$('#category').value};clientRequestId=requestIdForBody(body);body.client_request_id=clientRequestId;const r='''
if "clientRequestId=requestIdForBody(body)" not in text:
    if idempotency_send_old not in text:
        raise SystemExit("terminal idempotency send marker not found")
    text = text.replace(idempotency_send_old, idempotency_send_new, 1)

idempotency_401_old = r'''if(r.status===401){location.replace('/');return}const d=await r.json();'''
idempotency_401_new = r'''if(r.status===401){clearPendingRequest(clientRequestId);location.replace('/');return}const d=await r.json();'''
if "clearPendingRequest(clientRequestId);location.replace('/')" not in text:
    if idempotency_401_old not in text:
        raise SystemExit("terminal idempotency 401 marker not found")
    text = text.replace(idempotency_401_old, idempotency_401_new, 1)

idempotency_error_old = r'''if(!r.ok){const parts=[d.error||'Ukaz ni uspel.'];'''
idempotency_error_new = r'''if(!r.ok){clearPendingRequest(clientRequestId);const parts=[d.error||'Ukaz ni uspel.'];'''
if "if(!r.ok){clearPendingRequest(clientRequestId);" not in text:
    if idempotency_error_old not in text:
        raise SystemExit("terminal idempotency error marker not found")
    text = text.replace(idempotency_error_old, idempotency_error_new, 1)

idempotency_success_old = r'''alert(parts.join('\\n'));return}const list=rows();'''
idempotency_success_new = r'''alert(parts.join('\\n'));return}clearPendingRequest(clientRequestId);const list=rows();'''
if "clearPendingRequest(clientRequestId);const list=rows();" not in text:
    if idempotency_success_old not in text:
        raise SystemExit("terminal idempotency success marker not found")
    text = text.replace(idempotency_success_old, idempotency_success_new, 1)

idempotency_server_old = r'''      const requestId = crypto.randomUUID();
      const createdAt = new Date().toISOString();'''
idempotency_server_new = r'''      const clientRequestId = String(body.client_request_id || "").trim().toLowerCase();
      const requestId = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(clientRequestId)
        ? clientRequestId
        : crypto.randomUUID();
      const createdAt = new Date().toISOString();'''
if "const clientRequestId = String(body.client_request_id" not in text:
    if idempotency_server_old not in text:
        raise SystemExit("terminal idempotency server marker not found")
    text = text.replace(idempotency_server_old, idempotency_server_new, 1)

path.write_text(text, encoding="utf-8")
print("Terminal agent hardening applied")
