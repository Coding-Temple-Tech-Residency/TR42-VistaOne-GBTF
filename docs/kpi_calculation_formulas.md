# KPI Calculation Formulas (Excel)

| KPI Name           | Excel Formula Example                                               |
|--------------------|---------------------------------------------------------------------|
| User Registrations | =COUNT(users!A2:A1000)                                              |
| Active Users       | =COUNTIF(users!C2:C1000, 1)                                         |
| Jobs Created       | =COUNT(jobs!A2:A1000)                                               |
| Jobs Completed     | =COUNTIF(jobs!D2:D1000, "completed")                                |
| Submission Rate    | =COUNTA(submissions!A2:A1000)/COUNT(jobs!A2:A1000)                  |
| Photo Upload Rate  | =COUNTA(photos!A2:A1000)/COUNTA(submissions!A2:A1000)               |
| API Error Rate     | =COUNTIF(api_logs!C2:C1000, "error")/COUNTA(api_logs!A2:A1000)*1000 |

---

## _Last updated: 2026-03-23_
