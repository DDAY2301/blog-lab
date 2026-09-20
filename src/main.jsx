import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import LanguageTools from "./LanguageTools.jsx";
import PrivateTerminalAccess from "./PrivateTerminalAccess.jsx";
import "./styles.css";
import "./production.css";
import "./language-tools.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
    <LanguageTools />
    <PrivateTerminalAccess />
  </React.StrictMode>,
);
