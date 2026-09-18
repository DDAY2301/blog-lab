const OWNER = "DDAY2301";
const REPO = "blog-lab";
const WORKFLOW = "operator-terminal.yml";
const SESSION_COOKIE = "bloglab_session";
const SESSION_TTL_SECONDS = 60 * 60 * 12;
const AUTHORIZED_USERS = Object.freeze({
  "dan.grmusa@gmail.com": "DAN_LOGIN_PASSWORD",
  "maj@klemenc.org": "MAJ_LOGIN_PASSWORD"
});

function loginPassword(env, email) {
  const secretName = AUTHORIZED_USERS[email];
  if (!secretName) return "";
  const direct = String(env[secretName] || "").trim();
  if (direct) return direct;
  // Both approved users intentionally share the same password.
  // Fall back to the other configured login secret so a missing duplicate
  // secret cannot break login on a fresh device.
  const alternate = secretName === "DAN_LOGIN_PASSWORD" ? "MAJ_LOGIN_PASSWORD" : "DAN_LOGIN_PASSWORD";
  return String(env[alternate] || "").trim();
}

function securityHeaders(extra = {}) {
  return {
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    ...extra
  };
}

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: securityHeaders({
      "content-type": "application/json; charset=utf-8",
      ...extraHeaders
    })
  });
}

function html(body, status = 200, extraHeaders = {}) {
  return new Response(body, {
    status,
    headers: securityHeaders({
      "content-type": "text/html; charset=utf-8",
      "content-security-policy": "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
      ...extraHeaders
    })
  });
}

function b64url(bytes) {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function b64urlText(text) {
  return b64url(new TextEncoder().encode(text));
}

function fromB64(value) {
  const raw = atob(value);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

function fromB64url(value) {
  const normalized = String(value || "").replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - (normalized.length % 4 || 4)) % 4);
  return fromB64(padded);
}

function timingSafeEqual(a, b) {
  const left = typeof a === "string" ? new TextEncoder().encode(a) : a;
  const right = typeof b === "string" ? new TextEncoder().encode(b) : b;
  const length = Math.max(left.length, right.length);
  let diff = left.length ^ right.length;
  for (let i = 0; i < length; i++) diff |= (left[i] || 0) ^ (right[i] || 0);
  return diff === 0;
}

function setupState(env) {
  const missing = [];
  if (!String(env.GITHUB_DISPATCH_TOKEN || "").trim()) missing.push("GITHUB_DISPATCH_TOKEN");
  if (!String(env.TERMINAL_COMMAND_KEY || "").trim()) missing.push("TERMINAL_COMMAND_KEY");
  const hasLoginPassword =
    String(env.DAN_LOGIN_PASSWORD || "").trim().length >= 8 ||
    String(env.MAJ_LOGIN_PASSWORD || "").trim().length >= 8;
  if (!hasLoginPassword) missing.push("LOGIN_PASSWORD");
  return { ready: missing.length === 0, missing };
}

async function deriveSessionKey(env) {
  const terminalKey = String(env.TERMINAL_COMMAND_KEY || "").trim();
  let seed;
  try {
    const raw = terminalKey ? fromB64(terminalKey) : new Uint8Array();
    if (raw.length === 32) {
      seed = raw;
    }
  } catch {}
  if (!seed) {
    const fallback = loginPassword(env, "dan.grmusa@gmail.com") || loginPassword(env, "maj@klemenc.org");
    if (fallback.length < 8) throw new Error("Login password is not configured");
    seed = new TextEncoder().encode(`blog-lab-session-v3\n${fallback}`);
  }
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", seed));
  return crypto.subtle.importKey(
    "raw",
    digest,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
}

async function signSession(env, email) {
  const payload = b64urlText(JSON.stringify({
    email,
    exp: Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS
  }));
  const key = await deriveSessionKey(env);
  const signature = new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payload)));
  return `${payload}.${b64url(signature)}`;
}

async function verifySession(env, token) {
  try {
    const [payloadPart, signaturePart, extra] = String(token || "").split(".");
    if (!payloadPart || !signaturePart || extra) return null;
    const key = await deriveSessionKey(env);
    const valid = await crypto.subtle.verify(
      "HMAC",
      key,
      fromB64url(signaturePart),
      new TextEncoder().encode(payloadPart)
    );
    if (!valid) return null;
    const payload = JSON.parse(new TextDecoder().decode(fromB64url(payloadPart)));
    const email = String(payload?.email || "").trim().toLowerCase();
    const exp = Number(payload?.exp || 0);
    if (!AUTHORIZED_USERS[email] || !Number.isFinite(exp) || exp <= Math.floor(Date.now() / 1000)) return null;
    return { email };
  } catch {
    return null;
  }
}

function cookieValue(request, name) {
  const cookies = String(request.headers.get("cookie") || "").split(";");
  for (const part of cookies) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return rest.join("=");
  }
  return "";
}

async function identity(request, env) {
  return verifySession(env, cookieValue(request, SESSION_COOKIE));
}

function sessionCookie(token) {
  return `${SESSION_COOKIE}=${token}; Path=/; Max-Age=${SESSION_TTL_SECONDS}; HttpOnly; Secure; SameSite=Lax`;
}

function clearSessionCookie() {
  return `${SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
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

async function github(path, env, init = {}) {
  const token = String(env.GITHUB_DISPATCH_TOKEN || "").trim();
  if (!token) throw new Error("GITHUB_DISPATCH_TOKEN missing");
  const headers = new Headers(init.headers || {});
  headers.set("accept", "application/vnd.github+json");
  headers.set("x-github-api-version", "2022-11-28");
  headers.set("user-agent", "BlogLabPrivateTerminal/3.0");
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

const LOGIN_PAGE = `<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blog Lab · Prijava</title><style>*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f7f4ee;color:#17211b;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.card{width:min(92vw,460px);padding:34px;border:1px solid #d8ddd9;border-radius:22px;background:white;box-shadow:0 24px 70px rgba(21,41,31,.12)}.mark{width:56px;height:56px;border-radius:16px;background:#167349;color:white;display:grid;place-items:center;font-size:26px;font-weight:800;margin-bottom:20px}.eyebrow{font-size:13px;font-weight:800;letter-spacing:.16em;color:#517063;text-transform:uppercase}h1{font-size:34px;line-height:1.1;margin:8px 0 10px}p{color:#637169;line-height:1.55}.field{margin-top:16px}label{display:block;font-weight:750;margin-bottom:7px}input{width:100%;height:46px;border:1px solid #cbd3ce;border-radius:11px;padding:0 13px;font-size:15px}input:focus{outline:2px solid #16734933;border-color:#167349}.actions{display:flex;gap:10px;margin-top:22px}button,a.btn{min-height:44px;padding:0 18px;border-radius:11px;border:1px solid #167349;background:#167349;color:#fff;font-weight:800;display:inline-flex;align-items:center;justify-content:center;text-decoration:none;cursor:pointer}.btn.secondary{background:#fff;color:#167349}.error{min-height:22px;margin-top:12px;color:#a33;font-weight:650}.hint{font-size:12px;margin-top:18px;color:#7b877f}</style></head><body><main class="card"><div class="mark">B</div><div class="eyebrow">Blog Lab</div><h1>Zasebni terminal</h1><p>Prijava je dovoljena samo pooblaščenima operaterjema. Dostop deluje na brezplačnem Workerju in ne potrebuje Cloudflare Zero Trust naročnine.</p><form id="login"><div class="field"><label for="email">E-pošta</label><input id="email" type="email" autocomplete="username" required placeholder="ime@domena.si"></div><div class="field"><label for="password">Geslo</label><input id="password" type="password" autocomplete="current-password" required></div><div class="error" id="error"></div><div class="actions"><button id="submit" type="submit">Prijava</button><a class="btn secondary" href="https://dday2301.github.io/blog-lab/">Nazaj</a></div></form><div class="hint">Seja poteče po 12 urah. Geslo ni shranjeno v brskalniku ali GitHub repozitoriju.</div></main><script>const f=document.querySelector('#login'),e=document.querySelector('#error'),b=document.querySelector('#submit');f.addEventListener('submit',async(ev)=>{ev.preventDefault();e.textContent='';b.disabled=true;try{const r=await fetch('/api/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:document.querySelector('#email').value,password:document.querySelector('#password').value})});const d=await r.json().catch(()=>({}));if(!r.ok){e.textContent=d.error||'Prijava ni uspela.';return}location.replace('/')}catch{e.textContent='Povezava s terminalom ni uspela.'}finally{b.disabled=false}});</script></body></html>`;

const PAGE = `<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blog Lab · Private Terminal</title><style>*{box-sizing:border-box}body{margin:0;background:#090b0f;color:#d7e0ea;font:15px ui-monospace,SFMono-Regular,Consolas,monospace}.wrap{max-width:1100px;margin:auto;padding:28px}.bar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:18px}.barlinks{display:flex;gap:12px;align-items:center}.bar button{background:transparent;color:#8b949e;border:1px solid #30363d;border-radius:8px;padding:8px 10px;cursor:pointer}.tag{color:#7ee787}.warn{color:#d29922}.panel{border:1px solid #30363d;background:#0d1117;border-radius:14px;overflow:hidden}.head{padding:12px 16px;border-bottom:1px solid #30363d;color:#8b949e}.screen{height:430px;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:10px}.entry{border-left:2px solid #30363d;padding:8px 12px}.entry b{color:#7ee787}.entry .meta{color:#8b949e;font-size:12px;margin-top:5px}.entry.fail b{color:#ff7b72}.composer{border-top:1px solid #30363d;padding:14px}.row{display:flex;gap:10px;flex-wrap:wrap}.row select,.row textarea,.row button{background:#161b22;color:#d7e0ea;border:1px solid #30363d;border-radius:8px;padding:10px}.row textarea{width:100%;min-height:90px;resize:vertical;margin-top:10px}.row button{background:#238636;border-color:#2ea043;cursor:pointer;font-weight:700}.row button:disabled{opacity:.5}.hint{color:#8b949e;font-size:12px;margin-top:8px}a{color:#58a6ff}</style></head><body><div class="wrap"><div class="bar"><div><strong>Blog Lab / private-terminal</strong><div class="tag" id="who">● preverjam sejo …</div><div id="setup" class="warn"></div></div><div class="barlinks"><a href="https://dday2301.github.io/blog-lab/">blog ↗</a><button id="logout">odjava</button></div></div><div class="panel"><div class="head">private operator channel · ukazi se pošiljajo AES-GCM šifrirano</div><div class="screen" id="screen"></div><div class="composer"><div class="row"><select id="mode"><option value="auto">Samodejno</option><option value="article">Članek</option><option value="site">Sprememba strani</option><option value="control">Nadzor agenta</option></select><select id="category"><option value="aktualno">Aktualno</option><option value="sport">Šport</option><option value="politika">Politika</option></select><button id="send">IZVEDI</button><textarea id="command" placeholder="Primer: Objavi članek o današnji temi … / Dodaj rubriko Projekti … / Ustavi objavljanje …"></textarea></div><div class="hint">Terminal hrani zgodovino ukazov samo v tem brskalniku. Status izvedbe se bere iz GitHub Actions. Varnostnih datotek skozi ta kanal ni mogoče spreminjati.</div></div></div></div><script>
const $=s=>document.querySelector(s),KEY='bloglab-private-terminal-v3';
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function rows(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return []}}
function save(x){localStorage.setItem(KEY,JSON.stringify(x.slice(-60)))}
async function refreshRow(x){if(!x.id||x.status==='completed')return x;try{const r=await fetch('/api/status?id='+encodeURIComponent(x.id),{cache:'no-store'});if(r.status===401){location.replace('/');return x}if(r.ok){const s=await r.json();return {...x,...s}}}catch{}return x}
async function load(){const r=await fetch('/api/me',{cache:'no-store'});if(r.status===401){location.replace('/');return}if(!r.ok){$('#who').textContent='● napaka seje';return}const me=await r.json();$('#who').textContent='● '+me.email;$('#setup').textContent=me.ready?'':'Manjka nastavitev: '+me.missing.join(', ');let list=rows();list=await Promise.all(list.map(refreshRow));save(list);$('#screen').innerHTML=list.slice().reverse().map(x=>{const fail=x.conclusion&&x.conclusion!=='success';return '<div class="entry '+(fail?'fail':'')+'"><b>&gt; '+esc(x.command)+'</b><div>'+esc(x.status||'queued')+(x.conclusion?' / '+esc(x.conclusion):'')+(x.run_url?' · <a target="_blank" rel="noreferrer" href="'+esc(x.run_url)+'">GitHub run ↗</a>':'')+'</div><div class="meta">'+esc(x.mode)+' · '+esc(x.category)+' · '+esc(x.created_at)+'</div></div>'}).join('')||'<div class="entry">Terminal je pripravljen.</div>'}
$('#send').onclick=async()=>{const command=$('#command').value.trim();if(!command)return;$('#send').disabled=true;try{const body={command,mode:$('#mode').value,category:$('#category').value};const r=await fetch('/api/command',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});if(r.status===401){location.replace('/');return}const d=await r.json();if(!r.ok){alert(d.error+(d.missing?'\\nManjka: '+d.missing.join(', '):''));return}const list=rows();list.push({id:d.id,command,mode:body.mode,category:body.category,created_at:new Date().toISOString(),status:'queued',conclusion:null,run_url:null});save(list);$('#command').value='';await load()}finally{$('#send').disabled=false}};
$('#logout').onclick=async()=>{await fetch('/api/logout',{method:'POST'}).catch(()=>{});location.replace('/')};
load();setInterval(load,4000);
</script></body></html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      const state = setupState(env);
      const userReadiness = [
        loginPassword(env, "dan.grmusa@gmail.com").length >= 8,
        loginPassword(env, "maj@klemenc.org").length >= 8
      ];
      const authReady = userReadiness.every(Boolean);
      return json({
        ok: true,
        worker: "blog-lab",
        version: "auth-v3-cross-device",
        ready: state.ready,
        auth_ready: authReady,
        authorized_users_ready: userReadiness.filter(Boolean).length,
        auth_mode: "built-in-session",
        free_tier_compatible: true
      });
    }

    if (request.method === "POST" && url.pathname === "/api/login") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "Neveljavna prijavna zahteva." }, 400); }
      const email = String(body?.email || "").trim().toLowerCase();
      const password = String(body?.password || "");
      const secretName = AUTHORIZED_USERS[email];
      const expected = loginPassword(env, email);
      const configured = expected.length >= 8;
      const valid = Boolean(secretName && configured && password.length && timingSafeEqual(password, expected));
      if (!valid) {
        await new Promise((resolve) => setTimeout(resolve, 650));
        return json({ error: "Napačen e-poštni naslov ali geslo." }, 401);
      }
      let token;
      try { token = await signSession(env, email); } catch { return json({ error: "Terminal še ni pravilno konfiguriran." }, 503); }
      return json({ ok: true, email }, 200, { "set-cookie": sessionCookie(token) });
    }

    if (request.method === "POST" && url.pathname === "/api/logout") {
      return json({ ok: true }, 200, { "set-cookie": clearSessionCookie() });
    }

    const user = await identity(request, env);

    if (request.method === "GET" && url.pathname === "/") {
      return html(user ? PAGE : LOGIN_PAGE);
    }

    if (!user) return json({ error: "Prijava je potrebna." }, 401);

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
      const mode = ["auto", "article", "site", "control"].includes(body.mode) ? body.mode : "auto";
      const category = ["sport", "politika", "aktualno"].includes(body.category) ? body.category : "aktualno";
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

    return new Response("Not found", { status: 404, headers: securityHeaders() });
  }
};