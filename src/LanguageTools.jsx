import { useEffect, useMemo, useRef, useState } from "react";

const LANGUAGES = [
  {
    code: "sl",
    googleCode: "sl",
    short: "SL",
    name: "Slovenščina",
    nativeName: "Slovenščina",
    title: "Jezik strani",
    intro: "Izberi jezik. Prevajalnik prevede dejansko stran na istem naslovu, vključno s članki, meniji in gumbi.",
    activeLabel: "Izvirnik",
    statusReady: "Prevajalnik je pripravljen.",
    statusLoading: "Prevajalnik se nalaga …",
    statusTranslated: "Prikazana je izvirna slovenska stran.",
    note: "Viri, povezave in struktura člankov ostanejo enaki.",
    aria: "Izberi jezik strani"
  },
  {
    code: "en",
    googleCode: "en",
    short: "EN",
    name: "English",
    nativeName: "English",
    title: "Site language",
    intro: "Choose a language. The translator changes the actual page in place, including articles, menus and buttons.",
    activeLabel: "English",
    statusReady: "Translator is ready.",
    statusLoading: "Translator is loading …",
    statusTranslated: "The page is being shown in English.",
    note: "Sources, links and article structure stay unchanged.",
    aria: "Choose site language"
  },
  {
    code: "hr",
    googleCode: "hr",
    short: "HR",
    name: "Croatian",
    nativeName: "Hrvatski",
    title: "Jezik stranice",
    intro: "Odaberi jezik. Prevoditelj prevodi stvarnu stranicu na istoj adresi, uključujući članke, izbornike i gumbe.",
    activeLabel: "Hrvatski",
    statusReady: "Prevoditelj je spreman.",
    statusLoading: "Prevoditelj se učitava …",
    statusTranslated: "Stranica se prikazuje na hrvatskom.",
    note: "Izvori, poveznice i struktura članaka ostaju isti.",
    aria: "Odaberi jezik stranice"
  },
  {
    code: "de",
    googleCode: "de",
    short: "DE",
    name: "German",
    nativeName: "Deutsch",
    title: "Seitensprache",
    intro: "Sprache auswählen. Der Übersetzer überträgt die echte Seite direkt hier, einschließlich Artikel, Menüs und Buttons.",
    activeLabel: "Deutsch",
    statusReady: "Übersetzer ist bereit.",
    statusLoading: "Übersetzer wird geladen …",
    statusTranslated: "Die Seite wird auf Deutsch angezeigt.",
    note: "Quellen, Links und Artikelstruktur bleiben unverändert.",
    aria: "Seitensprache auswählen"
  }
];

const STORAGE_KEY = "blog-lab-language";
const COLLAPSE_STORAGE_KEY = "blog-lab-language-tools-collapsed";
const SCRIPT_ID = "blog-lab-google-translate-script";
const ELEMENT_ID = "google_translate_element";

function safeInitialLanguage() {
  if (typeof window === "undefined") return "sl";
  const fromUrl = new URLSearchParams(window.location.search).get("lang");
  const saved = window.localStorage.getItem(STORAGE_KEY);
  const preferred = fromUrl || saved || "sl";
  return LANGUAGES.some((item) => item.code === preferred) ? preferred : "sl";
}

function safeInitialCollapsed() {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(COLLAPSE_STORAGE_KEY) === "1";
}

function expireGoogleTranslateCookies() {
  if (typeof document === "undefined") return;
  const host = window.location.hostname;
  const domains = [host, `.${host}`].filter(Boolean);
  document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
  domains.forEach((domain) => {
    document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=${domain}`;
  });
}

function setGoogleTranslateCookie(targetCode) {
  if (typeof document === "undefined") return;
  const value = `/sl/${targetCode}`;
  const host = window.location.hostname;
  document.cookie = `googtrans=${value}; path=/; max-age=31536000; SameSite=Lax`;
  if (host && host.includes(".")) {
    document.cookie = `googtrans=${value}; path=/; domain=.${host}; max-age=31536000; SameSite=Lax`;
  }
}

function loadTranslateScript(setReady) {
  if (typeof window === "undefined") return;

  if (!document.getElementById(ELEMENT_ID)) {
    const holder = document.createElement("div");
    holder.id = ELEMENT_ID;
    holder.setAttribute("aria-hidden", "true");
    document.body.appendChild(holder);
  }

  window.googleTranslateElementInit = () => {
    if (!window.google?.translate?.TranslateElement) return;
    new window.google.translate.TranslateElement(
      {
        pageLanguage: "sl",
        includedLanguages: "sl,en,hr,de",
        autoDisplay: false
      },
      ELEMENT_ID
    );
    setReady(true);
  };

  if (window.google?.translate?.TranslateElement) {
    window.googleTranslateElementInit();
    return;
  }

  if (document.getElementById(SCRIPT_ID)) return;

  const script = document.createElement("script");
  script.id = SCRIPT_ID;
  script.async = true;
  script.src = "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
  document.body.appendChild(script);
}

function findTranslateSelect() {
  return document.querySelector("select.goog-te-combo");
}

function dispatchNativeChange(element) {
  element.dispatchEvent(new Event("change", { bubbles: true }));
}

function applyGoogleTranslate(targetCode) {
  if (targetCode === "sl") {
    expireGoogleTranslateCookies();
    const select = findTranslateSelect();
    if (select) {
      select.value = "";
      dispatchNativeChange(select);
    }
    return true;
  }

  setGoogleTranslateCookie(targetCode);
  const select = findTranslateSelect();
  if (!select) return false;
  select.value = targetCode;
  dispatchNativeChange(select);
  return true;
}

export default function LanguageTools() {
  const [language, setLanguage] = useState(safeInitialLanguage);
  const [isCollapsed, setIsCollapsed] = useState(safeInitialCollapsed);
  const [translatorReady, setTranslatorReady] = useState(false);
  const retryRef = useRef(null);
  const mutationTimerRef = useRef(null);
  const active = useMemo(
    () => LANGUAGES.find((item) => item.code === language) || LANGUAGES[0],
    [language]
  );

  useEffect(() => {
    loadTranslateScript(setTranslatorReady);
    return () => {
      if (retryRef.current) window.clearInterval(retryRef.current);
      if (mutationTimerRef.current) window.clearTimeout(mutationTimerRef.current);
    };
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
    window.localStorage.setItem(STORAGE_KEY, language);
  }, [language]);

  useEffect(() => {
    window.localStorage.setItem(COLLAPSE_STORAGE_KEY, isCollapsed ? "1" : "0");
  }, [isCollapsed]);

  useEffect(() => {
    const url = new URL(window.location.href);
    if (language === "sl") {
      url.searchParams.delete("lang");
    } else {
      url.searchParams.set("lang", language);
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  }, [language]);

  useEffect(() => {
    if (retryRef.current) window.clearInterval(retryRef.current);

    const target = active.googleCode;
    const tryApply = () => applyGoogleTranslate(target);

    if (tryApply()) return;

    retryRef.current = window.setInterval(() => {
      if (tryApply() && retryRef.current) {
        window.clearInterval(retryRef.current);
        retryRef.current = null;
        setTranslatorReady(true);
      }
    }, 700);

    return () => {
      if (retryRef.current) {
        window.clearInterval(retryRef.current);
        retryRef.current = null;
      }
    };
  }, [active.googleCode]);

  useEffect(() => {
    if (language === "sl") return undefined;

    const observer = new MutationObserver(() => {
      if (mutationTimerRef.current) window.clearTimeout(mutationTimerRef.current);
      mutationTimerRef.current = window.setTimeout(() => {
        applyGoogleTranslate(active.googleCode);
      }, 450);
    });

    observer.observe(document.getElementById("root") || document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });

    return () => {
      observer.disconnect();
      if (mutationTimerRef.current) {
        window.clearTimeout(mutationTimerRef.current);
        mutationTimerRef.current = null;
      }
    };
  }, [active.googleCode, language]);

  function chooseLanguage(code) {
    setLanguage(code);
  }

  function resetOriginal() {
    setLanguage("sl");
    expireGoogleTranslateCookies();
    window.setTimeout(() => window.location.reload(), 150);
  }

  return (
    <aside className={`language-tools ${isCollapsed ? "is-collapsed" : ""}`} aria-label={active.aria}>
      <div className="language-tools__topline">
        <span>{isCollapsed ? active.short : active.title}</span>
        <div className="language-tools__top-actions">
          <strong>{active.short}</strong>
          <button
            type="button"
            className="language-tools__collapse"
            onClick={() => setIsCollapsed((value) => !value)}
            aria-expanded={!isCollapsed}
            title={isCollapsed ? "Odpri prevajalnik" : "Zmanjšaj prevajalnik"}
          >
            {isCollapsed ? "+" : "–"}
          </button>
        </div>
      </div>

      {!isCollapsed && (
        <>
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
            {language === "sl" ? (
              <span>{active.activeLabel}</span>
            ) : (
              <button type="button" onClick={() => applyGoogleTranslate(active.googleCode)}>
                {active.activeLabel} · prevede stran
              </button>
            )}
            {language !== "sl" && (
              <button type="button" className="secondary" onClick={resetOriginal}>
                SL izvirnik
              </button>
            )}
          </div>
          <small>
            {translatorReady ? active.statusTranslated : active.statusLoading} {active.note}
          </small>
        </>
      )}
    </aside>
  );
}
