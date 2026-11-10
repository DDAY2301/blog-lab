import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import BlogLabMagazine from "./BlogLabMagazine.jsx";
import LanguageTools from "./LanguageTools.jsx";
import PrivateTerminalAccess from "./PrivateTerminalAccess.jsx";
import "./styles.css";
import "./production.css";
import "./language-tools.css";
import "./product-platform.css";
import "./editorial-theme.css";
import "./final-polish.css";
import "./painterly-theme.css";
import "./painterly-gallery-v3.css";
import "./painterly-original-v4.css";
import "./painterly-atelier-v5.css";
import "./painterly-photo-v6.css";
import "./bloglab-home-v1.css";
import "./bloglab-magazine.css";
import "./bloglab-real-editorial.css";

// Keep article links, editorial tools and all existing workflows available in the classic view.
// The redesigned homepage is the default only for the public root route.
const currentUrl = new URL(window.location.href);
const existingAppRoute = ["view", "article", "post", "slug", "category", "tab", "id"]
  .some((key) => currentUrl.searchParams.has(key)) || currentUrl.hash.startsWith("#/");
const isPublicHome = ["/", "/index.html"].includes(currentUrl.pathname) && !existingAppRoute;

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {isPublicHome ? <BlogLabMagazine /> : <App />}
    <LanguageTools />
    <PrivateTerminalAccess />
  </React.StrictMode>,
);
