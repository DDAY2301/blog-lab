from pathlib import Path

path = Path("terminal/worker/src/index.js")
text = path.read_text(encoding="utf-8")

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
  const operational = await terminalOperationalAnswer(env, message, email);
  if (operational) return operational;
  const system = ['''
if old in text and "const operational = await terminalOperationalAnswer" not in text:
    text = text.replace(old, new, 1)
elif "const operational = await terminalOperationalAnswer" not in text:
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

path.write_text(text, encoding="utf-8")
print("Terminal agent hardening applied")
