"""Rights-preserving optimization of Wikimedia Commons hero photographs.

Only already-licensed Commons images are downloaded. This is image processing,
not image generation: no photograph or location is invented.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_DOWNLOAD_BYTES = 8_000_000
MAX_INPUT_PIXELS = 36_000_000
OUTPUT_WIDTH = 1600
OUTPUT_HEIGHT = 900


def optimize_commons_hero(article: dict, public_dir: Path) -> dict:
    """Create a local optimized 16:9 WebP hero, retaining credit and sourceUrl.

    On unsafe, non-Commons or unprocessable photos, leave the original intact.
    Media quality/licensing validation happens *before* this optional transform.
    """
    hero = article.get("heroImage")
    if not isinstance(hero, dict):
        return article
    url = str(hero.get("url") or "").strip()
    source_url = str(hero.get("sourceUrl") or "").strip()
    parsed = urlsplit(url)
    provenance = urlsplit(source_url)
    if parsed.scheme != "https" or parsed.hostname != "upload.wikimedia.org":
        return article
    if provenance.scheme != "https" or provenance.hostname != "commons.wikimedia.org":
        return article
    caption = str(hero.get("caption") or "")
    if "Wikimedia Commons" not in caption or not any(
        license_id in caption.lower() for license_id in ("cc by", "cc-by", "cc0", "public domain")
    ):
        return article

    try:
        request = Request(url, headers={
            "User-Agent": "BlogLabImageOptimizer/1.0 (+https://bloglab.eu/)",
            "Accept": "image/webp,image/jpeg,image/png",
        })
        with urlopen(request, timeout=18) as response:
            mime = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if mime not in {"image/jpeg", "image/png", "image/webp"}:
                return article
            raw = response.read(MAX_DOWNLOAD_BYTES + 1)
        if len(raw) > MAX_DOWNLOAD_BYTES:
            return article
        with Image.open(io.BytesIO(raw)) as original:
            if original.width * original.height > MAX_INPUT_PIXELS:
                return article
            if original.width < 960 or original.height < 540:
                return article
            src = ImageOps.exif_transpose(original).convert("RGB")
            frame = ImageOps.fit(src, (OUTPUT_WIDTH, OUTPUT_HEIGHT), Image.Resampling.LANCZOS)
            frame.thumbnail((OUTPUT_WIDTH, OUTPUT_HEIGHT))
            out = io.BytesIO()
            frame.save(out, format="WEBP", quality=83, method=5)
            optimized = out.getvalue()
        if not optimized or len(optimized) > len(raw) * 1.5:
            return article
        digest = hashlib.sha256(raw).hexdigest()[:20]
        dest = public_dir / "media" / "articles" / f"{digest}.webp"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_bytes(optimized)
        result = dict(article)
        result["heroImage"] = {**hero, "url": "/media/articles/" + dest.name}
        return result
    except (OSError, ValueError, UnidentifiedImageError) as exc:
        print(f"IMAGE_OPTIMIZATION_SKIPPED {type(exc).__name__}: {exc}")
        return article
