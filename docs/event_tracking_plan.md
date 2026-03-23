# Event Tracking Plan

| Event Name         | Description                        | Properties                  |
|--------------------|------------------------------------|-----------------------------|
| user_registered    | User completes registration        | user_id, timestamp          |
| user_logged_in     | User logs in                       | user_id, timestamp          |
| user_logged_out    | User logs out                      | user_id, timestamp          |
| job_created        | New job created                    | job_id, contractor_id       |
| job_completed      | Job marked as completed            | job_id, contractor_id       |
| submission_made    | Submission created                 | submission_id, job_id       |
| photo_uploaded     | Photo uploaded                     | photo_id, submission_id     |
| api_error          | API error occurred                 | endpoint, error_code        |

---

## _Last updated: 2026-03-23_
