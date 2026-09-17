const OWNER = "DDAY2301";
const REPO = "blog-lab";
const WORKFLOW = "operator-terminal.yml";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer"
    }
  });
}

function b64url(bytes) {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function fromB64(value) {
  const raw = atob(value);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

function allowedEmails(env) {
  return String(env.ALLOWED_EMAILS || "")
    .split(",")
    .map((x) => x.trim().toLowerCase())
    .filter(Boolean);
}

function setupState(env) {
  const missing = [];
  if (!String(env.GITHUB_DISPATCH_TOKEN || "").trim()) missing.push("GITHUB_DISPATCH_TOKEN");
  if (!String(env.TERMINAL_COMMAND_KEY || "").trim()) missing.push("TERMINAL_COMMAND_KEY");
  if (allowedEmails(env).length === 0) missing.push("ALLOWED_EMAILS");
  return { ready: missing.length === 0, missing };
}

async function encryptPayload(env, value) {
  const keyBytes = fromB64(env.TERMINAL_COMMAND_KEY || "");
  if (keyBytes.length !== 32) throw new Error("TERMINAL_COMMAND_KEY must be base64 for 32 bytes");
  const key = await crypto.subtle.importKey("raw", keyBytes, "AES-GCM", false, ["encrypt"]);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plain = new TextEncoder().encode(JSON.stringify(value));
  const encrypted = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plain));
  const joined = new Uint8Array(iv.length + encrypted.length);
  joined.set(iv);
  joined.set(encrypted, iv.length);
  return b64url(joined);
}

async function identity(ctx, env) {
  if (!ctx.access) return null;
  let who;
  try {
    who = await ctx.access.getIdentity();
  } catch {
    return null;
  }
  const email = String(who?.email || "").trim().toLowerCase();
  const allowed = allowedEmails(env);
  if (!email || !allowed.length || !allowed.includes(email)) return null;
  return { email };
}

async function github(path, env, init = {}) {
  const token = String(env.GITHUB_DISPATCH_TOKEN || "").trim();
  if (!token) throw new Error("GITHUB_DISPATCH_TOKEN missing");
  const headers = new Headers(init.headers || {});
  headers.set("accept", "application/vnd.github+json");
  headers.set("x-github-api-version", "2022-11-28");
  headers.set("user-agent", "BlogLabPrivateTerminal/2.1");
  headers.set("authorization", `Bearer ${token}`);
  return fetch(`https://api.github.com${path}`, { ...init, headers });
}

async function findRun(requestId, env) {
  try {
    const r = await github(`/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/runs?event=workflow_dispatch&per_page=30`, env);
    if (!r.ok) return null;
    const data = await r.json();
    const expected = `Private Terminal · ${requestId}`;
    const run = (data.workflow_runs || []).find((x) => x.display_title === expected);
    if (!run) return { id: requestId, status: "queued", conclusion: null, run_url: null };
    return { id: requestId, status: run.status, conclusion: run.conclusion, run_url: run.html_url, updated_at: run.updated_at };
  } catch {
    return null;
  }
}

const PAGE = `<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blog Lab · Private Terminal</title><style>*{box-sizing:border-box}body{margin:0;background:#090b0f;color:#d7e0ea;font:15px ui-monospace,SFMono-Regular,Consolas,monospace}.wrap{max-width:1100px;margin:auto;padding:28px}.bar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:18px}.tag{color:#7ee787}.warn{color:#d29922}.panel{border:1px solid #30363d;background:#0d1117;border-radius:14px;overflow:hidden}.head{padding:12px 16px;border-bottom:1px solid #30363d;color:#8b949e}.screen{height:430px;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:10px}.entry{border-left:2px solid #30363d;padding:8px 12px}.entry b{color:#7ee787}.entry .meta{color:#8b949e;font-size:12px;margin-top:5px}.entry.fail b{color:#ff7b72}.composer{border-top:1px solid #30363d;padding:14px}.row{display:flex;gap:10px;flex-wrap:wrap}.row select,.row textarea,.row button{background:#161b22;color:#d7e0ea;border:1px solid #30363d;border-radius:8px;padding:10px}.row textarea{width:100%;min-height:90px;resize:vertical;margin-top:10px}.row button{background:#238636;border-color:#2ea043;cursor:pointer;font-weight:700}.row button:disabled{opacity:.5}.hint{color:#8b949e;font-size:12px;margin-top:8px}a{color:#58a6ff}</style></head><body><div class="wrap"><div class="bar"><div><strong>Blog Lab / private-terminal</strong><div class="tag" id="who">● preverjam dostop …</div><div id="setup" class="warn"></div></div><a href="https://dday2301.github.io/blog-lab/" rel="noreferrer">nazaj na blog ↗</a></div><div class="panel"><div class="head">authenticated operator channel · ukazi se pošiljajo AES-GCM šifrirano</div><div class="screen" id="screen"></div><div class="composer"><div class="row"><select id="mode"><option value="auto">Samodejno</option><option value="article">Članek</option><option value="site">Sprememba strani</option><option value="control">Nadzor agenta</option></select><select id="category"><option value="aktualno">Aktualno</option><option value="sport">Šport</option><option value="politika">Politika</option></select><button id="send">IZVEDI</button><textarea id="command" placeholder="Primer: Objavi članek o današnji temi … / Dodaj rubriko Projekti … / Ustavi objavljanje …"></textarea></div><div class="hint">Terminal hrani ukaze samo v tem brskalniku. Status izvedbe se bere iz GitHub Actions. Varnostnih datotek skozi ta kanal ni mogoče spreminjati.</div></div></div></div><script>
const $=s=>document.querySelector(s),KEY='bloglab-private-terminal-v2';
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function rows(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return []}}
function save(x){localStorage.setItem(KEY,JSON.stringify(x.slice(-60)))}
async function refreshRow(x){if(!x.id||x.status==='completed')return x;try{const r=await fetch('/api/status?id='+encodeURIComponent(x.id),{cache:'no-store'});if(r.ok){const s=await r.json();return {...x,...s}}}catch{}return x}
async function load(){const r=await fetch('/api/me',{cache:'no-store'});if(!r.ok){$('#who').textContent='● dostop zavrnjen';$('#screen').innerHTML='<div class="entry fail">Cloudflare Access ni aktiven ali ta račun ni dovoljen.</div>';return}const me=await r.json();$('#who').textContent='● '+me.email;$('#setup').textContent=me.ready?'':'Manjka nastavitev: '+me.missing.join(', ');let list=rows();list=await Promise.all(list.map(refreshRow));save(list);$('#screen').innerHTML=list.slice().reverse().map(x=>{const fail=x.conclusion&&x.conclusion!=='success';return '<div class="entry '+(fail?'fail':'')+'"><b>&gt; '+esc(x.command)+'</b><div>'+esc(x.status||'queued')+(x.conclusion?' / '+esc(x.conclusion):'')+(x.run_url?' · <a target="_blank" rel="noreferrer" href="'+esc(x.run_url)+'">GitHub run ↗</a>':'')+'</div><div class="meta">'+esc(x.mode)+' · '+esc(x.category)+' · '+esc(x.created_at)+'</div></div>'}).join('')||'<div class="entry">Terminal je pripravljen.</div>'}
$('#send').onclick=async()=>{const command=$('#command').value.trim();if(!command)return;$('#send').disabled=true;try{const body={command,mode:$('#mode').value,category:$('#category').value};const r=await fetch('/api/command',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok){alert(d.error+(d.missing?'\nManjka: '+d.missing.join(', '):''));return}const list=rows();list.push({id:d.id,command,mode:body.mode,category:body.category,created_at:new Date().toISOString(),status:'queued',conclusion:null,run_url:null});save(list);$('#command').value='';await load()}finally{$('#send').disabled=false}};
load();setInterval(load,4000);
</script></body></html>`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      const state = setupState(env);
      return json({ ok: true, worker: "blog-lab-private-terminal", ...state, access_required: true });
    }

    const user = await identity(ctx, env);
    if (!user) return new Response("Cloudflare Access required", { status: 403, headers: { "cache-control": "no-store" } });

    if (request.method === "GET" && url.pathname === "/") {
      return new Response(PAGE, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'" } });
    }

    if (request.method === "GET" && url.pathname === "/api/me") {
      return json({ email: user.email, ...setupState(env) });
    }

    if (request.method === "GET" && url.pathname === "/api/status") {
      const id = String(url.searchParams.get("id") || "").trim();
      if (!/^[0-9a-f-]{36}$/i.test(id)) return json({ error: "Neveljaven request id." }, 400);
      const run = await findRun(id, env);
      return json(run || { id, status: "unknown", conclusion: null, run_url: null });
    }

    if (request.method === "POST" && url.pathname === "/api/command") {
      const state = setupState(env);
      if (!state.ready) return json({ error: "Terminal še ni v celoti konfiguriran.", missing: state.missing }, 503);
      let body;
      try { body = await request.json(); } catch { return json({ error: "Neveljaven JSON." }, 400); }
      const command = String(body.command || "").trim();
      const mode = ["auto","article","site","control"].includes(body.mode) ? body.mode : "auto";
      const category = ["sport","politika","aktualno"].includes(body.category) ? body.category : "aktualno";
      if (!command || command.length > 4000) return json({ error: "Ukaz mora imeti 1–4000 znakov." }, 400);
      const requestId = crypto.randomUUID();
      const createdAt = new Date().toISOString();
      let privatePayload;
      try {
        privatePayload = await encryptPayload(env, { request_id: requestId, command, mode, category, actor: user.email, created_at: createdAt });
      } catch {
        return json({ error: "Šifriranje ukaza ni pravilno konfigurirano." }, 503);
      }
      const dispatch = await github(`/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, env, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ref: "main", inputs: { request_id: requestId, payload: privatePayload } })
      });
      if (!dispatch.ok) {
        const text = await dispatch.text().catch(() => "");
        return json({ error: "GitHub workflow se ni zagnal.", status: dispatch.status, detail: text.slice(0, 300) }, 502);
      }
      return json({ ok: true, id: requestId }, 202);
    }

    return new Response("Not found", { status: 404 });
  }
};
