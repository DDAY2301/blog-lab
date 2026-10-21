"""Read-only checks for BlogLab's public host, Pages fallback, and static assets.

Run from an internet-connected runner. Does not read secrets or mutate deployments.
"""
from __future__ import annotations

import re
import os
import shutil
import subprocess
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request


URLS = (
    "https://bloglab.eu/",
    "https://www.bloglab.eu/",
    "https://dday2301.github.io/blog-lab/",
)


def get(url: str) -> tuple[int, str, bytes, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "BlogLab-Public-Availability/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=14, context=ssl.create_default_context()) as res:
            return res.status, res.geturl(), res.read(400_000), res.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl(), exc.read(2000), exc.headers.get("Content-Type", "")


def main() -> int:
    for url in URLS:
        parsed = urllib.parse.urlparse(url)
        print(f"PUBLIC_SITE_CHECK url={url}", flush=True)
        try:
            addresses = sorted({
                entry[4][0] for entry in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
            })
            print(f"  dns={','.join(addresses[:8])}", flush=True)
        except Exception as exc:
            print(f"  DNS_ERROR {type(exc).__name__}: {exc}", flush=True)
            continue
        try:
            status, final, body, content_type = get(url)
            print(f"  http={status} final={final} type={content_type} length={len(body)}", flush=True)
        except Exception as exc:
            print(f"  HTTP_ERROR {type(exc).__name__}: {exc}", flush=True)
            continue
        html = body.decode("utf-8", errors="replace")
        print(f"  has_root={bool(re.search(r'<div[^>]+id=[\"\x27]root[\"\x27]', html))}", flush=True)
        print(f"  has_vite_dev_ref={'/src/main.jsx' in html}", flush=True)
        assets = re.findall(r'(?:src|href)=[\"\x27]([^\"\x27]+\.(?:js|css)(?:\?[^\"\x27]*)?)[\"\x27]', html)
        print(f"  assets={len(assets)}", flush=True)
        for asset in assets[:4]:
            resolved = urllib.parse.urljoin(final, asset)
            try:
                code, asset_final, payload, kind = get(resolved)
                print(f"  asset={code} url={asset_final} content_type={kind} length={len(payload)}", flush=True)
            except Exception as exc:
                print(f"  ASSET_ERROR url={resolved} error={type(exc).__name__}: {exc}", flush=True)
        if not assets:
            print(f"  sample={html[:160]!r}", flush=True)
    # HTTP status 200 and valid JS assets do not prove the React app renders.
    chrome = next(
        (path for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
         if (path := shutil.which(name))),
        None,
    )
    if chrome:
        print("PUBLIC_REACT_RENDER_CHECK url=https://bloglab.eu/", flush=True)
        try:
            result = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                 "--virtual-time-budget=7000", "--dump-dom", "https://bloglab.eu/"],
                capture_output=True, text=True, timeout=34,
            )
            dom = result.stdout
            print(f"  browser_exit={result.returncode} dom_bytes={len(dom)}", flush=True)
            print(f"  react_rubrics={sum(marker in dom for marker in ('Kolesarstvo','Dediščina','Sezonsko','Gourmet'))}", flush=True)
            print(f"  reacted_root={'id=\"root\"' in dom and len(dom) > 1600}", flush=True)
            if len(dom) <= 1600:
                print(f"  dom_sample={dom[:450]!r}", flush=True)
            errors = [
                line.strip()[:320] for line in result.stderr.splitlines()
                if "CONSOLE" in line or "Uncaught" in line or "SyntaxError" in line
            ]
            print(f"  browser_js_errors={len(errors)}", flush=True)
            for error in errors[:8]:
                print(f"    {error}", flush=True)
        except Exception as exc:
            print(f"  BROWSER_ERROR {type(exc).__name__}: {exc}", flush=True)
        for size, label in (("1440,1000", "desktop"), ("390,844", "mobile")):
            try:
                shot = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), f"atelier-live-{label}.png")
                process = subprocess.run(
                    [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                     "--hide-scrollbars", f"--window-size={size}",
                     "--virtual-time-budget=7000", f"--screenshot={shot}",
                     "https://bloglab.eu/"],
                    capture_output=True, text=True, timeout=34,
                )
                print(f"  screenshot={label} exit={process.returncode} exists={os.path.exists(shot)}", flush=True)
            except Exception as exc:
                print(f"  SCREENSHOT_ERROR label={label} error={type(exc).__name__}: {exc}", flush=True)
    else:
        print("PUBLIC_REACT_RENDER_CHECK browser_missing", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
