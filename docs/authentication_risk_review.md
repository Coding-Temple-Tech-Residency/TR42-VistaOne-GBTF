# Authentication Risk Review

## Token Storage

- Use HttpOnly, Secure cookies for session/JWT tokens.
- Never store tokens in localStorage or expose via frontend JS.
- Short token TTL, refresh tokens securely.

## Password Rules

- Enforce strong password policy (min length, complexity).
- Hash passwords with bcrypt or Argon2.
- Never log or email plaintext passwords.

## 2FA

- Require 2FA for admin and privileged users.
- Support TOTP (e.g., Google Authenticator) or SMS as fallback.

## Risks

- Token theft via XSS: Mitigated by HttpOnly cookies.
- Weak passwords: Mitigated by strong policy and hashing.
- 2FA bypass: Mitigated by secure 2FA implementation and monitoring.

---

## _Last updated: 2026-03-23_
