# Security Checklist — Mobile Applications

Concise checklist for security code reviews of native and hybrid mobile applications. Based on [OWASP Mobile Top 10:2024](https://owasp.org/www-project-mobile-top-10/).

**Applies to:** Native iOS (Swift/ObjC), native Android (Kotlin/Java), and cross-platform mobile apps (React Native, Flutter, Expo). Complements the Web and API checklists — also apply those when the app communicates with a backend API.

---

## Pre-Review
- [ ] Identify sensitive data handled by the app (credentials, PII, tokens, health/financial data)
- [ ] Identify all data persistence locations (keychain, shared prefs, SQLite, files, cache)
- [ ] Identify all network communication endpoints and authentication mechanisms

---

## M1:2024 - Improper Credential Usage

Hardcoded credentials or insecure credential storage in the app binary or configuration.

- [ ] No hardcoded credentials, API keys, or secrets in source code or config files
- [ ] API keys and secrets stored server-side where possible; not bundled in the app
- [ ] Credentials stored in secure system storage (iOS Keychain, Android Keystore) — not SharedPreferences, UserDefaults, or plain files
- [ ] Secrets excluded from source control (`.gitignore` covers `.env`, key files, etc.)
- [ ] Compiled binary does not contain plaintext secrets (check build outputs)

---

## M2:2024 - Inadequate Supply Chain Security

Vulnerabilities introduced through third-party SDKs, libraries, or build tooling.

- [ ] All third-party SDKs and dependencies inventoried and sourced from trusted registries
- [ ] Dependencies pinned to specific versions with integrity verification
- [ ] Automated vulnerability scanning in CI/CD (e.g., `npm audit`, `pod-audit`, Dependabot)
- [ ] Third-party SDKs reviewed for excessive permissions or data collection
- [ ] Ad/analytics SDKs audited for data exfiltration risks

---

## M3:2024 - Insecure Authentication and Authorization

Weak or bypassable authentication allowing unauthorized access to app functionality or data.

- [ ] Biometric authentication uses platform APIs correctly (iOS LocalAuthentication, Android BiometricPrompt)
- [ ] Authentication state is not stored in tamperable locations (plain files, unprotected prefs)
- [ ] Session tokens stored in secure storage (Keychain/Keystore), not in plain SharedPreferences or NSUserDefaults
- [ ] Authorization checks enforced server-side — client-side checks are UX only
- [ ] Re-authentication required for sensitive operations (payments, account changes)
- [ ] Logout clears all session tokens from secure storage

---

## M4:2024 - Insufficient Input/Output Validation

Unvalidated input or output enabling injection attacks or unexpected behavior in the app.

- [ ] All user input validated (type, length, format) before use or transmission
- [ ] Deep link / URL scheme parameters treated as untrusted and validated
- [ ] WebView content validated — JavaScript interfaces are not exposed unnecessarily
- [ ] Data received from the backend validated before rendering (XSS in WebViews, display logic)
- [ ] Intent extras (Android) and URL scheme parameters (iOS) validated before use

---

## M5:2024 - Insecure Communication

Sensitive data transmitted without proper TLS configuration or with certificate validation disabled.

- [ ] TLS enforced for all network communication — no HTTP fallback
- [ ] Certificate validation is not disabled (no `trustAllCerts`, `allowAllHostnames`, `NSAllowsArbitraryLoads`)
- [ ] Certificate pinning implemented for high-risk communications (banking, health)
- [ ] iOS ATS (App Transport Security) enabled and not broadly exempted
- [ ] Android Network Security Config does not define broad `<trust-anchors>` overrides
- [ ] Sensitive data not transmitted via query strings (visible in logs and proxies)

---

## M6:2024 - Inadequate Privacy Controls

App collects, stores, or transmits more user data than necessary, or without adequate user consent.

- [ ] App requests only permissions actually required (camera, location, contacts, etc.)
- [ ] Runtime permissions requested at the point of need with clear rationale
- [ ] Precise location not used where coarse location suffices
- [ ] Privacy policy accurately reflects data collected and shared with third parties
- [ ] Analytics/crash reporting SDKs configured to minimize PII collection
- [ ] Data deleted on account deletion or app uninstall where applicable

---

## M7:2024 - Insufficient Binary Protections

App binary can be reverse engineered, tampered with, or repackaged to bypass security controls.

- [ ] Code obfuscation applied to sensitive business logic (ProGuard/R8 on Android, symbol stripping on iOS)
- [ ] Sensitive algorithms or cryptographic operations not implemented solely client-side
- [ ] Jailbreak/root detection considered for high-security apps (banking, healthcare)
- [ ] Anti-tampering / integrity checks in place if app is a high-value target
- [ ] Debug builds not distributed to production (build type verification in CI)
- [ ] App not debuggable in release builds (`android:debuggable=false`, no Xcode debug entitlements)

---

## M8:2024 - Security Misconfiguration

Insecure platform or framework configuration leaving the app exposed.

- [ ] Android `backup` disabled for sensitive apps (`android:allowBackup=false`) or backup rules applied
- [ ] iOS data protection entitlement set appropriately for sensitive files
- [ ] Exported components (Activities, Services, Providers) restricted with permissions where not intended for external use
- [ ] WebViews have JavaScript disabled unless required; `setAllowFileAccess(false)` on Android
- [ ] Content providers restricted — no unintentional data exposure via content URIs
- [ ] Clipboard access restricted for sensitive input fields (passwords, card numbers)

---

## M9:2024 - Insecure Data Storage

Sensitive data persisted in insecure locations accessible to other apps, backups, or physical access.

- [ ] Sensitive data stored only in Keychain (iOS) or Keystore-backed storage (Android)
- [ ] No sensitive data in plain SharedPreferences, NSUserDefaults, or unprotected SQLite
- [ ] No sensitive data written to external storage (SD card)
- [ ] Log statements do not output sensitive data (tokens, PII, credentials)
- [ ] Screenshots of sensitive screens disabled (iOS `isHidden`, Android `FLAG_SECURE`)
- [ ] Temporary files containing sensitive data cleaned up after use

---

## M10:2024 - Insufficient Cryptography

Weak, broken, or incorrectly implemented cryptography protecting sensitive data.

- [ ] Strong algorithms only — no MD5, SHA-1, DES, 3DES, RC4, ECB mode
- [ ] AES-256-GCM or AES-256-CBC with HMAC used for symmetric encryption
- [ ] Cryptographic keys managed via platform APIs (iOS Keychain, Android Keystore) — not derived from static strings
- [ ] IVs and nonces are random and never reused with the same key
- [ ] Random values for security-sensitive use generated via `SecureRandom` / `SecRandomCopyBytes`
- [ ] No custom or home-grown cryptographic implementations

---

## Automated Scanning

- [ ] Run Semgrep with `p/mobile` or platform-specific configs (`p/kotlin`, `p/swift`) on changed files
- [ ] Run Semgrep with `p/secrets` to detect hardcoded credentials in source
- [ ] Check Android Lint for security warnings (`StrictMode`, `AllowBackup`, exported components)

---

## Issue Classification

### 🚨 CRITICAL (Immediate Fix Required)
- Hardcoded credentials or API keys in binary
- TLS certificate validation disabled
- Authentication state stored in tamperable, unprotected storage
- Sensitive PII stored in plain SharedPreferences or NSUserDefaults
- Broken cryptography (weak keys, static IVs, ECB mode)

### ⚠️ HIGH (Fix Before Release)
- Jailbreak/root detection absent in high-security apps
- Debug build distributed to production
- Sensitive data in logs
- `android:allowBackup=true` on apps with sensitive data
- Deep link / URL scheme parameters not validated

### 🔶 MEDIUM (Fix Soon)
- Excessive permissions requested
- Analytics SDKs collecting unnecessary PII
- Missing `FLAG_SECURE` on sensitive screens
- Certificate pinning absent for high-risk communications

### 💡 LOW (Track & Plan)
- Obfuscation not applied to sensitive logic
- Coarse location used where precise is requested
- Clipboard not restricted on password fields
