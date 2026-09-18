import fs from "node:fs";

const source = fs.readFileSync("terminal/worker/src/index.js", "utf8");

function extractTemplate(name, endMarker) {
  const start = source.indexOf(`const ${name} = \``);
  if (start < 0) throw new Error(`${name} template not found`);
  const bodyStart = start + `const ${name} = \``.length;
  const end = source.indexOf(endMarker, bodyStart);
  if (end < 0) throw new Error(`${name} end marker not found`);
  return source.slice(bodyStart, end);
}

function renderTemplate(raw) {
  return Function("return `" + raw.replace(/\`/g, "\\\`") + "`")();
}

function validateHtmlScripts(name, raw) {
  const html = renderTemplate(raw);
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  if (!scripts.length) throw new Error(`${name} has no embedded script`);
  scripts.forEach((script, index) => {
    try {
      new Function(script);
    } catch (error) {
      throw new Error(`${name} script #${index + 1} failed to parse: ${error.message}`);
    }
  });
}

validateHtmlScripts("LOGIN_PAGE", extractTemplate("LOGIN_PAGE", "`;\n\nconst PAGE"));
validateHtmlScripts("PAGE", extractTemplate("PAGE", "`;\n\nexport default"));

console.log("Worker embedded browser JavaScript parses successfully.");
