import { useEffect, useMemo, useState } from "react";

const DEFAULT_STATUS = {
  version: "auth-v6.27-production",
  demo_ready: true,
  trial_signup_ready: true,
  terminal_ready: true,
};

function StatusPill({ ok, children }) {
  return <span className={ok ? "product-status ok" : "product-status wait"}><i />{children}</span>;
}

function Step({ number, title, children }) {
  return (
    <article className="product-step">
      <span>{number}</span>
      <div><h3>{title}</h3><p>{children}</p></div>
    </article>
  );
}

export default function ProductPlatform({ terminalUrl }) {
  const [status, setStatus] = useState(DEFAULT_STATUS);
  const base = useMemo(() => String(terminalUrl || "").replace(/\/$/, ""), [terminalUrl]);

  useEffect(() => {
    let active = true;
    fetch(`${base}/api/public/product-status`, { cache: "no-store" })
      .then((response) => response.ok ? response.json() : DEFAULT_STATUS)
      .then((data) => { if (active) setStatus({ ...DEFAULT_STATUS, ...data }); })
      .catch(() => {});
    return () => { active = false; };
  }, [base]);

  const open = (path) => window.open(`${base}${path}`, "_blank", "noopener,noreferrer");

  return (
    <section className="product-page">
      <div className="product-hero container">
        <div className="product-hero-copy">
          <span className="product-kicker">BLOG LAB · AUTONOMOUS PUBLISHING</span>
          <h1>Od ukaza do objave.<br /><em>Agent opravi operativno delo.</em></h1>
          <p>
            Blog Lab poveže uredniški terminal, chatbot, avtomatsko objavljanje,
            varnostne teste in self-heal v en nadzorovan sistem. Človek določi cilj;
            sistem izvede, preveri in poroča o rezultatu.
          </p>
          <div className="product-actions">
            <button className="primary" onClick={() => open("/demo")}>Odpri interaktivni demo ↗</button>
            <button className="secondary" onClick={() => open("/join")}>Ustvari demo račun</button>
          </div>
          <div className="product-live-row">
            <StatusPill ok={status.demo_ready}>Demo pripravljen</StatusPill>
            <StatusPill ok={status.trial_signup_ready}>Onboarding aktiven</StatusPill>
            <StatusPill ok={status.terminal_ready}>Terminal online</StatusPill>
          </div>
        </div>
        <div className="product-console" aria-label="Primer Blog Lab terminala">
          <div className="product-console-top"><span /><span /><span /><b>Blog Lab Terminal</b></div>
          <div className="product-console-body">
            <small>OPERATER</small>
            <p>&gt; napiši članek, preveri vire in ga objavi po urniku</p>
            <div className="console-line success">✓ ukaz razumljen · article</div>
            <div className="console-line">→ evidence + source validation</div>
            <div className="console-line">→ build + security tests</div>
            <div className="console-line">→ deploy + live probe</div>
            <div className="console-line success">✓ izvedba zaključena</div>
          </div>
        </div>
      </div>

      <div className="product-proof container">
        <div><strong>300+</strong><span>avtomatskih regresijskih preverjanj</span></div>
        <div><strong>2.400</strong><span>stress-routing preverjanj</span></div>
        <div><strong>4</strong><span>jeziki ukazov</span></div>
        <div><strong>24/7</strong><span>watchdog + self-heal logika</span></div>
      </div>

      <section className="product-section container">
        <div className="product-section-head">
          <span>KAJ DEJANSKO PRODAJAMO</span>
          <h2>Operativni AI sistem, ne samo chat okno.</h2>
          <p>Vsak sloj ima jasno nalogo in preverljiv rezultat.</p>
        </div>
        <div className="product-feature-grid">
          <article><b>01</b><h3>Uredniški terminal</h3><p>Ukazi v naravnem jeziku za članke, stran, urnik, diagnostiko in nadzor agenta.</p></article>
          <article><b>02</b><h3>Agent + publisher</h3><p>Priprava vsebine, varna izvedba, build, commit in objava brez ročnega klikanja po več orodjih.</p></article>
          <article><b>03</b><h3>Chatbot pomočnik</h3><p>Operativna diagnostika za status, workflow, DNS in napake z lokalnim fallbackom ob AI izpadu.</p></article>
          <article><b>04</b><h3>Self-heal</h3><p>Ob neuspehu ponovno nanese preverjene popravke, požene teste in preveri živi Worker.</p></article>
          <article><b>05</b><h3>Idempotency</h3><p>Dvojni klik ali ponovni retry ne sprožita iste spremembe dvakrat.</p></article>
          <article><b>06</b><h3>Production gate</h3><p>Deploy se ne izvede, če static, runtime, execution ali stress testi niso uspešni.</p></article>
        </div>
      </section>

      <section className="product-flow">
        <div className="container">
          <div className="product-section-head light">
            <span>DEMO SCENARIJ</span>
            <h2>V petih korakih pokažeš, zakaj je sistem uporaben.</h2>
          </div>
          <div className="product-steps">
            <Step number="1" title="Vpiši cilj">Na primer: »pripravi članek, preveri vire in objavi«.</Step>
            <Step number="2" title="Router razume namen">Ukaz se razvrsti na article, site ali control in popravi pogoste tipkarske napake.</Step>
            <Step number="3" title="Agent izvede">Workflow dobi šifriran ukaz in dela samo z dovoljenimi potmi ter procesi.</Step>
            <Step number="4" title="Sistem preveri">Pred objavo se zaženejo varnostni, runtime in build testi.</Step>
            <Step number="5" title="Self-heal prevzame napake">Če preverjanje pade, repair loop preveri trenutno main vejo in obnovi znane invariante.</Step>
          </div>
        </div>
      </section>

      <section className="product-section product-commercial container">
        <div className="product-section-head">
          <span>ZA KOMERCIALNO UPORABO</span>
          <h2>Izberi obseg, ne novega kupa orodij.</h2>
          <p>Demo pokaže delovanje. Produkcijska aktivacija se nato prilagodi številu strani, uporabnikov in zahtevani stopnji avtomatizacije.</p>
        </div>
        <div className="product-package-grid">
          <article className="product-package">
            <span>PILOT</span>
            <h3>1 znamka / 1 portal</h3>
            <p>Za podjetje ali organizacijo, ki želi uredniški terminal, publisher, osnovni QA in varen deployment.</p>
            <ul><li>onboarding</li><li>publisher agent</li><li>production gate</li><li>osnovni self-heal</li></ul>
            <button className="secondary" onClick={() => open("/join")}>Preizkusi demo ↗</button>
          </article>
          <article className="product-package featured-package">
            <span>GROWTH</span>
            <h3>Več vsebin in ekip</h3>
            <p>Za redno produkcijo, kjer so pomembni urniki, ponovljivi procesi, diagnostika in hitrejša obnova po napaki.</p>
            <ul><li>več urnikov</li><li>napredni QA</li><li>watchdog</li><li>operativni chatbot</li></ul>
            <button className="primary" onClick={() => open("/join")}>Začni onboarding ↗</button>
          </article>
          <article className="product-package">
            <span>AGENCY</span>
            <h3>Več strank / več portalov</h3>
            <p>Za agencijski model z ločenimi delovnimi prostori, nadzorom izvajanja in prilagojenimi produkcijskimi pravili.</p>
            <ul><li>multi-workspace</li><li>ločeni procesi</li><li>monitoring</li><li>prilagojena aktivacija</li></ul>
            <button className="secondary" onClick={() => open("/join")}>Odpri demo račun ↗</button>
          </article>
        </div>
        <p className="product-commercial-note">Komercialna cena se določi po dejanskem obsegu integracij, številu portalov in zahtevani infrastrukturi. Javni demo ne zahteva produkcijskih GitHub ali Cloudflare dovoljenj.</p>
      </section>

      <section className="product-onboarding container">
        <div>
          <span className="product-kicker">EARLY ACCESS</span>
          <h2>Prvi uporabnik lahko začne brez dostopa do produkcijskega terminala.</h2>
          <p>
            Demo račun je ločen od operaterskega sistema. Uporabnik opravi onboarding,
            izbere primer uporabe in v varnem okolju preizkusi ukaze, brez možnosti
            posega v produkcijski GitHub ali objave.
          </p>
        </div>
        <div className="product-onboarding-card">
          <span>1</span><p>Profil in namen uporabe</p>
          <span>2</span><p>Delovni prostor in pogostost objav</p>
          <span>3</span><p>Interaktivni terminalski demo</p>
          <span>4</span><p>Pripravljen za aktivacijo plačljivega paketa</p>
          <button className="primary" onClick={() => open("/join")}>Začni onboarding ↗</button>
        </div>
      </section>

      <section className="product-cta">
        <div className="container">
          <div><span>LIVE PRODUCT</span><h2>Blog Lab je pripravljen za predstavitev.</h2></div>
          <div className="product-actions">
            <button className="primary" onClick={() => open("/demo")}>Pokaži demo</button>
            <button className="secondary" onClick={() => open("/")}>Zasebni terminal ↗</button>
          </div>
        </div>
      </section>
    </section>
  );
}
