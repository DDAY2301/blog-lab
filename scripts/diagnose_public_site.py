"""Read-only checks for BlogLab's public host, Pages fallback, and static assets.

Run from an internet-connected runner. Does not read secrets or mutate deployments.
"""
from __future__ import annotations

import re
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
