from pathlib import Path

path = Path("terminal/worker/src/index.js")
text = path.read_text(encoding="utf-8")

old_ui = "if(!r.ok){alert(d.error+(d.missing?'\\\\nManjka: '+d.missing.join(', '):''));return}"
new_ui = "if(!r.ok){const parts=[d.error||'Ukaz ni uspel.'];if(d.status)parts.push('HTTP status: '+d.status);if(d.code)parts.push('Koda: '+d.code);if(d.hint)parts.push('Namig: '+d.hint);if(d.detail)parts.push('GitHub odgovor: '+String(d.detail).slice(0,900));if(d.missing&&d.missing.length)parts.push('Manjka: '+d.missing.join(', '));alert(parts.join('\\\\n'));return}"

if old_ui in text:
    text = text.replace(old_ui, new_ui, 1)
elif "GitHub odgovor:" not in text:
    raise SystemExit("Worker UI dispatch alert marker not found")

old_dispatch = 'return json({ error: "GitHub workflow se ni zagnal.", status: dispatch.status, detail: text.slice(0, 300) }, 502);'
new_dispatch = 'const detail = text.slice(0, 900);\n        const hint = dispatch.status === 401 || dispatch.status === 403\n          ? "GITHUB_DISPATCH_TOKEN nima dovoljenja za Actions workflow dispatch ali repo write."\n          : dispatch.status === 404\n          ? "Workflow operator-terminal.yml ali repozitorij ni dostopen s tem tokenom."\n          : dispatch.status === 422\n          ? "GitHub je zavrnil workflow_dispatch payload/ref; preveri main branch in workflow inputs."\n          : "GitHub dispatch endpoint je vrnil napako.";\n        return json({ error: "GitHub workflow se ni zagnal.", code: "GITHUB_WORKFLOW_DISPATCH_FAILED", status: dispatch.status, detail, hint }, 502);'

if old_dispatch in text:
    text = text.replace(old_dispatch, new_dispatch, 1)
elif "GITHUB_WORKFLOW_DISPATCH_FAILED" not in text:
    raise SystemExit("Worker dispatch JSON marker not found")

path.write_text(text, encoding="utf-8")
print("Worker dispatch diagnostics patched")
