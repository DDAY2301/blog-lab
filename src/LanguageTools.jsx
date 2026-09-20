import { useEffect, useMemo, useState } from "react";

const LANGUAGES = [
  {
    code: "sl",
    short: "SL",
    name: "Slovenščina",
    nativeName: "Slovenščina",
    title: "Jezik strani",
    intro: "Izberi jezik. Slovenska različica je izvirna, druge jezike lahko odpreš kot prevod trenutne strani.",
    translate: "Prevedi trenutno stran",
    original: "Izvirnik",
    note: "Članki ostanejo povezani z istimi viri in povezavami.",
    aria: "Izberi jezik strani"
  },
  {
    code: "en",
    short: "EN",
    name: "English",
    nativeName: "English",
    title: "Site language",
    intro: "Choose a language. Slovenian is the original version; this opens the current page in translation.",
    translate: "Translate this page",
    original: "Original",
    note: "Articles keep the same sources and links.",
    aria: "Choose site language"
  },
  {
    code: "hr",
    short: "HR",
    name: "Croatian",
    nativeName: "Hrvatski",
    title: "Jezik stranice",
    intro: "Odaberi jezik. Slovenska verzija je izvorna, a ovu stranicu možeš otvoriti kao prijevod.",
    translate: "Prevedi ovu stranicu",
    original: "Izvornik",
    note: "Članci zadržavaju iste izvore i poveznice.",
    aria: "Odaberi jezik stranice"
  },
  {
    code: "de",
    short: "DE",
    name: "German",
    nativeName: "Deutsch",
    title: "Seitensprache",
    intro: "Sprache auswählen. Slowenisch ist die Originalversion; diese Seite kann als Übersetzung geöffnet werden.",
    translate: "Diese Seite übersetzen",
    original: "Original",
    note: "Artikel behalten dieselben Quellen und Links.",
    aria: "Seitensprache auswählen"
  }
];

const STORAGE_KEY = "blog-lab-language";

function safeInitialLanguage() {
  if (typeof window === "undefined") return "sl";
  const fromUrl = new URLSearchParams(window.location.search).get("lang");
  const saved = window.localStorage.getItem(STORAGE_KEY);
  const preferred = fromUrl || saved || "sl";
  return LANGUAGES.some((item) => item.code === preferred) ? preferred : "sl";
}

function translatedUrl(targetLanguage) {
  const url = new URL(window.location.href);
  url.searchParams.delete("lang");
  return `https://translate.google.com/translate?sl=auto&tl=${encodeURIComponent(targetLanguage)}&u=${encodeURIComponent(url.toString())}`;
}

export default function LanguageTools() {
  const [language, setLanguage] = useState(safeInitialLanguage);
  const active = useMemo(
    () => LANGUAGES.find((item) => item.code === language) || LANGUAGES[0],
    [language]
  );

  useEffect(() => {
    document.documentElement.lang = language;
    window.localStorage.setItem(STORAGE_KEY, language);
  }, [language]);

  function chooseLanguage(code) {
    setLanguage(code);
    const url = new URL(window.location.href);
    if (code === "sl") {
      url.searchParams.delete("lang");
    } else {
      url.searchParams.set("lang", code);
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  }

  function openTranslation() {
    if (language === "sl") return;
    window.open(translatedUrl(language), "_blank", "noopener,noreferrer");
  }

  return (
    <aside className="language-tools" aria-label={active.aria}>
      <div className="language-tools__topline">
        <span>{active.title}</span>
        <strong>{active.short}</strong>
      </div>
      <div className="language-tools__buttons" role="list" aria-label={active.aria}>
        {LANGUAGES.map((item) => (
          <button
            key={item.code}
            type="button"
            className={item.code === language ? "active" : ""}
            onClick={() => chooseLanguage(item.code)}
            aria-pressed={item.code === language}
            title={item.nativeName}
          >
            {item.short}
          </button>
        ))}
      </div>
      <p>{active.intro}</p>
      <div className="language-tools__actions">
        {language !== "sl" ? (
          <button type="button" onClick={openTranslation}>{active.translate} ↗</button>
        ) : (
          <span>{active.original}</span>
        )}
      </div>
      <small>{active.note}</small>
    </aside>
  );
}
