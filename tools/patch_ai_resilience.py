from pathlib import Path
import re
import textwrap

worker = Path('terminal/worker/src/index.js')
s = worker.read_text(encoding='utf-8')
s = s.replace('version: "auth-v6.17-ai-resilience"', 'version: "auth-v6.18-ai-diagnostics-fallback"')

m = re.search(r'async function runWorkersAiWithRetry\(env, request, attempts = 3\) \{.*?\n\}\n\nasync function generateArticleWithWorkersAi', s, re.S)
if not m:
    raise SystemExit('runWorkersAiWithRetry block not found')

block = r'''function aiGatewayOptions(env, purpose = "general", cacheKey = "") {
  const id = String(env.AI_GATEWAY_ID || env.WORKERS_AI_GATEWAY_ID || "").trim();
  if (!id) return undefined;
  const cacheTtl = Math.max(0, Math.min(Number(env.AI_GATEWAY_CACHE_TTL || 900) || 0, 86400));
  return {
    gateway: {
      id,
      skipCache: String(env.AI_GATEWAY_SKIP_CACHE || "").toLowerCase() === "true",
      cacheTtl,
      cacheKey: cacheKey || undefined,
      collectLog: true,
      metadata: { app: "blog-lab", purpose }
    }
  };
}

function workersAiModelCandidates(env) {
  const raw = String(env.WORKERS_AI_MODELS || "").trim();
  const configured = raw
    ? raw.split(/[\n,]+/).map((x) => x.trim()).filter(Boolean)
    : [];
  const defaults = [
    "@cf/zai-org/glm-4.7-flash",
    "@cf/meta/llama-3.1-8b-instruct-fp8",
    "@cf/google/gemma-3-12b-it",
    "@cf/meta/llama-3.1-8b-instruct-fast"
  ];
  return [...new Set([...configured, ...defaults])].slice(0, 8);
}

function sanitizeAiError(error) {
  const message = String(error?.message || error || "").replace(/\s+/g, " ").trim();
  const name = String(error?.name || "Error").slice(0, 80);
  const code = String(error?.code || error?.cause?.code || "").slice(0, 80);
  return { name, code: code || undefined, message: message.slice(0, 500) };
}

async function runWorkersAiWithRetry(env, request, attempts = 3, options = {}) {
  const errors = [];
  const total = Math.max(1, Math.min(Number(attempts) || 1, 3));
  const purpose = options.purpose || "general";
  const cacheKey = options.cacheKey || `${purpose}:${JSON.stringify(request).slice(0, 800)}`;
  const gatewayOptions = aiGatewayOptions(env, purpose, cacheKey);
  for (const model of workersAiModelCandidates(env)) {
    for (let attempt = 1; attempt <= total; attempt += 1) {
      try {
        const result = await env.AI.run(model, request, gatewayOptions);
        if (result && typeof result === "object") {
          try { Object.defineProperty(result, "_bloglab_model", { value: model, enumerable: false }); } catch {}
          try { Object.defineProperty(result, "_bloglab_gateway_log_id", { value: env.AI?.aiGatewayLogId || null, enumerable: false }); } catch {}
          try { Object.defineProperty(result, "_bloglab_attempts", { value: { model, attempt, errors }, enumerable: false }); } catch {}
        }
        return result;
      } catch (error) {
        const detail = { model, attempt, ...sanitizeAiError(error) };
        errors.push(detail);
        if (nonRetryableWorkersAiError(error)) {
          const nonRetry = new Error(`Workers AI non-retryable failure on ${model}: ${detail.message}`);
          nonRetry.aiErrors = errors;
          nonRetry.aiLastModel = model;
          throw nonRetry;
        }
        if (attempt < total) await new Promise((resolve) => setTimeout(resolve, attempt * 220));
      }
    }
  }
  const last = errors[errors.length - 1] || { message: "unknown Workers AI failure" };
  const failed = new Error(`Workers AI inference failed after ${errors.length} attempts. Last ${last.model || "model"}: ${last.message}`);
  failed.aiErrors = errors;
  failed.aiLastModel = last.model || null;
  throw failed;
}

async function diagnoseWorkersAi(env) {
  const available = Boolean(env.AI && typeof env.AI.run === "function");
  const models = workersAiModelCandidates(env);
  const gateway = Boolean(String(env.AI_GATEWAY_ID || env.WORKERS_AI_GATEWAY_ID || "").trim());
  const results = [];
  if (!available) return { ok: false, available, gateway, models, results, code: "AI_BINDING_MISSING" };
  for (const model of models.slice(0, 4)) {
    const started = Date.now();
    try {
      const result = await env.AI.run(
        model,
        {
          messages: [
            { role: "system", content: "Return only compact JSON." },
            { role: "user", content: "Return {\"ok\":true,\"service\":\"blog-lab\"}." }
          ],
          response_format: { type: "json_object" },
          max_tokens: 80,
          temperature: 0
        },
        aiGatewayOptions(env, "diagnostics", `diagnostics:${model}`)
      );
      results.push({
        model,
        ok: true,
        ms: Date.now() - started,
        gateway_log_id: env.AI?.aiGatewayLogId || null,
        keys: result && typeof result === "object" ? Object.keys(result).slice(0, 8) : []
      });
      return { ok: true, available, gateway, models, results };
    } catch (error) {
      results.push({ model, ok: false, ms: Date.now() - started, ...sanitizeAiError(error), gateway_log_id: env.AI?.aiGatewayLogId || null });
    }
  }
  return { ok: false, available, gateway, models, results, code: "ALL_MODELS_FAILED" };
}

async function generateArticleWithWorkersAi'''

s = s[:m.start()] + block + s[m.end():]

replacements = [
    ('max_tokens: 2800,\n      temperature: 0.32,\n      repetition_penalty: 1.08,\n    });', 'max_tokens: 2800,\n      temperature: 0.32,\n      repetition_penalty: 1.08,\n    }, 2, { purpose: "article-write", cacheKey: `article:${category}:${sourceJson.slice(0, 400)}` });'),
    ('max_tokens: 900,\n      temperature: 0.05,\n      repetition_penalty: 1.04,\n    });', 'max_tokens: 900,\n      temperature: 0.05,\n      repetition_penalty: 1.04,\n    }, 2, { purpose: "article-review", cacheKey: `review:${userPrompt.slice(0, 400)}` });'),
    ('max_tokens: 2800,\n      temperature: 0.20,\n      repetition_penalty: 1.06,\n    });', 'max_tokens: 2800,\n      temperature: 0.20,\n      repetition_penalty: 1.06,\n    }, 2, { purpose: "site-edit", cacheKey: `site:${requestText.slice(0, 400)}` });'),
    ('max_tokens: 3200,\n      temperature: 0.05,\n      repetition_penalty: 1.04,\n    });', 'max_tokens: 3200,\n      temperature: 0.05,\n      repetition_penalty: 1.04,\n    }, 2, { purpose: "self-heal", cacheKey: `repair:${requestText.slice(0, 400)}` });'),
    ('max_tokens: 180,\n      temperature: 0.02\n    });', 'max_tokens: 180,\n      temperature: 0.02\n    }, 1, { purpose: "intent-classifier", cacheKey: `intent:${String(command || "").slice(0, 300)}` });')
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f'missing replacement marker: {old[:40]}')
    s = s.replace(old, new, 1)

s = s.replace('model: "@cf/zai-org/glm-4.7-flash",\n    usage: result?.usage || null,', 'model: result?._bloglab_model || "workers-ai",\n    ai_gateway_log_id: result?._bloglab_gateway_log_id || null,\n    ai_attempts: result?._bloglab_attempts || null,\n    usage: result?.usage || null,')
s = s.replace('detail: String(error?.message || error || "").slice(0, 300),', 'detail: String(error?.message || error || "").slice(0, 500),\n      attempts: Array.isArray(error?.aiErrors) ? error.aiErrors.slice(-8) : [],\n      last_model: error?.aiLastModel || null,')
s = s.replace('free_tier_compatible: true\n      });', 'free_tier_compatible: true,\n        ai_gateway_configured: Boolean(String(env.AI_GATEWAY_ID || env.WORKERS_AI_GATEWAY_ID || "").trim()),\n        ai_gateway_cache_ttl: Number(env.AI_GATEWAY_CACHE_TTL || 900) || 900,\n        ai_model_fallbacks: workersAiModelCandidates(env)\n      });', 1)
route = '    if (request.method === "POST" && url.pathname === "/api/ai/write") {'
diag = '''    if (request.method === "GET" && url.pathname === "/api/ai/diagnostics") {
      if (!(await internalWriterAuthorized(request, env))) {
        return json({ error: "Nepooblaščen interni AI diagnostics klic.", code: "AI_UNAUTHORIZED" }, 401);
      }
      const result = await diagnoseWorkersAi(env);
      return json(result, result.ok ? 200 : 502);
    }

'''
if route not in s:
    raise SystemExit('route marker not found')
s = s.replace(route, diag + route, 1)
worker.write_text(s, encoding='utf-8')

provider = Path('agents/blog-lab-publisher/services/ai_provider.py')
p = provider.read_text(encoding='utf-8')
p = p.replace('from urllib.request import Request, urlopen', 'from urllib.request import Request, urlopen\nfrom urllib.error import HTTPError')
p = p.replace('''    try:\n        with urlopen(req, timeout=120) as response:\n            data = json.loads(response.read().decode("utf-8"))\n    except Exception as exc:\n        raise AIUnavailable(f"Workers AI writer ni uspel: {exc}") from exc\n''', '''    try:\n        with urlopen(req, timeout=120) as response:\n            data = json.loads(response.read().decode("utf-8"))\n    except HTTPError as exc:\n        detail = ""\n        try:\n            detail = exc.read().decode("utf-8", errors="replace")\n        except Exception:\n            detail = ""\n        raise AIUnavailable(f"Workers AI writer ni uspel: HTTP {exc.code}: {detail[:700]}") from exc\n    except Exception as exc:\n        raise AIUnavailable(f"Workers AI writer ni uspel: {exc}") from exc\n''', 1)
p = p.replace('''    try:\n        with urlopen(req, timeout=90) as response:\n            data = json.loads(response.read().decode("utf-8"))\n    except Exception as exc:\n        raise AIUnavailable(f"Workers AI review ni uspel: {exc}") from exc\n''', '''    try:\n        with urlopen(req, timeout=90) as response:\n            data = json.loads(response.read().decode("utf-8"))\n    except HTTPError as exc:\n        detail = ""\n        try:\n            detail = exc.read().decode("utf-8", errors="replace")\n        except Exception:\n            detail = ""\n        raise AIUnavailable(f"Workers AI review ni uspel: HTTP {exc.code}: {detail[:700]}") from exc\n    except Exception as exc:\n        raise AIUnavailable(f"Workers AI review ni uspel: {exc}") from exc\n''', 1)
provider.write_text(p, encoding='utf-8')

Path('docs/ai-resilience.md').write_text(textwrap.dedent('''\
# Blog Lab AI resilience

Runtime order:
1. Cloudflare Workers AI through `env.AI.run()`.
2. Model fallback list from `WORKERS_AI_MODELS`, then built-in defaults.
3. Optional AI Gateway when `AI_GATEWAY_ID` or `WORKERS_AI_GATEWAY_ID` is set.
4. GitHub Actions external model fallback when `MODEL_API_KEY`, `MODEL_BASE_URL`, and `MODEL_NAME` are configured.
5. Deterministic fallback publisher if AI providers are unavailable.

Endpoints:
- `GET /health` shows AI model fallbacks and AI Gateway readiness.
- `GET /api/ai/diagnostics` tests live model fallback and requires `Authorization: Bearer <TERMINAL_COMMAND_KEY>`.

Optional Cloudflare Worker variables/secrets:
- `AI_GATEWAY_ID=default`
- `AI_GATEWAY_CACHE_TTL=900`
- `AI_GATEWAY_SKIP_CACHE=false`
- `WORKERS_AI_MODELS=@cf/zai-org/glm-4.7-flash,@cf/meta/llama-3.1-8b-instruct-fp8,@cf/google/gemma-3-12b-it`

Optional GitHub Actions repository secrets:
- `MODEL_API_KEY`
- `MODEL_BASE_URL`
- `MODEL_NAME`
'''), encoding='utf-8')
