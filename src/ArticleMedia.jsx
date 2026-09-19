const HTTPS_RE = /^https:\/\//i;
const LOCAL_RE = /^\/[A-Za-z0-9._~!$&'()*+,;=:@%\/-]+$/;

export function safeMediaUrl(value) {
  const url = String(value || "").trim();
  if (!url) return "";
  if (HTTPS_RE.test(url) || LOCAL_RE.test(url)) return url;
  return "";
}

function normalizeImage(value) {
  if (!value) return null;
  if (typeof value === "string") {
    const url = safeMediaUrl(value);
    return url ? { url, alt: "", caption: "" } : null;
  }
  const url = safeMediaUrl(value.url);
  if (!url) return null;
  return {
    url,
    alt: String(value.alt || "").trim(),
    caption: String(value.caption || "").trim()
  };
}

function normalizeVideo(value) {
  if (!value) return null;
  if (typeof value === "string") {
    const url = safeMediaUrl(value);
    return url ? { url, title: "" } : null;
  }
  const url = safeMediaUrl(value.url);
  if (!url) return null;
  return { url, title: String(value.title || "").trim() };
}

function normalizeSource(value) {
  if (!value || typeof value !== "object") return null;
  const url = safeMediaUrl(value.url);
  if (!url) return null;
  return {
    label: String(value.label || value.title || "Vir").trim() || "Vir",
    url
  };
}

export function normalizeArticleMedia(article = {}) {
  const gallery = Array.isArray(article.gallery)
    ? article.gallery.map(normalizeImage).filter(Boolean).slice(0, 12)
    : [];
  const sources = Array.isArray(article.sources)
    ? article.sources.map(normalizeSource).filter(Boolean).slice(0, 30)
    : [];
  return {
    ...article,
    heroImage: normalizeImage(article.heroImage),
    video: normalizeVideo(article.video),
    gallery,
    sources
  };
}

export function parseGalleryText(value) {
  return String(value || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [urlPart, alt = "", caption = ""] = line.split("|").map((part) => part.trim());
      const url = safeMediaUrl(urlPart);
      return url ? { url, alt, caption } : null;
    })
    .filter(Boolean)
    .slice(0, 12);
}

export function galleryToText(items) {
  return (Array.isArray(items) ? items : [])
    .map((item) => [item?.url, item?.alt, item?.caption].filter(Boolean).join(" | "))
    .filter(Boolean)
    .join("\n");
}

export function parseSourcesText(value) {
  return String(value || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const pieces = line.split("|").map((part) => part.trim());
      const url = safeMediaUrl(pieces.length > 1 ? pieces[pieces.length - 1] : pieces[0]);
      if (!url) return null;
      const label = pieces.length > 1 ? pieces.slice(0, -1).join(" | ") : "Vir";
      return { label: label || "Vir", url };
    })
    .filter(Boolean)
    .slice(0, 30);
}

export function sourcesToText(items) {
  return (Array.isArray(items) ? items : [])
    .map((item) => item?.url ? `${item.label || "Vir"} | ${item.url}` : "")
    .filter(Boolean)
    .join("\n");
}

function youtubeEmbed(url) {
  const safe = safeMediaUrl(url);
  if (!safe) return "";
  try {
    const parsed = new URL(safe, window.location.origin);
    if (parsed.hostname === "youtu.be") {
      const id = parsed.pathname.replace(/^\//, "").split("/")[0];
      return id ? `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}` : "";
    }
    if (/(^|\.)youtube\.com$/i.test(parsed.hostname)) {
      if (parsed.pathname === "/watch") {
        const id = parsed.searchParams.get("v");
        return id ? `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}` : "";
      }
      const match = parsed.pathname.match(/^\/(?:embed|shorts)\/([^/?]+)/);
      return match ? `https://www.youtube-nocookie.com/embed/${encodeURIComponent(match[1])}` : "";
    }
  } catch {}
  return "";
}

export function ArticleImage({ image, className = "" }) {
  const item = normalizeImage(image);
  if (!item) return null;
  return (
    <figure className={`article-image ${className}`.trim()}>
      <img src={item.url} alt={item.alt || ""} loading="lazy" decoding="async" />
      {item.caption && <figcaption>{item.caption}</figcaption>}
    </figure>
  );
}

export function ArticleHero({ article, compact = false }) {
  const image = normalizeImage(article?.heroImage);
  if (!image) {
    if (!compact) return null;
    return <div className="card-art card-art-fallback"><span>{String(article?.category || "B").slice(0, 1)}</span></div>;
  }
  if (compact) {
    return (
      <div className="card-art card-art-image">
        <img src={image.url} alt={image.alt || article?.title || ""} loading="lazy" decoding="async" />
      </div>
    );
  }
  return (
    <figure className="article-hero">
      <img src={image.url} alt={image.alt || article?.title || ""} fetchPriority="high" />
      {image.caption && <figcaption>{image.caption}</figcaption>}
    </figure>
  );
}

export function ArticleVideo({ video }) {
  const item = normalizeVideo(video);
  if (!item) return null;
  const embed = youtubeEmbed(item.url);
  if (embed) {
    return (
      <section className="article-video" aria-label={item.title || "Video"}>
        {item.title && <h2>{item.title}</h2>}
        <div className="video-frame">
          <iframe
            src={embed}
            title={item.title || "Video v članku"}
            loading="lazy"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        </div>
      </section>
    );
  }
  if (/\.(mp4|webm|ogg)(?:$|\?)/i.test(item.url)) {
    return (
      <section className="article-video">
        {item.title && <h2>{item.title}</h2>}
        <video controls preload="metadata" src={item.url}>Vaš brskalnik ne podpira videa.</video>
      </section>
    );
  }
  return (
    <p className="article-video-link">
      <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title || "Odpri video ↗"}</a>
    </p>
  );
}

export function ArticleGallery({ items }) {
  const gallery = (Array.isArray(items) ? items : []).map(normalizeImage).filter(Boolean);
  if (!gallery.length) return null;
  return (
    <section className="article-gallery">
      <div className="media-section-heading"><span>GALERIJA</span><h2>Vizualni utrinki</h2></div>
      <div className="gallery-grid">
        {gallery.map((image, index) => (
          <ArticleImage image={image} key={`${image.url}-${index}`} />
        ))}
      </div>
    </section>
  );
}

function sourceHost(value) {
  try {
    return new URL(value).hostname.replace(/^www\./i, "");
  } catch {
    return "zunanji vir";
  }
}

export function ArticleSources({ items }) {
  const sources = (Array.isArray(items) ? items : []).map(normalizeSource).filter(Boolean);
  if (!sources.length) return null;
  return (
    <section className="article-sources" aria-labelledby="article-sources-title">
      <div className="sources-surface">
        <div className="media-section-heading sources-heading">
          <span>VIRI</span>
          <h2 id="article-sources-title">Uporabljeni viri</h2>
          <p>Izvirne povezave, uporabljene pri pripravi članka.</p>
        </div>
        <div className="sources-grid">
          {sources.map((source, index) => (
            <a
              className="source-row"
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              key={`${source.url}-${index}`}
            >
              <span className="source-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="source-copy">
                <strong>{source.label}</strong>
                <small>{sourceHost(source.url)}</small>
              </span>
              <span className="source-arrow" aria-hidden="true">↗</span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

export function InlineArticleMedia({ line }) {
  const imageMatch = String(line || "").match(/^!\[([^\]]*)\]\((https:\/\/[^\s)]+|\/[^\s)]+)(?:\s+"([^"]*)")?\)$/);
  if (imageMatch) {
    return <ArticleImage image={{ url: imageMatch[2], alt: imageMatch[1], caption: imageMatch[3] || "" }} className="article-image-inline" />;
  }
  const videoMatch = String(line || "").match(/^\[\[video:(https:\/\/[^|\]]+|\/[^|\]]+)(?:\|([^\]]+))?\]\]$/);
  if (videoMatch) {
    return <ArticleVideo video={{ url: videoMatch[1], title: videoMatch[2] || "" }} />;
  }
  return null;
}

export function isInlineMediaLine(line) {
  return /^!\[[^\]]*\]\((?:https:\/\/|\/)/.test(String(line || "")) ||
    /^\[\[video:(?:https:\/\/|\/)/.test(String(line || ""));
}

export function MediaEditorFields({ draft, setDraft }) {
  const hero = normalizeImage(draft.heroImage) || { url: "", alt: "", caption: "" };
  const video = normalizeVideo(draft.video) || { url: "", title: "" };
  return (
    <div className="side-card media-editor-card">
      <h3>Mediji članka</h3>
      <label htmlFor="article-hero-url">Hero fotografija URL</label>
      <input
        id="article-hero-url"
        value={hero.url}
        onChange={(event) => setDraft({ ...draft, heroImage: { ...hero, url: event.target.value } })}
        placeholder="https://… ali /media/slika.jpg"
      />
      <label htmlFor="article-hero-alt">Opis fotografije</label>
      <input
        id="article-hero-alt"
        value={hero.alt}
        onChange={(event) => setDraft({ ...draft, heroImage: { ...hero, alt: event.target.value } })}
        placeholder="Kaj je na fotografiji?"
      />
      <label htmlFor="article-video-url">Video URL</label>
      <input
        id="article-video-url"
        value={video.url}
        onChange={(event) => setDraft({ ...draft, video: { ...video, url: event.target.value } })}
        placeholder="YouTube ali neposredni MP4 URL"
      />
      <label htmlFor="article-video-title">Naslov videa</label>
      <input
        id="article-video-title"
        value={video.title}
        onChange={(event) => setDraft({ ...draft, video: { ...video, title: event.target.value } })}
        placeholder="Kratek opis videa"
      />
      <label htmlFor="article-gallery">Galerija</label>
      <textarea
        id="article-gallery"
        className="media-list-input"
        value={galleryToText(draft.gallery)}
        onChange={(event) => setDraft({ ...draft, gallery: parseGalleryText(event.target.value) })}
        placeholder={"Ena slika na vrstico:\nURL | opis | napis"}
      />
      <label htmlFor="article-sources">Strukturirani viri</label>
      <textarea
        id="article-sources"
        className="media-list-input"
        value={sourcesToText(draft.sources)}
        onChange={(event) => setDraft({ ...draft, sources: parseSourcesText(event.target.value) })}
        placeholder={"Ime vira | https://…"}
      />
      <p className="media-editor-hint">Inline slika v besedilu: <code>![opis](https://… "napis")</code>. Video med odstavki: <code>[[video:https://…|Naslov]]</code>.</p>
    </div>
  );
}
