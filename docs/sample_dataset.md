# Sample Dataset

This sample dataset illustrates the main entities and relationships. For a full dataset, export from the production or staging database (with PII removed).

## users.csv

user_id,email,is_active,created_at
1,<alice@example.com>,1,2026-01-01
2,<bob@example.com>,1,2026-01-02

## jobs.csv

job_id,contractor_id,vendor_id,status
101,1,10,open
102,2,11,completed

## submissions.csv

submission_id,job_id,submitted_at
1001,101,2026-01-10
1002,102,2026-01-11

## photos.csv

photo_id,submission_id,url
2001,1001,<https://example.com/photo1.jpg>
2002,1002,<https://example.com/photo2.jpg>

---

## _Last updated: 2026-03-23_
