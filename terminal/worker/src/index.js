const OWNER = "DDAY2301";
const REPO = "blog-lab";
const WORKFLOW = "operator-terminal.yml";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" } });
}
function b64url(bytes) {
  let s = ""; for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}
function fromB64(value) {
  const raw = atob(value); const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i); return out;
}
async function encryptPayload(env, value) {
  const keyBytes = fromB64(env.TERMINAL_COMMAND_KEY || "");
  if (keyBytes.length !== 32) throw new Error("TERMINAL_COMMAND_KEY must be base64 for 32 bytes");
  const key = await crypto.subtle.importKey("raw", keyBytes, "AES-GCM", false, ["encrypt"]);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plain = new TextEncoder().encode(JSON.stringify(value));
  const encrypted = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plain));
  const joined = new Uint8Array(iv.length + encrypted.length); joined.set(iv); joined.set(encrypted, iv.length);
  return b64url(joined);
}
async function identity(ctx, env) {
  if (!ctx.access) return null;
  const who = await ctx.access.getIdentity();
  const email = String(who?.email || "").trim().toLowerCase();
  const allowed = String(env.ALLOWED_EMAILS || "").split(",").map(x => x.trim().toLowerCase()).filter(Boolean);
  if (!email || !allowed.includes(email)) return null;
  return { email };
}
async function github(path, env, init = {}) {
  const headers = new Headers(init.headers || {});
  headers.set("accept", "application/vnd.github+json");
  headers.set("x-github-api-version", "2026-03-10");
  headers.set("user-agent", "BlogLabPrivateTerminal/1.0");
  headers.set("authorization", `Bearer ${env.GITHUB_DISPATCH_TOKEN}`);
  return fetch(`https://api.github.com${path}`, { ...init, headers });
}
async function refresh(record, env) {
  if (!record.run_id || record.status === "completed") return record;
  try {
    const r = await github(`/repos/${OWNER}/${REPO}/actions/runs/${record.run_id}`, env);
    if (r.ok) {
      const run = await r.json(); record.status = run.status; record.conclusion = run.conclusion; record.run_url = run.html_url; record.updated_at = new Date().toISOString();
    }
  } catch {}
  return record;
}
async function history(env) {
  const listed = await env.COMMANDS.list({ prefix: "cmd:", limit: 40 });
  const keys = listed.keys.map(k => k.name).reverse();
  const rows = [];
  for (const key of keys) {
    const record = await env.COMMANDS.get(key, "json"); if (!record) continue;
    const fresh = await refresh(record, env); rows.push(fresh);
    if (fresh !== record || fresh.updated_at !== record.updated_at) await env.COMMANDS.put(key, JSON.stringify(fresh), { expirationTtl: 60 * 60 * 24 * 30 });
  }
  return rows;
}
const PAGE = `<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blog Lab · Private Terminal</title><style>*{box-sizing:border-box}body{margin:0;background:#090b0f;color:#d7e0ea;font:15px ui-monospace,SFMono-Regular,Consolas,monospace}.wrap{max-width:1100px;margin:auto;padding:28px}.bar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:18px}.tag{color:#7ee787}.panel{border:1px solid #30363d;background:#0d1117;border-radius:14px;overflow:hidden}.head{padding:12px 16px;border-bottom:1px solid #30363d;color:#8b949e}.screen{height:430px;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:10px}.entry{border-left:2px solid #30363d;padding:8px 12px}.entry b{color:#7ee787}.entry .meta{color:#8b949e;font-size:12px;margin-top:5px}.entry.fail b{color:#ff7b72}.composer{border-top:1px solid #30363d;padding:14px}.row{display:flex;gap:10px;flex-wrap:wrap}.row select,.row textarea,.row button{background:#161b22;color:#d7e0ea;border:1px solid #30363d;border-radius:8px;padding:10px}.row textarea{width:100%;min-height:90px;resize:vertical;margin-top:10px}.row button{background:#238636;border-color:#2ea043;cursor:pointer;font-weight:700}.row button:disabled{opacity:.5}.hint{color:#8b949e;font-size:12px;margin-top:8px}a{color:#58a6ff}</style></head><body><div class="wrap"><div class="bar"><div><strong>Blog Lab / private-terminal</strong><div class="tag" id="who">● preverjam dostop …</div></div><a href="https://dday2301.github.io/blog-lab/" target="_blank">odpri blog ↗</a></div><div class="panel"><div class="head">authenticated operator channel · ukazi se pošiljajo šifrirano</div><div class="screen" id="screen"></div><div class="composer"><div class="row"><select id="mode"><option value="auto">Samodejno</option><option value="article">Članek</option><option value="site">Sprememba strani</option><option value="control">Nadzor agenta</option></select><select id="category"><option value="aktualno">Aktualno</option><option value="sport">Šport</option><option value="politika">Politika</option></select><button id="send">IZVEDI</button><textarea id="command" placeholder="Primer: Objavi članek o današnji temi … / Dodaj rubriko Projekti … / Ustavi objavljanje …"></textarea></div><div class="hint">Strukturne spremembe se preverijo z buildom in testi. Varnostne datoteke in terminal se ne morejo spreminjati skozi ta kanal.</div></div></div></div><script>const $=s=>document.querySelector(s);async function load(){const r=await fetch('/api/history',{cache:'no-store'});if(!r.ok){$('#who').textContent='● dostop zavrnjen';return}const d=await r.json();$('#who').textContent='● '+d.email;$('#screen').innerHTML=d.items.map(x=>{const fail=x.conclusion&&x.conclusion!=='success';return '<div class="entry '+(fail?'fail':'')+'"><b>&gt; '+esc(x.command)+'</b><div>'+esc(x.status||'queued')+(x.conclusion?' / '+esc(x.conclusion):'')+(x.run_url?' · <a target="_blank" href="'+x.run_url+'">GitHub run ↗</a>':'')+'</div><div class="meta">'+esc(x.mode)+' · '+esc(x.category)+' · '+esc(x.created_at)+'</div></div>'}).join('')||'<div class="entry">Terminal je pripravljen.</div>';$('#screen').scrollTop=$('#screen').scrollHeight}function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}$('#send').onclick=async()=>{const command=$('#command').value.trim();if(!command)return;$('#send').disabled=true;const r=await fetch('/api/command',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({command,mode:$('#mode').value,category:$('#category').value})});const d=await r.json();if(!r.ok)alert(d.error||'Napaka');else $('#command').value='';$('#send').disabled=false;await load()};load();setInterval(load,4000)</script></body></html>`;

export default {
  async fetch(request, env, ctx) {
    const user = await identity(ctx, env);
    if (!user) return new Response("Access required", { status: 403 });
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/") return new Response(PAGE, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'" } });
    if (request.method === "GET" && url.pathname === "/api/history") return json({ email: user.email, items: await history(env) });
    if (request.method === "POST" && url.pathname === "/api/command") {
      let body; try { body = await request.json(); } catch { return json({ error: "Neveljaven JSON." }, 400); }
      const command = String(body.command || "").trim(); const mode = ["auto","article","site","control"].includes(body.mode) ? body.mode : "auto"; const category = ["sport","politika","aktualno"].includes(body.category) ? body.category : "aktualno";
      if (!command || command.length > 4000) return json({ error: "Ukaz mora imeti 1–4000 znakov." }, 400);
      const requestId = crypto.randomUUID(); const created = new Date();
      const privatePayload = await encryptPayload(env, { request_id: requestId, command, mode, category, actor: user.email, created_at: created.toISOString() });
      const dispatch = await github(`/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, env, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ ref: "main", inputs: { request_id: requestId, payload: privatePayload } }) });
      if (!dispatch.ok) return json({ error: "GitHub workflow se ni zagnal.", status: dispatch.status }, 502);
      let run = {}; try { run = await dispatch.json(); } catch {}
      const record = { id: requestId, command, mode, category, actor: user.email, created_at: created.toISOString(), updated_at: created.toISOString(), status: "queued", conclusion: null, run_id: run.workflow_run_id || null, run_url: run.html_url || null };
      const key = `cmd:${String(created.getTime()).padStart(13,"0")}:${requestId}`; await env.COMMANDS.put(key, JSON.stringify(record), { expirationTtl: 60 * 60 * 24 * 30 });
      return json({ ok: true, id: requestId, run_url: record.run_url }, 202);
    }
    return new Response("Not found", { status: 404 });
  }
};
