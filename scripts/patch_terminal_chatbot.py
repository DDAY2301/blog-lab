from pathlib import Path

path = Path("terminal/worker/src/index.js")
text = path.read_text(encoding="utf-8")
original = text

helper = r'''
function terminalChatFallback(message, error = null) {
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
  return parts.join("\n\n");
}

function terminalChatTextFromResult(result) {
  const candidates = [
    result?.response?.response,
    result?.response?.answer,
    result?.response?.text,
    result?.response,
    result?.choices?.[0]?.message?.content,
    result?.choices?.[0]?.text,
    result?.answer,
    result?.text,
  ];
  for (const value of candidates) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  try {
    const jsonText = JSON.stringify(result?.response || result || {}, null, 2);
    return jsonText && jsonText !== "{}" ? jsonText.slice(0, 2400) : "";
  } catch {
    return "";
  }
}

async function terminalChatAssistant(env, message, email) {
  const system = [
    "Si zasebni Blog Lab terminal pomočnik.",
    "Odgovarjaj v slovenščini, praktično in operativno.",
    "Pomagaj pri: objavah, workflow napakah, Cloudflare Workerju, DNS za bloglab.eu, Neoserv usmeritvi, GitHub Pages, maintenance in samopopravljanju agenta.",
    "Ne zahtevaj gesel, tokenov ali secretov v klepetu.",
    "Če je problem izvedbeni, predlagaj točen terminal ukaz ali naslednji varen korak."
  ].join("\n");
  const request = {
    messages: [
      { role: "system", content: system },
      { role: "user", content: "Uporabnik: " + email + "\nVprašanje: " + String(message || "").slice(0, 4000) }
    ],
    max_tokens: 900,
    temperature: 0.2
  };
  try {
    const result = await runWorkersAiWithRetry(env, request, 2, {
      purpose: "terminal_chat",
      cacheKey: "terminal-chat-" + b64urlText(String(message || "").slice(0, 400)).slice(0, 80)
    });
    const answer = terminalChatTextFromResult(result);
    if (answer) return { mode: "workers_ai", text: answer, model: result?.model || result?.last_model || null };
    return { mode: "fallback", text: terminalChatFallback(message, new Error("empty_ai_response")) };
  } catch (error) {
    return { mode: "fallback", text: terminalChatFallback(message, error), error: sanitizeAiError(error) };
  }
}
'''

if "function terminalChatAssistant" not in text:
    marker = "async function runWorkersAiWithRetry"
    if marker not in text:
        raise SystemExit("Cannot find runWorkersAiWithRetry marker")
    text = text.replace(marker, helper + "\n" + marker, 1)

route = r'''
    if (request.method === "POST" && url.pathname === "/api/chat") {
      const user = await identity(request, env);
      if (!user) return json({ ok: false, error: "UNAUTHORIZED" }, 401);
      const body = await request.json().catch(() => ({}));
      const message = String(body.message || "").trim();
      if (!message) return json({ ok: false, error: "EMPTY_MESSAGE" }, 400);
      if (message.length > 4000) return json({ ok: false, error: "MESSAGE_TOO_LONG" }, 413);
      const answer = await terminalChatAssistant(env, message, user.email);
      return json({ ok: true, user: user.email, ...answer });
    }
'''

if 'url.pathname === "/api/chat"' not in text:
    marker = '    if (request.method === "POST" && url.pathname === "/api/media") {'
    if marker not in text:
        raise SystemExit("Cannot find /api/media router insertion marker")
    text = text.replace(marker, route + "\n" + marker, 1)

overlay = r'''
<style>
#terminalChatbotToggle{position:fixed;right:22px;bottom:22px;z-index:80;border:1px solid #2b6b44;background:#1aa54a;color:#fff;padding:12px 16px;border-radius:999px;font-weight:800;box-shadow:0 12px 32px rgba(0,0,0,.35);cursor:pointer}
#terminalChatbotDock{position:fixed;right:22px;bottom:78px;width:min(420px,calc(100vw - 44px));max-height:70vh;z-index:81;background:#0b1118;border:1px solid #2c3b4a;border-radius:18px;box-shadow:0 22px 60px rgba(0,0,0,.52);display:none;overflow:hidden;color:#dbeafe}
#terminalChatbotDock.open{display:flex;flex-direction:column}
#terminalChatbotHead{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-bottom:1px solid #253244;background:#0f1722}
#terminalChatbotHead strong{color:#86efac}
#terminalChatbotClose{background:#111827;color:#cbd5e1;border:1px solid #334155;border-radius:10px;padding:6px 9px;cursor:pointer}
#terminalChatbotMessages{padding:14px 16px;overflow:auto;max-height:42vh;font-size:14px;line-height:1.45;white-space:pre-wrap}
.terminal-chat-msg{margin:0 0 12px;padding:10px 12px;border-radius:12px;border:1px solid #253244;background:#0f1722}
.terminal-chat-msg.user{background:#102033;border-color:#1f4972;color:#bfdbfe}
.terminal-chat-msg.bot{background:#0f1d14;border-color:#245a35;color:#d1fae5}
#terminalChatbotInput{margin:0 14px 12px;width:calc(100% - 28px);min-height:90px;resize:vertical;background:#060b12;border:1px solid #334155;border-radius:12px;color:#e5e7eb;padding:10px;font:inherit}
#terminalChatbotSend{margin:0 14px 14px;background:#22c55e;color:#06210f;border:0;border-radius:12px;padding:11px 14px;font-weight:900;cursor:pointer}
#terminalChatbotSend:disabled{opacity:.55;cursor:wait}
</style>
<button id="terminalChatbotToggle" type="button">AI pomočnik</button>
<section id="terminalChatbotDock" aria-label="AI pomočnik terminala">
  <div id="terminalChatbotHead"><strong>AI pomočnik za kompleksne zadeve</strong><button id="terminalChatbotClose" type="button">zapri</button></div>
  <div id="terminalChatbotMessages"><div class="terminal-chat-msg bot">Vprašaj me za DNS bloglab.eu, objave, napake v workflowih, Cloudflare Worker, 24/7 delovanje ali kako poslati pravilen ukaz agentu.</div></div>
  <textarea id="terminalChatbotInput" placeholder="Npr. Povej mi točne DNS nastavitve za bloglab.eu in preveri kaj manjka za 24/7 delovanje..."></textarea>
  <button id="terminalChatbotSend" type="button">Vprašaj pomočnika</button>
</section>
<script>
(function(){
  var toggle=document.getElementById('terminalChatbotToggle');
  var dock=document.getElementById('terminalChatbotDock');
  var close=document.getElementById('terminalChatbotClose');
  var input=document.getElementById('terminalChatbotInput');
  var send=document.getElementById('terminalChatbotSend');
  var messages=document.getElementById('terminalChatbotMessages');
  if(!toggle||!dock||!input||!send||!messages)return;
  function add(kind,text){var node=document.createElement('div');node.className='terminal-chat-msg '+kind;node.textContent=text;messages.appendChild(node);messages.scrollTop=messages.scrollHeight;}
  toggle.addEventListener('click',function(){dock.classList.toggle('open'); if(dock.classList.contains('open')) input.focus();});
  close.addEventListener('click',function(){dock.classList.remove('open');});
  async function ask(){
    var text=input.value.trim();
    if(!text)return;
    input.value=''; add('user',text); send.disabled=true; send.textContent='Razmišljam ...';
    try{
      var res=await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:text})});
      var data=await res.json().catch(function(){return {};});
      if(!res.ok||!data.ok) throw new Error(data.error||('HTTP '+res.status));
      add('bot',(data.mode==='fallback'?'[fallback] ':'')+(data.text||'Ni odgovora.'));
    }catch(err){add('bot','Napaka pomočnika: '+(err&&err.message?err.message:String(err)));}
    finally{send.disabled=false; send.textContent='Vprašaj pomočnika';}
  }
  send.addEventListener('click',ask);
  input.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&e.key==='Enter')ask();});
})();
</script>
'''

page_start = text.find('const PAGE = `')
page_end = text.find('\n\nexport default', page_start)
page_segment = text[page_start:page_end if page_end != -1 else len(text)]
if "terminalChatbotDock" not in page_segment:
    marker = "pollLoop();\n</script></body></html>`;"
    if marker not in text:
        raise SystemExit("Cannot find terminal PAGE closing marker")
    replacement = "pollLoop();\n</script>" + overlay + "\n</body></html>`;"
    text = text.replace(marker, replacement, 1)

if text == original:
    print("No terminal chatbot changes needed")
else:
    path.write_text(text, encoding="utf-8")
    print("Patched terminal chatbot endpoint and terminal UI")
