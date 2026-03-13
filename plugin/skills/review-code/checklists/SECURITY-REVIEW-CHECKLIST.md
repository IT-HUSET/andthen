# Security Review Checklist

Concise checklist for security code reviews, based on [OWASP Top 10:2025](https://owasp.org/Top10/2025/).

---

## Pre-Review
- [ ] Identify trust boundaries, attack surface, and sensitive data flows
- [ ] Review threat model and security requirements
- [ ] Check compliance needs (GDPR, HIPAA, PCI-DSS, etc.)

---

## A01:2025 - Broken Access Control

Access control failures lead to unauthorized data access, modification, or privilege escalation.

- [ ] Server-side access control enforced (not client-side only)
- [ ] Default deny - explicit allow required for each resource
- [ ] IDOR prevented - object references validated against user context
- [ ] Horizontal/vertical privilege escalation prevented
- [ ] CORS configured restrictively (no wildcard in production)
- [ ] CSRF protection on state-changing operations
- [ ] SSRF prevented - URL destinations validated, internal network blocked
- [ ] Rate limiting on sensitive endpoints

---

## A02:2025 - Security Misconfiguration

Every tested app had some misconfiguration. As software becomes more configurable, risk grows.

- [ ] Hardened default configurations applied
- [ ] Unnecessary features, ports, services disabled
- [ ] Security headers configured (CSP, HSTS, X-Content-Type-Options, etc.)
- [ ] Error pages don't leak stack traces or internal details
- [ ] Directory listing disabled, .git and backup files not exposed
- [ ] Debug endpoints disabled in production
- [ ] Cloud/infrastructure permissions follow least privilege

---

## A03:2025 - Software Supply Chain Failures

Breakdowns in building, distributing, or updating software through vulnerable/malicious dependencies.

- [ ] SBOM (Software Bill of Materials) maintained
- [ ] Transitive dependencies tracked and scanned
- [ ] Automated vulnerability scanning in CI/CD
- [ ] Dependencies from trusted sources, integrity verified (checksums/signatures)
- [ ] CI/CD pipeline hardened (separation of duties, access control, signed builds)
- [ ] Unused dependencies removed
- [ ] Patch management process in place

---

## A04:2025 - Cryptographic Failures

Weak or missing cryptography leading to sensitive data exposure.

- [ ] Sensitive data classified and minimized
- [ ] TLS 1.2+ enforced for all connections
- [ ] Strong algorithms only (no MD5, SHA-1, DES, RC4)
- [ ] Passwords hashed with Argon2id, bcrypt, or scrypt
- [ ] Encryption keys properly managed (not in code, rotation supported)
- [ ] No sensitive data in URLs, logs, or error messages

---

## A05:2025 - Injection

Untrusted data sent to interpreters as part of commands or queries.

- [ ] Parameterized queries / prepared statements used
- [ ] Input validated with allowlists, type/bounds checking
- [ ] Output encoding context-appropriate (HTML, JS, URL, CSS)
- [ ] ORM/safe APIs preferred over raw queries
- [ ] Command execution avoided; if needed, arguments as arrays
- [ ] CSP configured to mitigate XSS impact

---

## A06:2025 - Insecure Design

Missing or ineffective security controls at the design level.

- [ ] Threat modeling performed
- [ ] Secure design patterns applied
- [ ] Business logic tested for abuse scenarios
- [ ] Resource limits prevent DoS
- [ ] Tenant segregation verified (multi-tenant systems)

---

## A07:2025 - Authentication Failures

Failures in confirming user identity.

- [ ] No default or weak credentials
- [ ] Brute force protection (lockout, rate limiting)
- [ ] No username enumeration (generic error messages)
- [ ] Session invalidated on logout/password change
- [ ] Session cookies: HttpOnly, Secure, SameSite
- [ ] MFA available for sensitive operations

---

## A08:2025 - Software or Data Integrity Failures

Assumptions about software updates, data, or CI/CD integrity without verification.

- [ ] CI/CD pipeline secured (access control, audit logging)
- [ ] Code review required for critical changes
- [ ] Unsigned code/updates rejected
- [ ] Deserialization of untrusted data avoided or strictly validated
- [ ] Dependency integrity verified before use

---

## A09:2025 - Security Logging and Alerting Failures

Insufficient logging, monitoring, or alerting to detect attacks.

- [ ] Auth events logged (login, logout, failures)
- [ ] Access control failures logged
- [ ] No sensitive data in logs (passwords, tokens, PII)
- [ ] Log injection prevented
- [ ] Alerting configured for suspicious patterns
- [ ] Incident response plan exists

---

## A10:2025 - Mishandling of Exceptional Conditions

Failing to properly handle errors and edge cases, leading to crashes or vulnerabilities.

- [ ] Fail securely / fail closed (deny access on error)
- [ ] Transactions rolled back completely on failure
- [ ] Resource exhaustion prevented (limits, quotas, timeouts)
- [ ] Race conditions addressed in critical operations
- [ ] Global exception handler in place
- [ ] Errors logged server-side, generic messages to users

---

## Issue Classification

### 🚨 CRITICAL (Immediate Fix Required)
- Remote code execution (RCE)
- SQL injection
- Authentication bypass
- Authorization bypass (privilege escalation)
- Sensitive data exposure (credentials, PII)
- Cryptographic failures (weak/broken crypto)

### ⚠️ HIGH (Fix Before Release)
- Stored XSS
- CSRF on sensitive operations
- Insecure direct object references
- Session fixation
- Missing security headers
- Vulnerable dependencies with known exploits

### 🔶 MEDIUM (Fix Soon)
- Reflected XSS
- Information disclosure
- Missing rate limiting
- Weak password policies
- Verbose error messages
- Minor misconfigurations

### 💡 LOW (Track & Plan)
- Best practice deviations
- Defense-in-depth improvements
- Security hardening opportunities
- Documentation gaps
