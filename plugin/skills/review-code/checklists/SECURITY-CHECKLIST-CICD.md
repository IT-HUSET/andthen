# Security Checklist — CI/CD Pipeline Security

Concise checklist for security reviews of CI/CD pipelines, build systems, and software delivery infrastructure. Based on [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/).

**Applies to:** Any codebase with CI/CD pipeline configuration (GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.), IaC files, deployment scripts, or containerized build processes. Use when reviewing pipeline config files, Dockerfiles, deployment workflows, or supply chain changes.

---

## Pre-Review
- [ ] Identify all pipeline configuration files (.github/workflows/, .gitlab-ci.yml, Jenkinsfile, etc.)
- [ ] Map secrets and credentials used in pipelines and where they are stored
- [ ] Identify all third-party actions, orbs, or plugins used in pipelines

---

## CICD-SEC-1 - Insufficient Flow Control Mechanisms

No gates or approvals on pipeline flows, allowing any code change to trigger deployment.

- [ ] Protected branches require PR reviews before merge
- [ ] Deployment to production requires manual approval or environment protection rules
- [ ] Force pushes disabled on main/release branches
- [ ] Branch protection rules enforced — direct commits to protected branches blocked
- [ ] PR merge requires passing CI checks

---

## CICD-SEC-2 - Inadequate Identity and Access Management

Overly permissive pipeline identities or shared credentials without scoping.

- [ ] Pipeline identities (service accounts, OIDC tokens) follow least privilege
- [ ] Separate identities for different pipeline stages (build vs. deploy vs. test)
- [ ] OIDC used instead of long-lived credentials where supported (GitHub Actions OIDC, etc.)
- [ ] Access to production deployment scoped and auditable
- [ ] Human access to pipeline systems requires MFA

---

## CICD-SEC-3 - Dependency Chain Abuse

Malicious or compromised packages introduced through package registries or dependency resolution.

- [ ] Dependencies pinned to exact versions (not ranges) in lock files
- [ ] Lock files committed and verified in CI
- [ ] Package integrity verified (checksums, signatures) during install
- [ ] Private package namespaces used to prevent dependency confusion attacks
- [ ] Automated vulnerability scanning on dependencies in CI (Dependabot, Snyk, `npm audit`)

---

## CICD-SEC-4 - Poisoned Pipeline Execution (PPE)

Attacker modifies pipeline execution by injecting malicious code into pipeline config or triggering pipelines on unreviewed code.

- [ ] Pipeline workflows triggered by external PRs run with minimal permissions (read-only token)
- [ ] Secrets not exposed to untrusted pipeline runs (fork PRs, external contributors)
- [ ] `pull_request_target` (GitHub Actions) used with caution — does not checkout untrusted code with write permissions
- [ ] Pipeline configuration files reviewed as security-critical code
- [ ] No `${{ github.event.*.body }}` or similar user-controlled values interpolated directly into `run:` steps (script injection)

---

## CICD-SEC-5 - Insufficient Pipeline-Based Access Controls (PBAC)

Pipeline jobs have access to more resources, secrets, or environments than needed for their specific task.

- [ ] Secrets scoped to the minimum set of pipeline jobs that require them
- [ ] Environment-specific secrets (prod credentials) only accessible to deployment jobs, not test/build jobs
- [ ] Pipeline jobs run with minimal OS/container permissions
- [ ] No shared secret stores across unrelated pipelines without justification

---

## CICD-SEC-6 - Insufficient Credential Hygiene

Secrets and credentials leaked, hardcoded, or improperly managed in pipeline configuration or logs.

- [ ] No secrets hardcoded in pipeline config files
- [ ] Secrets passed via environment variables from a secrets manager, not inline values
- [ ] Pipeline logs do not print secret values (use masking; avoid `echo $SECRET`)
- [ ] Secrets rotated regularly and revocable
- [ ] Unused or stale credentials revoked
- [ ] `.env` files and key files excluded from version control

---

## CICD-SEC-7 - Insecure System Configuration

Misconfigured pipeline infrastructure, runners, or build environments.

- [ ] Self-hosted runners isolated — not shared across projects with different trust levels
- [ ] Runners are ephemeral or cleaned between jobs (no state leakage)
- [ ] Runner OS and tooling kept up to date and hardened
- [ ] Container images used in pipelines sourced from trusted registries and pinned by digest
- [ ] Build environments do not have access to production systems beyond what's needed for deployment

---

## CICD-SEC-8 - Ungoverned Usage of Third-Party Services

Third-party CI/CD services or actions used without vetting, versioning, or oversight.

- [ ] Third-party GitHub Actions / orbs pinned to a specific commit SHA (not a mutable tag like `@v1`)
- [ ] Third-party actions reviewed before adoption — check permissions requested and code
- [ ] Minimal set of third-party integrations — unused integrations removed
- [ ] Third-party services given least-privilege access (scoped tokens, not org-wide)
- [ ] Changelog for third-party actions monitored when updating

---

## CICD-SEC-9 - Improper Artifact Integrity Validation

Build artifacts are not signed or verified, allowing tampered artifacts to be deployed.

- [ ] Build artifacts signed and signatures verified before deployment
- [ ] Container images signed (e.g., Cosign / Sigstore) and verified at deploy time
- [ ] Artifacts stored in a trusted, access-controlled artifact registry
- [ ] SBOMs generated for deployable artifacts
- [ ] Artifact checksums verified when downloading during pipelines

---

## CICD-SEC-10 - Insufficient Logging and Visibility

Pipeline activity not logged or monitored, making attacks or misuse undetectable.

- [ ] All pipeline runs, approvals, and deployments logged with actor identity
- [ ] Audit logs for secrets access and pipeline config changes retained
- [ ] Alerts configured for failed deployments, unusual pipeline triggers, and permission changes
- [ ] Pipeline logs retained for sufficient duration per compliance requirements
- [ ] Anomalous pipeline behavior (unexpected external network calls, unusual resource usage) is detectable

---

## Automated Scanning

- [ ] Run Semgrep with `p/secrets` on pipeline config files to detect hardcoded credentials
- [ ] Run `actionlint` on GitHub Actions workflows for security and correctness issues
- [ ] Check third-party actions are pinned to commit SHAs (not mutable tags)
- [ ] Verify lock files are present and committed for all package managers in use

---

## Issue Classification

### CRITICAL
- Secrets hardcoded in pipeline config or logged in plaintext
- PPE — untrusted PR code can access production secrets
- Production deployment has no approval gate
- Third-party actions pinned to mutable tags (supply chain risk)

### HIGH
- Pipeline identity has overly broad permissions (e.g., org-level write)
- Secrets accessible to build/test jobs that don't need them
- Self-hosted runners shared across untrusted projects
- No artifact signing or integrity verification

### MEDIUM
- Dependencies not pinned in lock files
- Stale or unused credentials not revoked
- Missing pipeline run audit logs
- Container images not pinned by digest

### LOW
- Third-party actions not reviewed at adoption
- SBOMs not generated for artifacts
- Log retention below compliance recommendations
