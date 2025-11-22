# Tailor Webapp - Complete Design & API Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Authentication Flow](#authentication-flow)
4. [API Endpoints](#api-endpoints)
5. [File Upload Strategy](#file-upload-strategy)
6. [Deployment Architecture](#deployment-architecture)

---

## Architecture Overview

### High-Level Components

**Frontend Layer**
- React/Vue.js single-page application
- Deployed on AWS Amplify or S3 + CloudFront
- Communicates with FastAPI backend via REST API
- Client-side routing and state management

**Backend Layer**
- FastAPI application handling business logic
- JWT-based authentication
- CORS enabled for frontend communication
- Deployed on AWS App Runner or EC2
- Environment-based configuration

**Data Layer**
- PostgreSQL database on AWS RDS
- SQLAlchemy ORM for database operations
- Alembic for schema migrations
- Connection pooling for performance

**Storage Layer**
- AWS S3 for image storage (gallery, client uploads)
- CloudFront CDN for image delivery
- Secure presigned URLs for client image access

**External Services**
- AWS Secrets Manager for credentials storage
- AWS CloudWatch for logging and monitoring
- AWS IAM for access control

---

## Database Schema

### Users Table
Stores client and admin user information.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | Primary Key | Unique identifier |
| email | String | Unique, Not Null | Login credential |
| password_hash | String | Not Null | Bcrypt hashed |
| first_name | String | Not Null | Client's first name |
| last_name | String | Not Null | Client's last name |
| phone | String | Optional | Contact number |
| address | String | Optional | Delivery address |
| user_type | Enum | Not Null | 'client' or 'admin' |
| created_at | DateTime | Not Null | Account creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |
| is_active | Boolean | Not Null | Default: True |

### Services Table
Catalog of tailoring services offered.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | Primary Key | Unique identifier |
| name | String | Not Null | Service name (e.g., "Hemming") |
| description | String | Optional | Detailed description |
| base_price | Decimal | Not Null | Starting price |
| category | String | Not Null | Category (alteration, custom, repair, etc.) |
| estimated_days | Integer | Not Null | Turnaround time |
| image_url | String | Optional | Service image stored in S3 |
| is_active | Boolean | Not Null | Default: True |
| created_at | DateTime | Not Null | Creation timestamp |

### Orders Table
Tracks all client order requests.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | Primary Key | Unique identifier |
| client_id | UUID | Foreign Key (Users) | References the client |
| service_id | UUID | Foreign Key (Services) | Service requested |
| status | Enum | Not Null | pending, in_progress, ready, completed, cancelled |
| description | String | Not Null | Client's detailed requirements |
| requested_date | DateTime | Not Null | When order was placed |
| estimated_completion | DateTime | Not Null | Calculated from service turnaround |
| actual_completion | DateTime | Optional | When order was actually completed |
| quoted_price | Decimal | Not Null | Final price quote |
| actual_price | Decimal | Optional | Final charged price |
| notes | String | Optional | Admin notes |
| priority | Enum | Optional | normal, high, urgent |
| created_at | DateTime | Not Null | Order creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

### Order Images Table
Stores images uploaded with orders (before/after, client photos, etc.).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | Primary Key | Unique identifier |
| order_id | UUID | Foreign Key (Orders) | Associated order |
| s3_url | String | Not Null | S3 path to image |
| image_type | Enum | Not Null | before, after, reference, instruction |
| uploaded_by | UUID | Foreign Key (Users) | Who uploaded it |
| uploaded_at | DateTime | Not Null | Upload timestamp |

### Gallery Table
Public portfolio of completed work.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | Primary Key | Unique identifier |
| title | String | Not Null | Project title |
| description | String | Optional | Details about the work |
| service_category | String | Not Null | Type of work shown |
| before_image_url | String | Optional | S3 URL for before image |
| after_image_url | String | Not Null | S3 URL for after image |
| created_at | DateTime | Not Null | When added to gallery |

---

## Authentication Flow

### Registration Flow (Client)
1. Client provides email, password, name, phone, address
2. Backend validates email format and uniqueness
3. Backend hashes password with bcrypt (rounds: 12)
4. User created with user_type='client'
5. Return success with user ID (no auto-login)
6. Client redirected to login page

### Login Flow
1. Client submits email and password
2. Backend finds user by email
3. Backend verifies password hash
4. Backend generates JWT token with:
   - User ID
   - Email
   - User type
   - Expiration (30 minutes)
   - Issue timestamp
5. Return access token and refresh token
6. Frontend stores token in secure httpOnly cookie or localStorage
7. Subsequent requests include token in Authorization header

### Token Refresh
1. Client sends refresh token
2. Backend validates refresh token (longer expiration, like 7 days)
3. Backend generates new access token
4. Return new access token

### Admin Authentication
- Admin users created manually in database or special registration endpoint
- Same JWT flow as clients
- user_type='admin' distinguishes permissions

---

## API Endpoints

### Authentication Routes

#### POST /api/auth/register
Register a new client account.

**Request Body:**
```json
{
  "email": "client@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St, City"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-here",
  "email": "client@example.com",
  "first_name": "John",
  "message": "Registration successful. Please log in."
}
```

#### POST /api/auth/login
Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "client@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "jwt-token-here",
  "refresh_token": "refresh-jwt-here",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "client@example.com",
    "user_type": "client"
  }
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request Header:** Authorization: Bearer {refresh_token}

**Response (200 OK):**
```json
{
  "access_token": "new-jwt-token",
  "token_type": "bearer"
}
```

#### POST /api/auth/logout
Invalidate tokens (optional—client can delete tokens locally).

---

### Services Routes

#### GET /api/services
List all active services with pricing and details.

**Query Parameters:**
- category (optional): Filter by category (alteration, custom, repair)
- page (optional): Pagination page number

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Pants Hemming",
      "description": "Professional hemming for all types of pants",
      "base_price": 25.00,
      "category": "alteration",
      "estimated_days": 3,
      "image_url": "https://cloudfront.../image.jpg"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10
}
```

#### GET /api/services/{service_id}
Get detailed information about a specific service.

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "Custom Suit Tailoring",
  "description": "Full custom suit from fabric selection to fitting",
  "base_price": 500.00,
  "category": "custom",
  "estimated_days": 14,
  "image_url": "https://cloudfront.../image.jpg"
}
```

#### GET /api/services/categories
List available service categories.

**Response (200 OK):**
```json
{
  "categories": ["alteration", "custom", "repair", "wedding", "casualwear"]
}
```

---

### Orders Routes

#### POST /api/orders
Create a new order (requires authentication).

**Request Header:** Authorization: Bearer {access_token}

**Request Body:**
```json
{
  "service_id": "uuid-of-service",
  "description": "Need pants hemmed to knee length, currently too long",
  "priority": "normal",
  "preferred_completion_date": "2025-12-15"
}
```

**Response (201 Created):**
```json
{
  "id": "order-uuid",
  "client_id": "client-uuid",
  "service_id": "service-uuid",
  "status": "pending",
  "description": "Need pants hemmed...",
  "requested_date": "2025-11-22T10:30:00Z",
  "estimated_completion": "2025-11-25T10:30:00Z",
  "quoted_price": 25.00,
  "message": "Order created successfully. Please upload images if needed."
}
```

#### POST /api/orders/{order_id}/upload-images
Upload images for an order (before photos, measurements, etc.).

**Request Header:** Authorization: Bearer {access_token}

**Form Data:**
- Files: MultipartFile (multiple images allowed)
- image_type: "before" | "reference" | "instruction"

**Response (200 OK):**
```json
{
  "order_id": "order-uuid",
  "uploaded_images": [
    {
      "id": "image-uuid",
      "image_type": "before",
      "s3_url": "https://cloudfront.../image1.jpg",
      "uploaded_at": "2025-11-22T10:35:00Z"
    }
  ]
}
```

#### GET /api/orders
List client's orders (requires authentication).

**Request Header:** Authorization: Bearer {access_token}

**Query Parameters:**
- status (optional): Filter by status (pending, in_progress, ready, completed)
- page (optional): Pagination
- sort_by (optional): created_date, estimated_completion

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "order-uuid",
      "service_name": "Pants Hemming",
      "status": "in_progress",
      "requested_date": "2025-11-22T10:30:00Z",
      "estimated_completion": "2025-11-25T10:30:00Z",
      "quoted_price": 25.00
    }
  ],
  "total": 5,
  "page": 1
}
```

#### GET /api/orders/{order_id}
Get detailed order information.

**Request Header:** Authorization: Bearer {access_token}

**Response (200 OK):**
```json
{
  "id": "order-uuid",
  "client_id": "client-uuid",
  "service_id": "service-uuid",
  "service_name": "Pants Hemming",
  "status": "in_progress",
  "description": "Need pants hemmed to knee length",
  "requested_date": "2025-11-22T10:30:00Z",
  "estimated_completion": "2025-11-25T10:30:00Z",
  "actual_completion": null,
  "quoted_price": 25.00,
  "images": [
    {
      "id": "image-uuid",
      "image_type": "before",
      "s3_url": "https://cloudfront.../image.jpg"
    }
  ],
  "notes": "Hemmed to exactly knee length. Ready for pickup."
}
```

#### PUT /api/orders/{order_id}
Update order (client can update pending orders only).

**Request Header:** Authorization: Bearer {access_token}

**Request Body:**
```json
{
  "description": "Updated description",
  "priority": "high"
}
```

**Response (200 OK):**
```json
{
  "id": "order-uuid",
  "status": "pending",
  "message": "Order updated successfully"
}
```

#### DELETE /api/orders/{order_id}
Cancel order (only if status is 'pending').

**Request Header:** Authorization: Bearer {access_token}

**Response (200 OK):**
```json
{
  "message": "Order cancelled successfully"
}
```

---

### Client Profile Routes

#### GET /api/clients/profile
Get authenticated client's profile.

**Request Header:** Authorization: Bearer {access_token}

**Response (200 OK):**
```json
{
  "id": "client-uuid",
  "email": "client@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St, City",
  "created_at": "2025-11-01T00:00:00Z",
  "total_orders": 5,
  "completed_orders": 3
}
```

#### PUT /api/clients/profile
Update client profile.

**Request Header:** Authorization: Bearer {access_token}

**Request Body:**
```json
{
  "phone": "+1987654321",
  "address": "456 Oak Ave, City",
  "first_name": "Jonathan"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "updated_fields": ["phone", "address", "first_name"]
}
```

#### PUT /api/clients/change-password
Change password.

**Request Header:** Authorization: Bearer {access_token}

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

### Gallery Routes

#### GET /api/gallery
Get portfolio gallery of completed work (public endpoint).

**Query Parameters:**
- category (optional): Filter by service category
- page (optional): Pagination
- limit (optional): Items per page (default 12)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "gallery-uuid",
      "title": "Custom Italian Suit",
      "description": "Hand-tailored suit from premium Italian fabric",
      "service_category": "custom",
      "before_image_url": "https://cloudfront.../before.jpg",
      "after_image_url": "https://cloudfront.../after.jpg",
      "created_at": "2025-10-15T00:00:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 12
}
```

#### GET /api/gallery/{gallery_id}
Get detailed gallery entry.

**Response (200 OK):**
```json
{
  "id": "gallery-uuid",
  "title": "Custom Italian Suit",
  "description": "Hand-tailored suit from premium Italian fabric",
  "service_category": "custom",
  "before_image_url": "https://cloudfront.../before.jpg",
  "after_image_url": "https://cloudfront.../after.jpg"
}
```

---

### Admin Routes (Requires Admin Authentication)

#### GET /api/admin/orders
Get all orders (pagination, filtering, sorting).

**Request Header:** Authorization: Bearer {admin_token}

**Query Parameters:**
- status (optional): Filter by status
- client_name (optional): Search by client name
- date_from, date_to (optional): Date range filter
- page, page_size: Pagination
- sort_by: created_date, estimated_completion, priority

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "order-uuid",
      "client_name": "John Doe",
      "client_email": "john@example.com",
      "service_name": "Pants Hemming",
      "status": "pending",
      "requested_date": "2025-11-22T10:30:00Z",
      "estimated_completion": "2025-11-25T10:30:00Z",
      "quoted_price": 25.00,
      "priority": "normal"
    }
  ],
  "total": 47,
  "page": 1
}
```

#### PATCH /api/admin/orders/{order_id}
Update order status and add admin notes.

**Request Header:** Authorization: Bearer {admin_token}

**Request Body:**
```json
{
  "status": "in_progress",
  "notes": "Started work on hemming. Client specified knee length.",
  "actual_price": 25.00
}
```

**Response (200 OK):**
```json
{
  "id": "order-uuid",
  "status": "in_progress",
  "updated_at": "2025-11-22T14:00:00Z",
  "message": "Order updated successfully"
}
```

#### POST /api/admin/gallery
Add new entry to gallery (admin only).

**Request Header:** Authorization: Bearer {admin_token}

**Request Body:**
```json
{
  "title": "Custom Wedding Suit",
  "description": "Bespoke wedding suit with custom details",
  "service_category": "custom",
  "order_id": "order-uuid"
}
```

**Response (201 Created):**
```json
{
  "id": "gallery-uuid",
  "title": "Custom Wedding Suit",
  "message": "Gallery entry created. Upload before/after images next."
}
```

#### POST /api/admin/gallery/{gallery_id}/upload-images
Upload before and after images for gallery.

**Request Header:** Authorization: Bearer {admin_token}

**Form Data:**
- before_image: File
- after_image: File

**Response (200 OK):**
```json
{
  "gallery_id": "gallery-uuid",
  "before_image_url": "https://cloudfront.../before.jpg",
  "after_image_url": "https://cloudfront.../after.jpg"
}
```

#### POST /api/admin/services
Create new service offering (admin only).

**Request Header:** Authorization: Bearer {admin_token}

**Request Body:**
```json
{
  "name": "Wedding Alterations",
  "description": "Complete alteration service for wedding attire",
  "base_price": 75.00,
  "category": "wedding",
  "estimated_days": 7
}
```

**Response (201 Created):**
```json
{
  "id": "service-uuid",
  "name": "Wedding Alterations",
  "message": "Service created successfully"
}
```

#### GET /api/admin/dashboard
Admin dashboard with key metrics.

**Request Header:** Authorization: Bearer {admin_token}

**Response (200 OK):**
```json
{
  "total_orders": 150,
  "pending_orders": 12,
  "in_progress_orders": 8,
  "completed_this_month": 45,
  "total_clients": 87,
  "total_revenue": 5420.50,
  "average_completion_time_days": 5.2,
  "recent_orders": [
    {
      "id": "order-uuid",
      "client_name": "Jane Smith",
      "status": "pending",
      "requested_date": "2025-11-22T10:30:00Z"
    }
  ]
}
```

---

## File Upload Strategy

### Image Upload Flow

**Frontend:**
1. User selects images from their device
2. Frontend validates: format (JPG, PNG), size (max 5MB each), dimensions (min 300x300px)
3. Frontend shows preview to user
4. On confirmation, frontend calls upload endpoint with FormData

**Backend:**
1. Validate file type and size again (server-side)
2. Generate unique filename: `{order_id}/{timestamp}_{random}.jpg`
3. Upload to S3 with private ACL
4. Generate presigned URL valid for 7 days
5. Store presigned URL in database
6. Return URL to frontend

**Storage Structure on S3:**
```
s3://tailor-webapp-images/
├── gallery/
│   ├── {gallery_id}/
│   │   ├── before.jpg
│   │   └── after.jpg
├── orders/
│   ├── {order_id}/
│   │   ├── 1732281000_abc123.jpg
│   │   ├── 1732281010_def456.jpg
├── services/
│   ├── {service_id}/
│   │   └── image.jpg
```

**Access Pattern:**
- Gallery images: Public read via CloudFront
- Order images: Private with presigned URLs (7-day expiry)
- Service images: Public via CloudFront

---

## Deployment Architecture

### Local Development
- FastAPI running on `localhost:8000`
- PostgreSQL on `localhost:5432`
- Frontend on `localhost:3000`
- S3 emulation with LocalStack (optional)
- All via Docker Compose

### Staging Environment
- FastAPI on AWS App Runner or EC2
- PostgreSQL on AWS RDS (small instance)
- S3 for image storage
- CloudFront CDN
- Route 53 for domain (`staging.tailorapp.com`)

### Production Environment
- **Compute:** AWS App Runner (auto-scaling, managed)
  - Or EC2 with Auto Scaling Group if more control needed
- **Database:** AWS RDS PostgreSQL (Multi-AZ for high availability)
  - Automated backups, read replicas
- **Storage:** AWS S3 with versioning enabled
- **CDN:** CloudFront with TTL of 30 days for images
- **DNS:** Route 53 pointing to CloudFront and App Runner
- **Monitoring:** CloudWatch dashboards and alarms
- **Logging:** CloudWatch Logs with log retention (30 days)
- **Security:**
  - WAF on CloudFront
  - VPC with security groups
  - RDS in private subnet
  - Secrets Manager for credentials
  - SSL/TLS everywhere (ACM certificates)

### CI/CD Pipeline (GitHub Actions)
1. Developer pushes to GitHub
2. GitHub Actions runs:
   - Unit tests
   - Integration tests
   - Linting and code quality checks
3. Build Docker image and push to ECR
4. Deploy to staging automatically
5. Manual approval for production deployment
6. Deploy to production
7. Run smoke tests
8. Notify team of deployment status

### Environment Variables Management
```
Development: .env file locally
Staging: AWS Secrets Manager
Production: AWS Secrets Manager
```

Critical secrets:
- DATABASE_URL
- SECRET_KEY
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- JWT tokens configuration

### Database Migrations
- Use Alembic for schema versioning
- Migrations run before app startup
- Rollback capability for each migration
- Staging environment tested before production

### Monitoring & Alerts
- CPU and memory usage on compute
- Database connection pool health
- API response times
- Error rates and exceptions
- S3 storage growth
- CloudFront cache hit ratio
- Alerts for: high error rate (>5%), slow response times (>1s), database issues

### Backup & Disaster Recovery
- RDS automated backups (daily, 30-day retention)
- S3 versioning enabled
- Database restore tested monthly
- Recovery time objective (RTO): 1 hour
- Recovery point objective (RPO): 1 hour