import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";

const CONFIG_URL = `${import.meta.env.BASE_URL}terminal-config.json`;

function cleanUrl(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  try {
    const url = new URL(text);
    return url.protocol === "https:" ? url.href : "";
  } catch {
    return "";
  }
}

export default function PrivateTerminalAccess() {
  const [host, setHost] = useState(null);
  const [terminalUrl, setTerminalUrl] = useState(() => cleanUrl(import.meta.env.VITE_PRIVATE_TERMINAL_URL));
  const [configLoaded, setConfigLoaded] = useState(Boolean(terminalUrl));

  useEffect(() => {
    const attach = () => {
      const header = document.querySelector(".site-header");
      if (header) setHost(header);
      return Boolean(header);
    };

    if (attach()) return undefined;
    const observer = new MutationObserver(() => {
      if (attach()) observer.disconnect();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (terminalUrl) return undefined;
    let active = true;
    fetch(CONFIG_URL, { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((config) => {
        if (!active) return;
        setTerminalUrl(cleanUrl(config?.terminalUrl));
        setConfigLoaded(true);
      })
      .catch(() => {
        if (active) setConfigLoaded(true);
      });
    return () => {
      active = false;
    };
  }, [terminalUrl]);

  const fallbackUrl = useMemo(
    () => `${import.meta.env.BASE_URL}terminal-access.html`,
    []
  );

  if (!host) return null;

  return createPortal(
    <a
      className={`terminal-login-button${terminalUrl ? " is-ready" : " is-setup"}`}
      href={terminalUrl || fallbackUrl}
      target={terminalUrl ? "_blank" : undefined}
      rel={terminalUrl ? "noreferrer" : undefined}
      aria-label={terminalUrl ? "Prijava v zasebni Blog Lab terminal" : "Nastavitev zasebnega Blog Lab terminala"}
      title={terminalUrl ? "Prijava prek Cloudflare Access" : configLoaded ? "Terminal še ni povezan z javnim URL-jem" : "Preverjam terminal"}
    >
      <svg aria-hidden="true" viewBox="0 0 24 24">
        <path d="M12 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z" />
        <path d="M4.5 21a7.5 7.5 0 0 1 15 0" />
      </svg>
      <span>Prijava</span>
    </a>,
    host
  );
}
