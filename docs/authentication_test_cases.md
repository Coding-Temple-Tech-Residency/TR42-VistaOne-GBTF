# Authentication Test Cases

| Test Case                                 | Description                                 | Automated | Manual |
|-------------------------------------------|---------------------------------------------|-----------|--------|
| Register with valid credentials           | User can register with valid data           | Yes       | Yes    |
| Register with weak password               | Registration fails for weak password        | Yes       | Yes    |
| Register with duplicate email             | Registration fails for duplicate email      | Yes       | Yes    |
| Login with valid credentials              | User can log in with correct password       | Yes       | Yes    |
| Login with invalid credentials            | Login fails for wrong password/email        | Yes       | Yes    |
| Login with inactive account               | Login fails for inactive user               | Yes       | Yes    |
| Logout                                    | User session is terminated                  | Yes       | Yes    |
| 2FA required for admin                    | Admin login requires 2FA                    | Planned   | Yes    |
| Token invalidation on logout              | Token is invalid after logout               | Yes       | Yes    |
| Brute force protection                    | Rate limiting enforced                      | Yes       | Yes    |

---

## _Last updated: 2026-03-23_
