# Security Checklist — API Security

Concise checklist for security code reviews of APIs (REST, GraphQL, gRPC, and similar). Based on [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x00-header/).

**Applies to:** Any codebase that exposes or consumes HTTP/API endpoints, including microservices, BFFs, and public/private APIs. Complements the Web checklist — use both when the application has a web frontend consuming an API.

---

## Pre-Review
- [ ] Map all exposed API endpoints (routes, methods, parameters)
- [ ] Identify which endpoints are public vs. authenticated vs. admin
- [ ] Review data classification — which endpoints handle sensitive or privileged data

---

## API1:2023 - Broken Object Level Authorization (BOLA)

Object IDs in requests are not validated against the requesting user's ownership, enabling data access across accounts.

- [ ] Every endpoint that accepts an object ID verifies the caller owns or has explicit access to that object
- [ ] Object IDs are not predictable/sequential in sensitive contexts (use UUIDs or opaque tokens)
- [ ] Indirect access (e.g., nested resources) validated at every level
- [ ] Tests exist for accessing another user's resources with valid credentials

---

## API2:2023 - Broken Authentication

Weak or missing authentication mechanisms allow attackers to impersonate users.

- [ ] All non-public endpoints require authentication
- [ ] JWT tokens validated fully (signature, expiry, issuer, audience)
- [ ] API keys rotatable and revocable; not embedded in client-side code
- [ ] No credentials in query strings (logged in access logs)
- [ ] Token refresh flows do not bypass authentication requirements
- [ ] Brute force protection on auth endpoints (rate limiting, lockout)

---

## API3:2023 - Broken Object Property Level Authorization (BOPLA)

API returns or accepts more object properties than the caller is allowed to see or set (mass assignment / over-exposure).

- [ ] Response serialization uses explicit allowlists — no `SELECT *` or full ORM object serialization
- [ ] Input deserialization uses allowlists — no mass assignment of arbitrary client-supplied fields
- [ ] Sensitive fields (e.g., `role`, `isAdmin`, `balance`) excluded from user-writeable input schemas
- [ ] API versioning does not inadvertently re-expose deprecated sensitive fields

---

## API4:2023 - Unrestricted Resource Consumption

No limits on API usage, allowing DoS, cost exhaustion, or enumeration attacks.

- [ ] Rate limiting applied per user/IP/tenant on all endpoints
- [ ] Pagination enforced — no unbounded list queries
- [ ] File upload size limits enforced
- [ ] Expensive operations (search, export, report) have stricter limits or async processing
- [ ] Cost-generating third-party calls (email, SMS, LLM) are rate-limited separately

---

## API5:2023 - Broken Function Level Authorization (BFLA)

Admin or privileged functions accessible to regular users due to missing role checks.

- [ ] Role/permission checks applied to every endpoint, not just data-returning ones
- [ ] Admin endpoints separated and protected beyond regular authentication
- [ ] HTTP method restrictions enforced (e.g., `GET` cannot trigger state changes)
- [ ] Undocumented/deprecated endpoints removed or protected

---

## API6:2023 - Unrestricted Access to Sensitive Business Flows

Business-critical flows (checkout, account creation, voting) can be abused at scale without rate controls.

- [ ] High-value flows have rate limiting and abuse detection
- [ ] Automated abuse mitigations in place (CAPTCHA, device fingerprinting where appropriate)
- [ ] Idempotency keys prevent duplicate submissions on sensitive operations
- [ ] Anomalous usage patterns are alertable (e.g., mass account creation)

---

## API7:2023 - Server Side Request Forgery (SSRF)

API fetches remote resources using user-supplied URLs, enabling access to internal systems.

- [ ] User-supplied URLs are validated against an allowlist of permitted destinations
- [ ] Internal/cloud metadata endpoints (169.254.x.x, 10.x.x.x) blocked
- [ ] URL redirects are not followed blindly when user-supplied
- [ ] DNS rebinding mitigations in place for sensitive fetch operations

---

## API8:2023 - Security Misconfiguration

Insecure defaults, overly permissive settings, or unnecessary features exposed through the API.

- [ ] CORS configured restrictively — no wildcard `*` in production for credentialed requests
- [ ] Unnecessary HTTP methods disabled per endpoint
- [ ] Security headers present (CSP, HSTS, X-Content-Type-Options, etc.)
- [ ] Error responses do not leak stack traces, internal paths, or system details
- [ ] API documentation (Swagger/OpenAPI) not publicly exposed in production
- [ ] Debug or development endpoints removed in production builds

---

## API9:2023 - Improper Inventory Management

Outdated, unmanaged, or shadow API versions expose vulnerabilities.

- [ ] All active API versions documented and inventoried
- [ ] Deprecated API versions have a decommission date and are monitored
- [ ] Old API versions receive the same security patches as current versions
- [ ] Third-party/hosted API endpoints (gateways, managed services) included in inventory

---

## API10:2023 - Unsafe Consumption of APIs

Trusting data from third-party APIs without validation, enabling injection or logic attacks.

- [ ] Third-party API responses validated and sanitized before use
- [ ] Third-party API data is not trusted for authorization decisions without re-validation
- [ ] TLS verified on all outbound API calls (no certificate verification disabled)
- [ ] Timeouts and circuit breakers on outbound API calls
- [ ] Third-party API failures handled gracefully without exposing internal errors

---

## Automated Scanning

- [ ] Run Semgrep with `p/owasp-top-ten` and `p/security-audit` on API handler code
- [ ] Run Semgrep with `p/secrets` to detect hardcoded API keys or tokens
- [ ] Verify OpenAPI/Swagger schema defines auth requirements on all endpoints

---

## Issue Classification

### CRITICAL
- BOLA — accessing another user's resources (data breach)
- BFLA — regular user accessing admin functions
- Authentication bypass
- Mass assignment of privileged fields (e.g., `role`, `isAdmin`)

### HIGH
- No rate limiting on auth or high-value endpoints
- CORS wildcard on credentialed endpoints
- SSRF via user-supplied URLs
- JWT not fully validated

### MEDIUM
- Response over-exposure (extra fields returned)
- Missing pagination limits
- Deprecated API versions still active and unmonitored
- Error messages leaking internal details

### LOW
- API docs exposed in production
- Missing idempotency on sensitive operations
- Third-party API calls missing timeouts
