# Threat Model Report

| Threat/Risk                | Description                                                 | Likelihood | Impact | Mitigation                                     |
| -------------------------- | ----------------------------------------------------------- | ---------- | ------ | ---------------------------------------------- |
| Credential Leakage         | Secrets/keys in code or logs                                | Medium     | High   | Use env vars, .env in .gitignore, Bitwarden    |
| Weak Passwords             | Users choose weak passwords                                 | High       | High   | Enforce strong password policy, validation     |
| Brute Force Attacks        | Automated login attempts                                    | Medium     | High   | Rate limiting, account lockout, logging        |
| Token Theft                | Session/JWT tokens stolen via XSS or insecure storage       | Medium     | High   | HttpOnly/Secure cookies, short token TTL       |
| Insecure Biometric Storage | Biometric data stored insecurely                            | Low        | High   | Never store raw biometrics, use secure hashes  |
| SQL Injection              | Unsanitized input in DB queries                             | Low        | High   | Use ORM, parameterized queries                 |
| CSRF                       | Cross-site request forgery on sensitive endpoints           | Low        | High   | CSRF tokens, SameSite cookies                  |
| Privilege Escalation       | Users gain unauthorized access                              | Low        | High   | RBAC, least privilege, code review             |
| Dependency Vulnerabilities | Vulnerable packages in use                                  | Medium     | High   | Dependabot, pip-audit, regular updates         |
| Data Exposure via Logs     | Sensitive data logged                                       | Medium     | Medium | Scrub logs, avoid logging PII/secrets          |
| Insecure API Endpoints     | Unauthenticated/unauthorized API access                     | Medium     | High   | Auth checks, test coverage, code review        |
| Lack of 2FA                | No two-factor authentication for admin or sensitive actions | Medium     | High   | Enforce 2FA for privileged users               |
| Insecure File Uploads      | Malicious files uploaded                                    | Low        | High   | File type/size checks, AV scan, storage limits |

---

## _Last updated: 2026-03-23_
