# TR Project Template

## Project Information

**Project Name:**  
**Team Name:**  
**Team Members:**  

- Justin Wold - Full stack (Backend Head)
- Aldo Emmanuel Pena Herrera- Full stack
- Charlie Estrada - Full stack (Frontend Head)
- Hector Gomez - Cybersecurity

**Tech Stack:**

## Project Overview

## Field Contractor Mobile App - Project Overview

What Problem Does It Solve?
The Field Contractor app solves the critical problem of inefficiency, lack of transparency, and fraud vulnerability in oil and gas field operations. Currently, many small to mid-sized operators rely on manual, paper-based ticketing systems that are:

Laborious and error-prone - Paper tickets get lost, damaged, or illegible

Difficult to verify - No way to confirm work was actually performed at the correct location

Vulnerable to fraud - Phantom employees, inflated hours, and false billing are hard to detect

Expensive - Existing solutions require $8,000+ hardware or expensive enterprise software

Our solution digitizes the entire workflow using standard smartphones, making it affordable and accessible.

Who Is the Target User?
The platform serves three distinct user types:

## User Role

Description Primary Need
-Field Contractor: Drivers and field workers performing on-site services Easy job execution, offline capability, clear instructions
-Vendor Manager Dispatchers and managers: at service companies Track contractor work, review anomalies, manage billing
-Operator Admin Oil and gas company representatives: Verify work was performed, audit field operations, approve payments

## Setup & Documentation

This is the backend API for the Field Contractor mobile app, focusing on user authentication and company management.

## Features

- User registration with role-based access
- JWT authentication (access + refresh tokens)
- Company management (operator/vendor types)
- Password hashing with bcrypt
- Test data seeding

## Technology Stack

- Flask 2.3.2
- PostgreSQL
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-Migrate

## Installation

```bash
# Clone repository
git clone backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed test data
python seed.py

# Run server
python app.py
```

## Migration setup

'''txt
Database migrations will be stored here when initialized with Flask-Migrate.
(remember to make a DB for this in postgresql)

To initialize migrations:
flask db init

To create a migration:
flask db migrate -m "Initial migration"

To apply migrations:
flask db upgrade
'''

## Required environment variables

- Flask

FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

- Database

DATABASE_URL=postgresql://username:password@localhost:5432/field_contractor_db

- AWS

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=

## Notes

List any known limitations, incomplete features, or important technical considerations.

## Development Standards Reminder

All submissions should reflect professional engineering standards:

- Write clean, readable, and modular code  
- Use clear naming conventions  
- Remove unused files, variables, and console logs  
- Follow consistent formatting and linting practices  
- Write meaningful commit messages  
- Keep branches organized and avoid pushing broken code to main  
- Review teammate pull requests respectfully and constructively  

Your repository should be organized, understandable, and demo-ready.

## POSTMAN

'''postman
{
  "info": {
    "name": "Field Contractor API - Sprint 1",
    "schema": "<https://schema.getpostman.com/json/collection/v2.1.0/collection.json>"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/api/health",
          "host": ["{{base_url}}"],
          "path": ["api", "health"]
        }
      }
    },
    {
      "name": "Register Contractor",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"username\": \"test_contractor\",\n    \"email\": \"contractor@test.com\",\n    \"password\": \"password123\",\n    \"first_name\": \"Test\",\n    \"last_name\": \"Contractor\",\n    \"role\": \"field_contractor\",\n    \"company_id\": 2\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/auth/register",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "register"]
        }
      }
    },
    {
      "name": "Register Vendor Manager",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"username\": \"test_vendor\",\n    \"email\": \"vendor@test.com\",\n    \"password\": \"password123\",\n    \"first_name\": \"Test\",\n    \"last_name\": \"Vendor\",\n    \"role\": \"vendor_manager\",\n    \"company_id\": 2\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/auth/register",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "register"]
        }
      }
    },
    {
      "name": "Register Operator Admin",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"username\": \"test_operator\",\n    \"email\": \"operator@test.com\",\n    \"password\": \"password123\",\n    \"first_name\": \"Test\",\n    \"last_name\": \"Operator\",\n    \"role\": \"operator_admin\",\n    \"company_id\": 1\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/auth/register",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "register"]
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"username\": \"john_doe\",\n    \"password\": \"password123\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/auth/login",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "login"]
        }
      },
      "response": []
    },
    {
      "name": "Get Current User",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/auth/me",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "me"]
        }
      }
    },
    {
      "name": "Refresh Token",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{refresh_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/auth/refresh",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "refresh"]
        }
      }
    },
    {
      "name": "Logout",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/auth/logout",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "logout"]
        }
      }
    },
    {
      "name": "Get Companies",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/auth/companies",
          "host": ["{{base_url}}"],
          "path": ["api", "auth", "companies"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000"
    },
    {
      "key": "access_token",
      "value": ""
    },
    {
      "key": "refresh_token",
      "value": ""
    }
  ]
}
'''

## postman collection

API Endpoints
Method Endpoint Description
POST /api/auth/register Register new user
POST /api/auth/login Login and get tokens
POST /api/auth/refresh Refresh access token
GET /api/auth/me Get current user
POST /api/auth/logout Logout
GET /api/auth/companies Get companies
GET /api/health Health check

## Test Credentials

After running seed.py:

### Contractors

john_doe / password123

jane_smith / password123

bob_wilson / password123

### Vendor Manager

vendor_manager / password123

### Operator Admin

operator_admin / password123

## Running Tests

bash
python -m unittest tests/test_auth.py
Postman Collection
Import Field_Contractor_Auth.postman_collection.json into Postman to test all endpoints.

### Set environment variables

base_url: [http://localhost:5000](http://localhost:5000)

access_token: (auto-populated after login)

refresh_token: (auto-populated after login)

## Intellectual Property Notice

This project was created as part of a Coding Temple Tech Residency. All work produced during the residency is considered the intellectual property of Coding Temple or the sponsoring employer, unless otherwise stated in a signed agreement. By contributing to this project, you acknowledge and agree to these terms.
