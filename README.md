# 👔 Tailor Stitching Backend (FastAPI)

A modern, scalable FastAPI backend for a tailor cloth stitching service — supporting both web and mobile clients (Android/iOS). This system handles:

- 🏠 Home, Register, and Login endpoints
- 👕 Services for shirts stiching, fittings, and minute work.
-  Email/SMS integration for notification.
- 💳 Payment integration (e.g., Stripe, Razorpay)
- 🔐 JWT-based authentication
- 🔁 RESTful APIs designed for frontend and mobile consumption

---

## 🚀 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 
- **Authentication**: OAuth2 + JWT
- **Migrations**: Alembic
- **Task Queue (optional)**: Celery + Redis
- **Testing**: Pytest
- **Containerization**: Docker
- **Environment Management**: python-dotenv

---

## 📦 Project Structure (Proposed)

```

tailor-backend/
├── app/
│   ├── api/                  # All route definitions
│   │   ├── v1/               # Versioned API (v1)
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py         # Login, register
│   │   │   │   ├── users.py        # User-related routes
│   │   │   │   ├── services.py     # Tailoring services
│   │   │   │   ├── payments.py     # Payment-related endpoints
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── core/                # Core configurations
│   │   ├── config.py         # Settings using Pydantic
│   │   ├── security.py       # Auth logic (JWT, hashing)
│   │   └── __init__.py
│   │
│   ├── models/              # SQLAlchemy or Tortoise ORM models
│   │   ├── user.py
│   │   ├── service.py
│   │   ├── payment.py
│   │   └── __init__.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── service.py
│   │   ├── payment.py
│   │   └── __init__.py
│   │
│   ├── services/            # Business logic (service layer)
│   │   ├── user_service.py
│   │   ├── payment_service.py
│   │   └── __init__.py
│   │
│   ├── db/                  # Database session, init, migrations
│   │   ├── base.py           # Declarative base and init
│   │   ├── session.py        # DB session creation
│   │   └── init_db.py        # Optional: seed DB
│   │
│   ├── main.py              # Entry point for FastAPI app
│   └── __init__.py
│
├── tests/                   # Unit and integration tests
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_services.py
│   └── __init__.py
│
├── alembic/                 # Alembic migrations
│   └── (auto-generated migration files)
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt     # Optional: for dev tools
├── .env
├── .env.dev
├── .env.prod
├── .gitignore
├── .dockerignore
├── README.md
└── pyproject.toml           # (Optional: if using tools like Black, isort)

```




commands-

```

docker compose up --build


In case of any requirement changes - 
docker compose down --volumes
docker compose build --no-cache
docker compose up

```



{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYzNjE2OTMyfQ.OwqCv6yfcjhMYttjxo6ogxG1yw4GlSyZyXhaw7VuKqc",
  "token_type": "bearer"
}

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYzNjE3MDcwfQ.-HVEBCycp01hkdMVT36c1GGCs2Cm28G_60oTD2LqXNk",
  "token_type": "bearer"
}


The db is created in container so we cannot see it.
To view it you can go to docker - 

docker exec -it 2e7cf9f471f4(this is container id) sh
if sqlite is not installed - apt update && apt install -y sqlite3
sqlite3 ./app/db_data/app.db
.tables - to show tables


Ok


Todo-

check on delete all the related should also get deleted

booking
async
email
sms
aws s3



for minio setup

## Getting started

1. Create .env file:

```bash
cp .env.example .env
```

2. Run docker compose:
```bash
docker compose up
```

3. Create a bucket in MinIO Console http://localhost:9001/:
- login and password are env variables S3_ACCESS_KEY and S3_SECRET_KEY
- name of bucket to create is "my-bucket" (env variable S3_BUCKET_NAME)

Once started, the following services are available:

1. http://localhost:8000/ - Backend
2. http://localhost:8000/docs/ - API Documentation Swagger
3. http://localhost:9001/ - MinIO Console

## Useful commands

Upload a file using curl command and presigned upload link:

```bash
curl -X PUT "http://localhost:9000/my-bucket/orders/2025/12/02/4148cfe5-8ee5-4dc3-acf3-b5197c92a986?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=user%2F20251202%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251202T124625Z&X-Amz-Expires=21600&X-Amz-SignedHeaders=host&X-Amz-Signature=f76cf68d4ce386cd90078d9204bc2af61b7d10d28b0055831c572e5258480287" \
     -H "Content-Type: image/jpeg" \
     --data-binary "@/Users/f/images/2102105.jpg"

```




```bash
curl -X PUT -T backend/test_upload_file.txt "<presigned_upload_link>"
```