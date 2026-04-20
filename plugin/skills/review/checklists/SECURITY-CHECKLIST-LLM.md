# Security Checklist – LLM & Generative AI Applications

Concise checklist for security code reviews of applications that integrate Large Language Models or generative AI. Based on [OWASP Top 10 for LLM Applications:2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

**Applies to:** Any codebase that calls an LLM API, embeds a model, uses RAG pipelines, or exposes AI-generated output to users or downstream systems.

---

## Pre-Review
- [ ] Identify all LLM integration points (API calls, agent loops, RAG pipelines, tool/function calls)
- [ ] Identify trust boundaries: what reaches the model, what comes back, what acts on model output
- [ ] Review data classification – what user/system data is sent to the model

---

## LLM01:2025 - Prompt Injection

Attacker-controlled input manipulates the model into overriding instructions or performing unintended actions.

- [ ] User input is clearly delimited and never concatenated raw into system prompts
- [ ] Indirect prompt injection mitigated – content retrieved from web, files, or tools is treated as untrusted
- [ ] Model output is not re-injected into subsequent prompts without sanitization
- [ ] Agentic systems validate intent before executing tool calls derived from model output
- [ ] Output from model is not used to construct shell commands, SQL, or code without strict validation

---

## LLM02:2025 - Sensitive Information Disclosure

Model reveals confidential data from training, system prompts, or conversation context.

- [ ] System prompt does not contain secrets, credentials, or internal infrastructure details
- [ ] System prompt content treated as potentially leakable – no security-by-obscurity reliance
- [ ] PII and sensitive data minimized before being sent to the model
- [ ] Model responses are filtered before being returned to lower-trust clients
- [ ] Conversation history trimmed or redacted when passed across trust boundaries

---

## LLM03:2025 - Supply Chain

Vulnerabilities introduced via third-party models, datasets, fine-tuning pipelines, or LLM tooling.

- [ ] Model provenance verified – source, version, and integrity of base models documented
- [ ] Third-party plugins, tools, and agents reviewed before integration
- [ ] LLM SDKs and dependencies pinned and scanned for vulnerabilities
- [ ] Fine-tuning data sources vetted for poisoning risk
- [ ] Model updates treated as dependency updates – tested before rollout

---

## LLM04:2025 - Data and Model Poisoning

Malicious data introduced during training or fine-tuning alters model behavior.

- [ ] Training and fine-tuning data sourced from trusted, validated datasets
- [ ] Data pipelines have integrity checks (checksums, provenance tracking)
- [ ] Fine-tuned models evaluated for behavioral regressions and backdoors
- [ ] RAG knowledge base has access controls – untrusted content cannot be injected
- [ ] Anomalous model behavior monitored post-deployment

---

## LLM05:2025 - Improper Output Handling

Model output used in downstream systems without validation, enabling injection attacks.

- [ ] LLM output is never directly rendered as HTML without escaping (XSS risk)
- [ ] LLM output is never used in OS commands, SQL, or eval without strict sanitization
- [ ] Structured output (JSON, code) validated against a schema before use
- [ ] LLM-generated URLs or redirects validated before following
- [ ] Output passed to other agents or tools treated as untrusted input

---

## LLM06:2025 - Excessive Agency

Model granted too many permissions or takes autonomous actions beyond what's necessary.

- [ ] Principle of least privilege applied to all tools/functions exposed to the model
- [ ] Destructive or irreversible actions require human confirmation before execution
- [ ] Agent scope limited – model cannot access systems outside its defined task
- [ ] Tool call parameters validated before execution (model output is untrusted)
- [ ] Agentic loops have iteration/step limits to prevent runaway execution

---

## LLM07:2025 - System Prompt Leakage

System prompt contents exposed to users or attackers, revealing instructions or sensitive context.

- [ ] System prompt does not contain secrets, API keys, or internal logic that must stay hidden
- [ ] Application does not rely on system prompt secrecy as a security control
- [ ] Model is not instructed to repeat or summarize its system prompt on request
- [ ] Responses monitored for inadvertent system prompt disclosure patterns

---

## LLM08:2025 - Vector and Embedding Weaknesses

Vulnerabilities in RAG pipelines or vector stores enabling data poisoning, extraction, or bypass.

- [ ] Access controls on vector store match source document permissions
- [ ] Documents ingested into vector store are validated and from trusted sources
- [ ] Retrieval results are not blindly trusted – source and relevance verified
- [ ] Embedding model is pinned and sourced from a trusted provider
- [ ] Vector store queries cannot be manipulated by user-controlled input to retrieve unauthorized content

---

## LLM09:2025 - Misinformation

Model generates plausible but incorrect output that causes harm when acted upon.

- [ ] High-stakes decisions (medical, legal, financial) are not made solely on model output
- [ ] Model outputs in critical workflows are validated against authoritative sources
- [ ] Users are informed when content is AI-generated
- [ ] Hallucination-prone outputs (citations, code, facts) are verified before use
- [ ] Feedback mechanisms exist to capture and act on incorrect outputs

---

## LLM10:2025 - Unbounded Consumption

Excessive resource consumption through uncontrolled model usage, leading to DoS or cost exhaustion.

- [ ] Rate limiting applied per user/tenant on LLM API calls
- [ ] Maximum token limits enforced on input and output
- [ ] Cost budgets and alerts configured on LLM provider accounts
- [ ] Prompt size validated before submission – oversized inputs rejected
- [ ] Agentic loops have timeouts and hard step limits

---

## Automated Scanning

- [ ] Run Semgrep with `p/secrets` to detect hardcoded API keys for LLM providers
- [ ] Review LLM SDK usage for insecure patterns (raw string interpolation into prompts)
- [ ] Check for `eval()` or `exec()` calls consuming model output

---

## Issue Classification

### 🚨 CRITICAL (Immediate Fix Required)
- Prompt injection enabling privilege escalation or data exfiltration
- LLM output used in `eval`, OS commands, or SQL without validation
- PII or credentials sent to external model APIs without authorization
- Excessive agency – model can take irreversible actions without confirmation

### ⚠️ HIGH (Fix Before Release)
- System prompt leakage of sensitive internal logic
- RAG store accessible beyond document-level permissions
- No rate limiting on LLM endpoints (cost/DoS exposure)
- Model output rendered as raw HTML (XSS)

### 🔶 MEDIUM (Fix Soon)
- Missing output schema validation
- Conversation history passed across trust boundaries without redaction
- No user disclosure for AI-generated content in high-stakes contexts

### 💡 LOW (Track & Plan)
- Model version not pinned
- Missing cost alerting
- Hallucination risk in non-critical informational output
