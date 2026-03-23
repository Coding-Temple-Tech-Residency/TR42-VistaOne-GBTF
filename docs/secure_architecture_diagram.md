# Secure Architecture Diagram

This project should use a layered architecture for security and maintainability. The diagram below describes the recommended structure:

- Client (Web/Mobile)
  - Authenticates via HTTPS
  - Never stores tokens in localStorage
- API Gateway (Flask Backend)
  - Handles authentication, rate limiting, logging
  - Validates all input
- Application Layer
  - Implements business logic
  - Enforces RBAC and permissions
- Data Layer
  - Uses ORM for DB access
  - No raw SQL
  - Secrets loaded from environment variables
- External Services
  - Integrates with third-party APIs securely
  - All secrets managed via environment or secret manager

A visual diagram should be created in Lucidchart, Draw.io, or PowerPoint and saved as an image (e.g., architecture.png) in this folder. For now, this file documents the structure in text form.

---

## _Last updated: 2026-03-23_
