# API Reference

**Base URL:** `/api/v1`

## Authentication
Uses JSON Web Tokens (JWT). Send `Authorization: Bearer <token>` in headers.

### `POST /auth/login`
- **Description:** Authenticate user and return JWT.
- **Auth:** None
- **Body:** `OAuth2PasswordRequestForm` (username, password)
- **Response:**
  ```json
  {
    "access_token": "eyJhbG...",
    "token_type": "bearer"
  }
  ```

### `POST /users/register`
- **Description:** Register a new user.
- **Auth:** None
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword",
    "full_name": "John Doe",
    "role": "citizen"
  }
  ```

## Citizen Complaints

### `GET /complaints`
- **Description:** Get list of complaints.
- **Auth:** Required
- **Query Params:** `skip` (int), `limit` (int), `status` (str)
- **Response:** Array of Complaint objects.

### `POST /complaints`
- **Description:** Submit a new complaint.
- **Auth:** Required (Citizen)
- **Body (Multipart form-data):** `title`, `description`, `latitude`, `longitude`, `image` (file).
- **Response:** 201 Created.

### `GET /complaints/{id}`
- **Description:** Get complaint details.
- **Auth:** Required
- **Response:** Complaint object with AI analysis payload.

## AI Analysis (Internal / Admin)

### `POST /ai/analyze/{complaint_id}`
- **Description:** Manually trigger AI analysis for a complaint.
- **Auth:** Required (Admin)
- **Response:** Analysis results (Severity, Confidence, Class).

## Admin Management

### `PUT /complaints/{id}/status`
- **Description:** Update complaint status.
- **Auth:** Required (Admin/Department)
- **Body:**
  ```json
  {
    "status": "in_progress",
    "comments": "Team dispatched."
  }
  ```
