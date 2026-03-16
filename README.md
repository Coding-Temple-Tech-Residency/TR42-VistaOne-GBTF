# Field Contractor Mobile App

## 📋 Project Overview

The Field Contractor app solves the critical problem of inefficiency, lack of transparency, and fraud vulnerability in oil and gas field operations. Currently, many small to mid-sized operators rely on manual, paper-based ticketing systems that are:

- **Laborious and error-prone** - Paper tickets get lost, damaged, or illegible
- **Difficult to verify** - No way to confirm work was actually performed at the correct location
- **Vulnerable to fraud** - Phantom employees, inflated hours, and false billing are hard to detect
- **Expensive** - Existing solutions require $8,000+ hardware or expensive enterprise software

Our solution digitizes the entire workflow using standard smartphones, making it affordable and accessible.

## 👥 Target Users

| User Role | Description | Primary Need |
| ----------- | ------------- | -------------- |
| **Field Contractor** | Drivers and field workers performing on-site services | Easy job execution, offline capability, clear instructions |
| **Vendor Manager** | Dispatchers and managers at service companies | Track contractor work, review anomalies, manage billing |
| **Operator Admin** | Oil and gas company representatives | Verify work was performed, audit field operations, approve payments |

## 🏗️ Tech Stack

### Backend

- **Framework**: Flask 2.3.2
- **Database**: PostgreSQL
- **ORM**: Flask-SQLAlchemy
- **Authentication**: JWT (Flask-JWT-Extended)
- **Password Hashing**: Flask-Bcrypt
- **State Management**: Context API
- **Offline Storage**: WatermelonDB
- **Maps**: React Native Maps
- **Charts**: Recharts
- **Tables**: MUI X Data Grid
- **HTTP Client**: Axios
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+

## Clone repository

### Backend Setup

#### Clone repository 2

git clone [https://github.com/your-org/field-contractor-backend.git](https://github.com/your-org/field-contractor-backend.git)
cd field-contractor-backend

#### Create virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

#### Install dependencies

pip install -r requirements.txt

cp .env.example .env

Edit the .env file with your credentials

cp .env.example .env
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

#### Seed test data

python seed.py

#### Run server

python app.py

### Frontend (Mobile) Installation

```bash
# Clone repository
git clone https://github.com/your-org/field-contractor-mobile.git
cd field-contractor-mobile
# Install dependencies
npm install

# Set up environment variables```

cp .env.example .env

# iOS

cd ios && pod install && cd ..
npm run ios

# Android

npm run android
Frontend (Web Dashboard) Installation
bash

# Clone repository

git clone https://github.com/your-org/field-contractor-web.git
cd field-contractor-web

# Install dependencies

## Frontend (Mobile) Installation
### Frontend (Mobile) Installation

npm install

# Set up environment variables

cp .env.example .env

## Run development server

npm start
🔧 Environment Variables
Backend (.env)
env
'''

## Flask

FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

## Database

DATABASE_URL=postgresql://username:password@localhost:5432/field_contractor_db

## AWS

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

## Redis (for Celery)

REDIS_URL=redis://localhost:6379/0
Mobile (.env)
env
API_URL=[http://localhost:5000/api](http://localhost:5000/api)
MAPS_API_KEY=your-google-maps-key

📚 API Documentation
# 📚 API Documentation

## Table of Contents
- [Authentication Endpoints](#authentication-endpoints)
- [Job Management Endpoints](#job-management-endpoints)
- [Anomaly Management Endpoints](#anomaly-management-endpoints)
- [🧪 Testing](#🧪-testing)
  - [Backend Tests](#backend-tests)
  - [Frontend Tests (Web)](#frontend-tests-web)
- [📱 Postman Collection](#📱-postman-collection)
- [🔑 Test Credentials](#🔑-test-credentials)
- [📊 Sprint Timeline](#📊-sprint-timeline)
- [🤝 Contributing](#🤝-contributing)
  - [Development Standards](#development-standards)
  - [Git Workflow](#git-workflow)
- [📝 Known Limitations](#📝-known-limitations)
- [🔒 Intellectual Property Notice](#🔒-intellectual-property-notice)
- [📄 License](#📄-license)
- [👨‍💻 Team](#👨‍💻-team)
- [📞 Contact](#📞-contact)

## Authentication Endpoints

| Method | Endpoint                     | Description                      |
|--------|------------------------------|----------------------------------|
| POST   | `/api/auth/register`         | Register new user                |
| POST   | `/api/auth/login`            | Login and get tokens             |
| POST   | `/api/auth/refresh`          | Refresh access token             |
| GET    | `/api/auth/me`               | Get current user                 |
| POST   | `/api/auth/logout`           | Logout                           |
| GET    | `/api/auth/companies`        | Get companies                    |
| GET    | `/api/health`                | Health check                     |

## Job Management Endpoints

| Method | Endpoint                     | Description                      |
|--------|------------------------------|----------------------------------|
| GET    | `/api/jobs/assigned`         | Get assigned jobs                |
| GET    | `/api/jobs/:id`              | Get job details                  |
| POST   | `/api/jobs/:id/start`        | Start job                        |
| POST   | `/api/jobs/:id/complete`     | Complete job                     |
| POST   | `/api/jobs/:submission_id/photos` | Upload photos               |
| POST   | `/api/jobs/offline/submit`   | Submit offline job               |
| GET    | `/api/jobs/history`          | Get job history                  |

## Anomaly Management Endpoints

| Method | Endpoint                     | Description                      |
|--------|------------------------------|----------------------------------|
| GET    | `/api/anomalies`             | List anomalies                   |
| GET    | `/api/anomalies/stats`       | Get anomaly statistics           |
| GET    | `/api/anomalies/:id`         | Get anomaly details              |
| POST   | `/api/anomalies/:id/review`  | Review anomaly                   |

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
python -m unittest tests/test_auth.py

# Load testing
locust -f locustfile.py

# Run unit tests
# Run e2e tests (Detox)
npm run e2e:ios
```

### Frontend Tests (Web)

```bash
npm test
```

## 📱 Postman Collection

Import the `Field_Contractor_Auth.postman_collection.json` file into Postman to test all endpoints.

**refresh_token:** (auto-populated after login)

### Register Contractor

```json
POST {{base_url}}/api/auth/register
{
    "username": "test_contractor",
    "email": "contractor@test.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "Contractor",
    "role": "field_contractor",
    "company_id": 2
}
```

### Login

```json
POST {{base_url}}/api/auth/login
{
    "username": "john_doe",
    "password": "password123"
}
```

## 🔑 Test Credentials

After running `seed.py`:

### Contractors

- john_doe / password123
- jane_smith / password123
- bob_wilson / password123

### Vendor Manager

- vendor_manager / password123

### Operator Admin

- operator_admin / password123

## 📊 Sprint Timeline

| Sprint | Backend Focus                  | Frontend Focus                    |
| ------ | ------------------------------ | --------------------------------- |
| 1      | Foundation & Database          | Mobile App Foundation             |
| 2      | Core Business Models           | Mobile Job List & Details         |
| 3      | Job Management API             | Mobile Job Execution              |
| 4      | Anomaly Detection Engine       | Mobile Offline Storage            |
| 5      | Anomaly Management             |Mobile History & Profile Management|
| 6      | Dashboard APIs                 | Contractor Web Dashboard          |
| 7      | Notification System            | Operator/Vendor Dashboard         |
| 8      | Security & Deployment          | Testing & Polish                  |

## 🤝 Contributing

### Development Standards

- Write clean, readable, and modular code.
- Use clear naming conventions.
- Remove unused files, variables, and console logs.
- Follow consistent formatting and linting practices.
- Write meaningful commit messages.
- Keep branches organized and avoid pushing broken code to main.
- Review teammate pull requests respectfully and constructively.

### Git Workflow

1. Create feature branch from main.
2. Implement changes with clear commits.
3. Push branch and create PR.
4. Request review from team members.
5. Address feedback and merge.

## 📝 Known Limitations

- **Sprint 1:** Only authentication and basic user management completed.
- **Offline Sync:** Full implementation scheduled for Sprint 4.
- **Push Notifications:** Scheduled for Sprint 7.
- **Real-time Updates:** WebSocket implementation optional for Sprint 7.

## 🔒 Intellectual Property Notice

This project was created as part of a Coding Temple Tech Residency. All work produced during the residency is considered the intellectual property of Coding Temple or the sponsoring employer, unless otherwise stated in a signed agreement. By contributing to this project, you acknowledge and agree to these terms.

## 📄 License

Copyright © 2026 Coding Temple. All rights reserved.

## 👨‍💻 Team

| Name                          | Role                       |
|-------------------------------|----------------------------|
| Justin Wold                   | Full Stack Backend Head    |
| Aldo Emmanuel Pena Herrera    | Full Stack Backend         |
| Charlie Estrada               | Full Stack Frontend Head   |
| Hector Gomez                  | Cybersecurity              |

## 📞 Contact

For questions or support, please contact the team through GitHub Issues or reach out to your team lead.
