# Cognevance Online Job Portal System

## Overview
A full-stack job portal with applicant/employer roles, job listings, applications, search/filtering, profiles and REST API access.

## Features
- Applicant and employer registration
- Role-based access control
- Password hashing
- Employer job posting
- Applicant job application
- Application status management
- Search and filtering
- Profile management
- REST API: `/api/jobs`
- SQLite development database; PostgreSQL/MySQL can be configured through `DATABASE_URL`

## Run
```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## Repository
`cognevance_onlineJobPortal`

## API
`GET /api/jobs` returns job records as JSON.

## Deployment
Use Render, Railway or PythonAnywhere. Configure `SECRET_KEY` and a production `DATABASE_URL`.

## Screenshots
Capture Home/Search, Registration, Login, Employer Dashboard, Job Posting, Applicant Dashboard, Application Status and Profile screens.

## TODO
Add the deployed URL and final GitHub URL after publishing.

