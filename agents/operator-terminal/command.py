from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CONTROL = BASE / "data/agent-control.json"
RUBRICS = BASE / "public/site-rubrics.json"
ARTICLE_AGENT = BASE / "agents/blog-lab-publisher/agent.py"
VALID_MODES = {"auto", "article", "site", "control"}
VALID_CATEGORIES = {"sport", "politika", "aktualno"}

def read_json(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError: return default

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

def _schedule_intent(low: str) -> bool:
    schedule_terms = [
        "urnik",
        "trikrat na dan", "tri krat na dan", "3x na dan", "3 x na dan", "3 krat na dan",
        "samostojna objava", "samodejna objava", "avtomatska objava",
        "samostojno objavljanje", "samodejno objavljanje", "avtomatsko objavljanje",
    ]
    if any(term in low for term in schedule_terms):
        return True
    # Slovene inflections: termin, termini, termine, terminov + objava/objave/objav.
    return "termin" in low and "objav" in low

def _site_intent(low: str) -> bool:
    site_terms = [
        "stran", "spletno stran", "rubrik", "meni", "header", "footer", "navigacij",
        "layout", "dizajn", "design", "izgled", "sekcij", "stolpec", "sidebar",
        "galerij", "gumb", "logo", "favicon", "hero", "kartic", "css", "responsive",
    ]
    return any(term in low for term in site_terms)

def _article_intent(low: str) -> bool:
    article_nouns = ["članek", "clanek", "prispevek", "novico", "novica"]
    article_actions = ["objavi", "napiši", "napisi", "pripravi", "ustvari", "sestavi"]
    if any(noun in low for noun in article_nouns) and any(action in low for action in article_actions):
        return True
    return "napiši o" in low or "napisi o" in low

def infer_mode(command: str) -> str:
    low = command.lower()
    if (
        any(x in low for x in ["ustavi", "pavza", "zaustavi", "nadaljuj", "vklopi", "izklopi", "resume", "pause"])
        or _schedule_intent(low)
    ):
        return "control"
    if _article_intent(low):
        return "article"
    if _site_intent(low):
        return "site"
    if "objavi" in low:
        return "article"
    return "site"

DEFAULT_SCHEDULE_TIMES = ("08:17", "13:27", "19:43")

def _explicit_schedule_times(text: str) -> list[str]:
    found = []
    for hour, minute in re.findall(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b", text):
        value = f"{int(hour):02d}:{int(minute):02d}"
        if value not in found:
            found.append(value)
    for hour in re.findall(r"\bob\s+([01]?\d|2[0-3])\s*(?:h|ih|uri|ure)\b", text, flags=re.I):
        value = f"{int(hour):02d}:00"
        if value not in found:
            found.append(value)
    return found

def control_command(command: str) -> None:
    ctl = read_json(CONTROL, {"enabled": True, "publish_mode": "automatic"})
    low = command.lower()
    schedule_requested = _schedule_intent(low)
    explicit_times = _explicit_schedule_times(low)
    if schedule_requested and explicit_times and tuple(explicit_times) != DEFAULT_SCHEDULE_TIMES:
        print(
            "CONTROL_UNSUPPORTED custom schedule requested: "
            + ", ".join(explicit_times)
            + ". Podprt je preverjeni urnik 08:17 / 13:27 / 19:43 Europe/Ljubljana.",
            file=sys.stderr,
        )
        raise SystemExit(64)

    if any(x in low for x in ["ustavi", "zaustavi", "izklopi", "pause", "pavza"]):
        ctl["enabled"] = False
    elif any(x in low for x in ["nadaljuj", "vklopi", "resume", "začni", "zacni"]) or schedule_requested:
        ctl["enabled"] = True

    if "draft" in low or "osnut" in low:
        ctl["publish_mode"] = "draft"
    elif "review" in low or "pregled" in low:
        ctl["publish_mode"] = "review"
    elif (
        "automatic" in low or "avtomats" in low or "samodejn" in low
        or "samostojn" in low or schedule_requested
    ):
        ctl["publish_mode"] = "automatic"

    if schedule_requested:
        ctl["schedule_profile"] = "default-3x-daily"
        ctl["schedule"] = {
            "timezone": "Europe/Ljubljana",
            "slots": [
                {"time": "08:17", "category": "sport"},
                {"time": "13:27", "category": "politika"},
                {"time": "19:43", "category": "aktualno"},
            ],
        }

    write_json(CONTROL, ctl)
    print(
        "CONTROL_OK "
        f"enabled={str(ctl.get('enabled', True)).lower()} "
        f"publish_mode={ctl.get('publish_mode', 'automatic')} "
        f"schedule_profile={ctl.get('schedule_profile', 'unchanged')}"
    )

def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def article_command(command: str, category: str) -> None:
    app = BASE / "src/App.jsx"
    before = _sha256(app)
    cmd = [sys.executable, str(ARTICLE_AGENT), "--category", category, "--topic", command, "--force"]
    result = subprocess.run(cmd, cwd=BASE, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    after = _sha256(app)
    if not after or after == before:
        raise SystemExit("Manual article request completed without publishing a new article")

def _safe_agent_log(value: str, limit: int = 3500) -> str:
    text = str(value or "")
    text = re.sub(r"(github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+|Bearer\\s+[A-Za-z0-9._-]+)", "[REDACTED]", text, flags=re.I)
    return text[-limit:].strip()

DESIGN_MARKER = "/* Blog Lab built-in design upgrade v1 */"

def _design_intent(low: str) -> bool:
    design_terms = [
        "polepš", "poleps", "izboljšaj izgled", "izboljsaj izgled",
        "lepši izgled", "lepsi izgled", "modernizir", "modern design",
        "izgled strani", "design strani", "dizajn strani",
        "uredi izgled", "izboljšaj stran", "izboljsaj stran",
    ]
    return any(term in low for term in design_terms)

def apply_design_upgrade() -> bool:
    path = BASE / "src/styles.css"
    if not path.exists():
        return False
    css = path.read_text(encoding="utf-8")
    if DESIGN_MARKER in css:
        print("BUILTIN_SITE_OK design-upgrade already installed")
        return True
    upgrade = r"""

/* Blog Lab built-in design upgrade v1 */
:root {
  --surface-soft: rgba(255,255,255,.74);
  --surface-strong: rgba(255,255,255,.94);
  --ring: rgba(23,107,69,.14);
}
body {
  background:
    radial-gradient(circle at 10% 5%, rgba(23,107,69,.055), transparent 30rem),
    linear-gradient(180deg, #f7f7f2 0%, #fbfbf8 45%, #f5f6f1 100%);
}
.site-header {
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  background: rgba(250,251,247,.86);
  border-bottom: 1px solid rgba(204,211,204,.72);
  box-shadow: 0 8px 30px rgba(19,31,23,.045);
}
.brand { letter-spacing: -.025em; }
.hero {
  position: relative;
  overflow: hidden;
  isolation: isolate;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 8% auto auto 58%;
  width: 34rem;
  height: 34rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(35,134,85,.14), rgba(35,134,85,0) 68%);
  z-index: -1;
  pointer-events: none;
}
.hero h1 {
  letter-spacing: -.045em;
  text-wrap: balance;
}
.hero p { max-width: 720px; }
.section-heading {
  align-items: end;
  border-bottom: 1px solid var(--line);
  padding-bottom: 18px;
}
.section-heading h2 { letter-spacing: -.035em; }
.post-card {
  background: var(--surface-strong);
  border: 1px solid rgba(205,212,206,.82);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 16px 42px rgba(17,31,21,.055);
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}
.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 24px 58px rgba(17,31,21,.10);
  border-color: rgba(23,107,69,.28);
}
.card-copy h3 { letter-spacing: -.025em; }
.card-copy p { line-height: 1.7; }
.card-art {
  background:
    linear-gradient(135deg, rgba(23,107,69,.11), rgba(23,107,69,.025)),
    #eef2ec;
}
.live-pulse {
  background: var(--surface-soft);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-color: rgba(205,212,206,.82);
  box-shadow: 0 18px 48px rgba(18,34,23,.075);
}
.live-pulse-item {
  border-radius: 10px;
  transition: background .16s ease, transform .16s ease;
}
.live-pulse-item:hover {
  background: rgba(23,107,69,.055);
  transform: translateX(2px);
}
button, .button, .primary-button, .secondary-button {
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}
button:hover, .button:hover, .primary-button:hover, .secondary-button:hover {
  transform: translateY(-1px);
}
.article-page, .editor-main, .preview-modal {
  background: rgba(255,255,255,.94);
}
.article-heading h1 {
  letter-spacing: -.045em;
  text-wrap: balance;
}
.article-body {
  font-size: 17px;
  line-height: 1.78;
}
.article-body p { max-width: 72ch; }
.article-hero, .article-image, .video-frame {
  box-shadow: 0 20px 48px rgba(15,30,20,.08);
}
footer {
  background: rgba(248,249,245,.76);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
@media (prefers-reduced-motion: reduce) {
  .post-card, .live-pulse-item, button, .button, .primary-button, .secondary-button {
    transition: none !important;
  }
}
"""
    path.write_text(css.rstrip() + upgrade + "\n", encoding="utf-8")
    print("BUILTIN_SITE_OK design-upgrade applied")
    return True

def _rubric_slug(value: str) -> str:
    value = value.lower().strip()
    repl = {"č":"c","š":"s","ž":"z","ć":"c","đ":"d"}
    value = "".join(repl.get(ch, ch) for ch in value)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:48]

def _rubric_request(command: str):
    text = " ".join(str(command or "").strip().split())
    add = re.match(
        r"^(?:dodaj|ustvari)\s+(?:novo\s+|novo\s+spletno\s+)?(?:rubriko|stran)\s+(.+?)"
        r"(?:\s+(?:v|na)\s+(?:meni|navigacijo|header|glavni\s+meni))?[.!?]?$",
        text,
        flags=re.I,
    )
    if add:
        return "add", add.group(1).strip(" .,:;!?")
    remove = re.match(
        r"^(?:odstrani|izbriši|izbrisi|umakni)\s+(?:rubriko|stran)\s+(.+?)[.!?]?$",
        text,
        flags=re.I,
    )
    if remove:
        return "remove", remove.group(1).strip(" .,:;!?")
    return None

def manage_rubric(command: str) -> bool:
    request = _rubric_request(command)
    if not request:
        return False
    action, name = request
    name = re.sub(r"\s+(?:v|na)\s+(?:meni|navigacijo|header|glavni\s+meni)$", "", name, flags=re.I).strip()
    if not name or len(name) > 40:
        raise SystemExit("Ime rubrike mora imeti 1–40 znakov.")
    if not re.search(r"[A-Za-zČŠŽčšžĆćĐđ0-9]", name):
        raise SystemExit("Ime rubrike ni veljavno.")

    rubrics = read_json(RUBRICS, [])
    if not isinstance(rubrics, list):
        rubrics = []
    slug = _rubric_slug(name)
    existing = [r for r in rubrics if isinstance(r, dict) and str(r.get("slug", "")).lower() == slug]

    if action == "add":
        if not existing:
            rubrics.append({"name": name, "slug": slug})
            write_json(RUBRICS, rubrics[:12])
            print(f"BUILTIN_SITE_OK rubric-added name={name}")
        else:
            print(f"BUILTIN_SITE_OK rubric-exists name={existing[0].get('name', name)}")
        return True

    filtered = [r for r in rubrics if not (isinstance(r, dict) and str(r.get("slug", "")).lower() == slug)]
    if len(filtered) != len(rubrics):
        write_json(RUBRICS, filtered)
        print(f"BUILTIN_SITE_OK rubric-removed name={name}")
    else:
        print(f"BUILTIN_SITE_OK rubric-not-found name={name}")
    return True

def builtin_site_command(command: str) -> bool:
    low = command.lower()
    if manage_rubric(command):
        return True
    if _design_intent(low):
        return apply_design_upgrade()
    live_intent = (
        ("pol ure" in low or "30 min" in low or "30 minut" in low)
        and ("mini" in low or "tekoč" in low or "aktual" in low)
        and ("stolpec" in low or "stran" in low or "lev" in low)
    )
    if live_intent:
        required = [
            BASE / "src/LivePulse.jsx",
            BASE / "agents/live-feed/update.py",
            BASE / ".github/workflows/live-feed.yml",
            BASE / "public/live-feed.json",
        ]
        if all(path.exists() for path in required):
            print("BUILTIN_SITE_OK live-pulse already installed")
            return True
    return False

def site_command(command: str) -> None:
    if builtin_site_command(command):
        return
    if not shutil.which("copilot"):
        raise SystemExit("Copilot CLI is not installed")
    prompt = """You are the authenticated repository editor for DDAY2301/blog-lab. Execute the operator request below by editing the existing repository, preserving working functionality and design. Do not merely explain. You may edit normal website files under src/, public/, and the Blog Lab publisher prompts/config when relevant. The site has a structured multimedia article system in src/ArticleMedia.jsx: hero images, inline images, YouTube/direct video, galleries and structured sources. When the operator supplies media URLs, integrate them into that system instead of inventing replacements. NEVER edit .github/, terminal/, agents/operator-terminal/, AGENTS.md, requirements-agent.txt, secrets, authentication, permissions, or security controls. Do not use shell commands or network tools. Do not reveal tokens or environment variables. Keep changes minimal and production-ready.\n\nOPERATOR REQUEST:\n""" + command
    excluded = "bash,powershell,web_fetch,task,write_agent,ask_user"
    proc = subprocess.run(
        ["copilot", "-s", "-p", prompt, "--no-ask-user", "--no-custom-instructions", "--disable-builtin-mcps", f"--excluded-tools={excluded}", "--no-auto-update", "--no-remote", "--no-remote-export"],
        cwd=BASE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=240,
        check=False,
    )
    if proc.returncode != 0:
        diagnostic = _safe_agent_log((proc.stderr or "") + "\n" + (proc.stdout or ""))
        if diagnostic:
            print("COPILOT_DIAGNOSTIC_BEGIN", file=sys.stderr)
            print(diagnostic, file=sys.stderr)
            print("COPILOT_DIAGNOSTIC_END", file=sys.stderr)
        if "access denied by policy settings" in diagnostic.lower():
            print("COPILOT_POLICY_DENIED", file=sys.stderr)
            raise SystemExit(78)
        auth_hint = ""
        if os.environ.get("COPILOT_PERSONAL_TOKEN_CONFIGURED", "").lower() != "true":
            auth_hint = " Personal repositories may require repository secret COPILOT_GITHUB_TOKEN with Copilot Requests permission."
        raise SystemExit(f"Copilot edit failed with exit code {proc.returncode}.{auth_hint}")

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--command-file", required=True); args = ap.parse_args()
    payload = json.loads(Path(args.command_file).read_text(encoding="utf-8"))
    command = str(payload.get("command", "")).strip()
    mode = str(payload.get("mode", "auto")).lower()
    category = str(payload.get("category", "aktualno")).lower()
    if not command or len(command) > 4000: raise SystemExit("invalid command")
    if mode not in VALID_MODES: mode = "auto"
    if category not in VALID_CATEGORIES: category = "aktualno"
    if mode == "auto": mode = infer_mode(command)
    if mode == "control": control_command(command)
    elif mode == "article": article_command(command, category)
    elif mode == "site": site_command(command)
    return 0
if __name__ == "__main__": raise SystemExit(main())
