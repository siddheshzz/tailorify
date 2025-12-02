# User Stories for Tailor Cloth Stitching Backend

---

## 🧱 Epic: Project Setup

### 01. Initialize FastAPI project structure

**User Story:**  
As a developer, I want to scaffold a FastAPI project structure so I can organize code cleanly.

**Acceptance Criteria:**  
- Create base folders: `api`, `models`, `schemas`, `core`, `services`, `db`  
- Add `main.py` entry point  
- Add `__init__.py` files for all submodules  

**Labels:**  
`epic:setup`, `type:chore`

---

### 02. Add Dockerfile for FastAPI app

**User Story:**  
As a developer, I want to containerize the FastAPI app so it runs consistently in any environment.

**Acceptance Criteria:**  
- Create a `Dockerfile` using Python 3.11 slim  
- Install dependencies and expose port 8000  
- Use `uvicorn` to run app  

**Labels:**  
`epic:setup`, `type:chore`

---

### 03. Add docker-compose.yml for app + database

**User Story:**  
As a developer, I want to use Docker Compose to run both FastAPI and PostgreSQL together.

**Acceptance Criteria:**  
- Define services for API and PostgreSQL  
- Mount volumes for code and DB persistence  
- Expose ports 8000 (API) and 5432 (DB)  

**Labels:**  
`epic:setup`, `type:chore`

---

### 04. Add environment variable support using Pydantic

**User Story:**  
As a developer, I want to use `.env` files so I can separate configuration from code.

**Acceptance Criteria:**  
- Create `.env` and `.env.example` files  
- Use Pydantic `BaseSettings` in `config.py` to load env variables  
- Configure database and secret keys via env  

**Labels:**  
`epic:setup`, `type:feature`

---

### 05. Connect FastAPI to PostgreSQL using SQLAlchemy

**User Story:**  
As a developer, I want to connect to PostgreSQL so I can store application data.

**Acceptance Criteria:**  
- Install SQLAlchemy and asyncpg  
- Create DB session and engine config  
- Test connection at startup  

**Labels:**  
`epic:setup`, `type:feature`

---

# 06. Set up Alembic for database migrations

**User Story:**  
As a developer, I want to manage database schema changes with Alembic.

**Acceptance Criteria:**  
- Install and configure Alembic  
- Generate initial migration  
- Document how to run `alembic upgrade head`  

**Labels:**  
`epic:setup`, `type:chore`

---

# 07. Configure logging for FastAPI

**User Story:**  
As a developer, I want to log key events and errors so I can monitor and debug the application.

**Acceptance Criteria:**  
- Configure logging format and levels  
- Write logs to console and/or file  
- Add request/response logging for debugging  

**Labels:**  
`epic:setup`, `type:feature`

---

### 08. Add health check endpoint

**User Story:**  
As a developer, I want to have a `/healthz` endpoint so infrastructure tools can check if the API is up.

**Acceptance Criteria:**  
- Add `/healthz` route  
- Return 200 OK with JSON response  
- Ensure it works without auth  

**Labels:**  
`epic:setup`, `type:feature`

---

## 🔐 Epic: Authentication & Authorization

### 09. Create User model for authentication

**User Story:**  
As a developer, I want a user model in the database so I can store registered users.

**Acceptance Criteria:**  
- Define User table with id, email, hashed_password, created_at  
- Add Alembic migration  
- Use UUIDs or integers as primary keys  

**Labels:**  
`epic:auth`, `type:feature`

---

### 10. User can register with email and password

**User Story:**  
As a new user, I want to register with my email and password so I can create an account.

**Acceptance Criteria:**  
- Accept `email`, `password` in request  
- Validate input using Pydantic  
- Hash password and store user in DB  
- Return success or error if email exists  

**Labels:**  
`epic:auth`, `type:feature`, `priority:high`

---

### 11. User can log in and receive a JWT token

**User Story:**  
As a user, I want to log in with my email and password so I can access protected parts of the system.

**Acceptance Criteria:**  
- Accept email and password in request  
- Validate credentials against DB  
- Return access and refresh JWT tokens on success  
- Return 401 error on invalid credentials  

**Labels:**  
`epic:auth`, `type:feature`, `priority:high`

---

### 12. Protect endpoints with JWT authentication middleware

**User Story:**  
As a developer, I want to ensure protected endpoints can only be accessed by authenticated users.

**Acceptance Criteria:**  
- Create a dependency to verify JWT token  
- Apply it to protected routes  
- Return 401 Unauthorized for invalid or missing tokens  

**Labels:**  
`epic:auth`, `type:feature`

---

### 13. Secure user passwords with hashing

**User Story:**  
As a developer, I want to hash user passwords before storing them to improve security.

**Acceptance Criteria:**  
- Use `passlib` or `bcrypt` to hash passwords  
- Never store plaintext passwords  
- Verify password hashes on login  

**Labels:**  
`epic:auth`, `type:security`

---

### 14. Authenticated user can fetch their profile

**User Story:**  
As a user, I want to view my profile data so I can verify or use my account info.

**Acceptance Criteria:**  
- Return user info from JWT  
- Protect endpoint with token  
- Return fields like email, name, created_at  

**Labels:**  
`epic:auth`, `type:feature`

---

### 15. Assign user roles (admin, customer)

**User Story:**  
As an admin, I want to assign roles to users so I can control access to certain features.

**Acceptance Criteria:**  
- Add `role` column to user model  
- Allow roles: `admin`, `customer`  
- Restrict admin-only routes via role check  

**Labels:**  
`epic:auth`, `type:feature`

---

## 📦 Epic: Tailoring Services

### 16. View list of tailoring services

**User Story:**  
As a user, I want to view a list of available tailoring services so I can choose what I need.

**Acceptance Criteria:**  
- Public endpoint returns all active services  
- Include name, description, price  
- Return 200 OK with JSON  

**Labels:**  
`epic:services`, `type:feature`

---

### 17. Admin can create new tailoring service

**User Story:**  
As an admin, I want to add new tailoring services so customers can place orders.

**Acceptance Criteria:**  
- Accept `name`, `description`, `price`, `category`  
- Require admin token for access  
- Save to DB and return created service  

**Labels:**  
`epic:services`, `type:feature`, `permission:admin`

---

### 18. Admin can update or delete a tailoring service

**User Story:**  
As an admin, I want to manage tailoring services so I can edit or remove them.

**Acceptance Criteria:**  
- PATCH endpoint to update fields  
- DELETE endpoint to remove service  
- Admin access only  

**Labels:**  
`epic:services`, `type:feature`, `permission:admin`

---

### 19. View detailed information for a service

**User Story:**  
As a user, I want to view details for a specific service so I know exactly what’s included.

**Acceptance Criteria:**  
- Endpoint returns full details by service ID  
- Return 404 if service not found  

**Labels:**  
`epic:services`, `type:feature`

---

## 📦 Epic: Orders & Fittings

### 20. Place an order for a tailoring service

**User Story:**  
As a user, I want to place an order for a tailoring service with my preferences so I can get custom clothing.

**Acceptance Criteria:**  
- Accept `service_id`, measurements, notes  
- Create order in DB and associate with user  
- Return order confirmation  

**Labels:**  
`epic:orders`, `type:feature`

---

### 21. User can view their orders

**User Story:**  
As a user, I want to view my past and current orders so I can track their status.

**Acceptance Criteria:**  
- Return orders associated with the authenticated user  
- Include status, service details, created_at  

**Labels:**  
`epic:orders`, `type:feature`

---

### 22. Update order status (admin only)

**User Story:**  
As an admin, I want to update order statuses (e.g. pending, fitting, completed) so users are informed.

**Acceptance Criteria:**  
- PATCH endpoint to update order status  
- Admin access only  
- Notify user on status change (optional)  

**Labels:**  
`epic:orders`, `type:feature`, `permission:admin`

---

## 💳 Epic: Payments

### 23. Integrate payment gateway (e.g. Stripe)

**User Story:**  
As a user, I want to pay for my tailoring orders securely through a trusted payment gateway.

**Acceptance Criteria:**  
- Connect to Stripe (or similar) API  
- Create payment intent for an order  
- Handle webhook callbacks for payment confirmation  

**Labels:**  
`epic:payments`, `type:feature`

---

### 24. Store payment transaction details

**User Story:**  
As a developer, I want to store payment transaction details for auditing and user history.

**Acceptance Criteria:**  
- Save transaction ID, amount, status, timestamps  
- Associate payment with user and order  

**Labels:**  
`epic:payments`, `type:feature`

---

### 25. User can view payment history

**User Story:**  
As a user, I want to view my past payments so I can keep track of my spending.

**Acceptance Criteria:**  
- Return paginated list of payments per user  
- Include amount, date, status  

**Labels:**  
`epic:payments`, `type:feature`

---

## 🔒 Epic: Security & Testing

### 26. Add rate limiting to API

**User Story:**  
As a developer, I want to add rate limiting to prevent abuse and protect the API.

**Acceptance Criteria:**  
- Limit number of requests per IP per time window  
- Return 429 Too Many Requests on violation  

**Labels:**  
`epic:security`, `type:feature`

---

### 27. Add input validation and sanitization

**User Story:**  
As a developer, I want to validate and sanitize all inputs to prevent injection and malformed data.

**Acceptance Criteria:**  
- Use Pydantic models extensively  
- Reject invalid inputs with clear errors  

**Labels:**  
`epic:security`, `type:feature`

---

### 28. Write unit and integration tests

**User Story:**  
As a developer, I want automated tests to ensure code quality and prevent regressions.

**Acceptance Criteria:**  
- Add tests for auth, services, orders, payments  
- Use `pytest` framework  
- Achieve 80%+ coverage  

**Labels:**  
`epic:testing`, `type:chore`

---

### 29. Set up CI/CD pipeline

**User Story:**  
As a developer, I want to automate testing and deployment to ensure fast, reliable releases.

**Acceptance Criteria:**  
- Use GitHub Actions or similar  
- Run tests on PR and merge  
- Deploy on merge to main branch (optional)  

**Labels:**  
`epic:infra`, `type:chore`

---

# END OF USER STORIES
