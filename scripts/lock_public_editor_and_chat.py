from pathlib import Path


def lock_public_app() -> None:
    app_path = Path("src/App.jsx")
    app = app_path.read_text(encoding="utf-8")

    if "const PUBLIC_WRITE_LOCK_NOTICE" not in app:
        app = app.replace(
            'const TERMINAL_URL = "https://blog-lab.dan-grmusa.workers.dev/";\n',
            'const TERMINAL_URL = "https://blog-lab.dan-grmusa.workers.dev/";\n'
            'const PUBLIC_WRITE_LOCK_NOTICE = "Javno pisanje in lokalno objavljanje sta zaklenjena. Objave se dodajajo samo prek zasebnega terminala, publisher agenta in odobrenega workflowa.";\n'
        )

    replacements = {
        'selectedArticle?.seoDescription || "Blog Lab – preprosta platforma za pisanje in objavljanje člankov."':
            'selectedArticle?.seoDescription || "Blog Lab – javni bralni blog. Objavljanje je zaklenjeno na zasebni uredniški terminal."',
        'Blog Lab – preprosta platforma za pisanje in objavljanje člankov.':
            'Blog Lab – javni bralni blog. Objavljanje je zaklenjeno na zasebni uredniški terminal.',
        'Ustvarite članek in ga objavite — prikazal se bo tukaj.':
            'Objave se dodajajo samo prek zasebnega uredniškega terminala, publisher agenta in odobrenega workflowa.',
        '<button className="secondary" onClick={newArticle}>Ustvari članek</button>':
            '<button className="secondary" onClick={openEditorialTerminal}>Odpri uredniški terminal ↗</button>',
        '<div><span className="kicker">UREDNIK</span><h1>Vsi članki</h1><p>Vsi prikazani članki so trajno shranjeni v GitHub repozitoriju in so enaki na vseh napravah.</p></div>':
            '<div><span className="kicker">ARHIV</span><h1>Vsi članki</h1><p>Javna stran je samo za branje. Objavljanje, urejanje in vzdrževanje potekajo izključno prek zasebnega terminala, publisher agenta in zaščitenih workflowov.</p></div>',
        '{view === "editor" && (':
            '{false && view === "editor" && ('
    }
    for before, after in replacements.items():
        app = app.replace(before, after)

    guards = {
        '  function validateDraft() {\n': '  function validateDraft() {\n    setToast(PUBLIC_WRITE_LOCK_NOTICE);\n    return false;\n',
        '  function saveArticle(status) {\n': '  function saveArticle(status) {\n    setToast(PUBLIC_WRITE_LOCK_NOTICE);\n    openEditorialTerminal();\n    return;\n',
        '  function removeArticle(id) {\n': '  function removeArticle(id) {\n    setToast(PUBLIC_WRITE_LOCK_NOTICE);\n    openEditorialTerminal();\n    return;\n',
        '  function exportArticles() {\n': '  function exportArticles() {\n    setToast("Izvoz javnih podatkov je zaklenjen. Upravljanje vsebine poteka samo prek zasebnega terminala.");\n    openEditorialTerminal();\n    return;\n',
        '  function importArticles(event) {\n': '  function importArticles(event) {\n    setToast(PUBLIC_WRITE_LOCK_NOTICE);\n    openEditorialTerminal();\n    return;\n',
    }
    for marker, guard in guards.items():
        if marker in app and guard not in app:
            app = app.replace(marker, guard)

    data_actions = '''            <div className="data-actions">
              <button className="icon-button" onClick={exportArticles} title="Izvozi JSON"><Icon name="export" /></button>
              <button className="text-button" onClick={() => importRef.current?.click()}>Uvozi</button>
              <input ref={importRef} type="file" accept="application/json" hidden onChange={importArticles} />
            </div>'''
    locked_actions = '''            <div className="data-actions locked-publish-note" title="Objavljanje je dovoljeno samo v zasebnem terminalu">
              <span className="lock-dot" />
              <span>Objavljanje zaklenjeno</span>
              <button className="text-button" onClick={openEditorialTerminal}>Terminal ↗</button>
            </div>'''
    app = app.replace(data_actions, locked_actions)

    app_path.write_text(app, encoding="utf-8")

    css_path = Path("src/styles.css")
    css = css_path.read_text(encoding="utf-8")
    if "/* locked public publishing guard */" not in css:
        css += '''

/* locked public publishing guard */
.locked-publish-note {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 999px;
  border: 1px solid rgba(21, 98, 68, .2);
  background: rgba(21, 98, 68, .08);
  color: var(--muted, #64756b);
  font-size: 13px;
  font-weight: 700;
}
.locked-publish-note .lock-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #159447;
  box-shadow: 0 0 0 4px rgba(21, 148, 71, .12);
}
.locked-publish-note .text-button {
  margin-left: 2px;
}
'''
        css_path.write_text(css, encoding="utf-8")


def clean_terminal_chat() -> None:
    worker_path = Path("terminal/worker/src/index.js")
    worker = worker_path.read_text(encoding="utf-8")

    login_start = worker.index("const LOGIN_PAGE =")
    page_start = worker.index("const PAGE =")
    login_segment = worker[login_start:page_start]
    block_marker = "\n<style>\n#terminalChatbotToggle"
    if block_marker in login_segment:
        before, after = login_segment.split(block_marker, 1)
        after.index("\n</body></html>`;")
        login_segment = before + "\n</body></html>`;\n\n"
        worker = worker[:login_start] + login_segment + worker[page_start:]

    if "function cleanTerminalChatAnswer" not in worker:
        clean_fn = r'''

function extractTerminalAnswerObject(value, depth = 0) {
  if (!value || depth > 5) return "";
  if (typeof value === "string") return value;
  if (typeof value !== "object") return "";
  const keys = ["answer", "text", "content", "message", "response", "output", "result", "data"];
  for (const key of keys) {
    const candidate = extractTerminalAnswerObject(value[key], depth + 1);
    if (candidate) return candidate;
  }
  const choice = value.choices?.[0]?.message?.content || value.choices?.[0]?.text;
  if (typeof choice === "string" && choice.trim()) return choice;
  return "";
}

function cleanTerminalChatAnswer(text, originalMessage = "") {
  let out = String(text || "").trim();
  for (let i = 0; i < 3; i += 1) {
    const compact = out.trim();
    if (!compact.startsWith("{") && !compact.startsWith("[")) break;
    try {
      const decoded = JSON.parse(compact);
      const nested = extractTerminalAnswerObject(decoded);
      if (!nested || nested === out) break;
      out = nested.trim();
    } catch {
      break;
    }
  }
  out = out
    .replace(/\\n/g, "\n")
    .replace(/\\"/g, '"')
    .replace(/^```(?:json|text|markdown)?\s*/i, "")
    .replace(/```$/i, "")
    .replace(/\r/g, "")
    .trim();
  const planningLeak = /(Draft \d|Refining the Response|Opening:|Since I'?m not connected|Better\):|Persona-aligned|contentReference)/i;
  if (planningLeak.test(out)) {
    return terminalChatFallback(originalMessage, new Error("planning_leak_cleaned"));
  }
  return out.slice(0, 2400).trim();
}
'''
        worker = worker.replace("\nfunction terminalChatTextFromResult(result) {", clean_fn + "\nfunction terminalChatTextFromResult(result, originalMessage = \"\") {")
        worker = worker.replace("if (typeof value === \"string\" && value.trim()) return value.trim();", "if (typeof value === \"string\" && value.trim()) return cleanTerminalChatAnswer(value, originalMessage);")
        worker = worker.replace("return jsonText && jsonText !== \"{}\" ? jsonText.slice(0, 2400) : \"\";", "return jsonText && jsonText !== \"{}\" ? cleanTerminalChatAnswer(jsonText, originalMessage) : \"\";")
        worker = worker.replace("const answer = terminalChatTextFromResult(result);", "const answer = terminalChatTextFromResult(result, message);")

    worker = worker.replace("AI pomočnik za kompleksne zadeve", "AI pomočnik")
    worker = worker.replace(
        "#terminalChatbotDock{position:fixed;right:22px;bottom:78px;width:min(420px,calc(100vw - 44px));max-height:70vh;",
        "#terminalChatbotDock{position:fixed;right:22px;bottom:78px;width:min(460px,calc(100vw - 44px));max-height:72vh;"
    )
    worker = worker.replace(
        "#terminalChatbotMessages{padding:14px 16px;overflow:auto;max-height:42vh;font-size:14px;line-height:1.45;white-space:pre-wrap}",
        "#terminalChatbotMessages{padding:14px 16px;overflow:auto;max-height:44vh;font-size:14px;line-height:1.55;white-space:pre-wrap;user-select:text}"
    )

    worker_path.write_text(worker, encoding="utf-8")


if __name__ == "__main__":
    lock_public_app()
    clean_terminal_chat()
    print("protected_public_publishing_lock_applied")
