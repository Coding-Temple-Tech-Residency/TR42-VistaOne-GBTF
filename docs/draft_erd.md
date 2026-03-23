# Draft Entity Relationship Diagram (ERD)

This is a draft ERD from an analyst perspective. For a full diagram, use a tool like dbdiagram.io, Lucidchart, or Draw.io and export as an image (add to this folder).

## Main Entities

- User: id, email, password_hash, is_active, created_at
- Contractor: id, user_id, name, company, ...
- Vendor: id, name, ...
- Job: id, contractor_id, vendor_id, status, ...
- Submission: id, job_id, submitted_at, ...
- Photo: id, submission_id, url, ...
- AuditLog: id, user_id, action, timestamp, ...

## Relationships

- User 1---* Contractor
- Contractor 1---* Job
- Vendor 1---* Job
- Job 1---* Submission
- Submission 1---* Photo
- User 1---* AuditLog

---

## _Last updated: 2026-03-23_
