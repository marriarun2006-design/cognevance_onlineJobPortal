# REST API Documentation

## GET /api/jobs
Returns all jobs.

### Response
```json
[
  {
    "id": 1,
    "title": "Python Developer",
    "company": "Example Ltd",
    "location": "Hyderabad",
    "skills": "Python, Flask, SQL"
  }
]
```

## Database
Tables:
- `user`: account, role and profile data
- `job`: job postings
- `application`: applicant/job relationship and status

