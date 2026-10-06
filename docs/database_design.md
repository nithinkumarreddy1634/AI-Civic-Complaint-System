# Database Design

## ER Diagram (Text Representation)

```text
[ Users ] 1 ------ * [ Complaints ]
                        |
                        | 1
                        |
                        * [ Images ]
                        
[ Complaints ] * ----- 1 [ Departments ]
```

## Table Descriptions

### `users`
- **Purpose:** Stores user accounts, authentication data, and roles.
- **Columns:**
  - `id` (UUID, Primary Key)
  - `email` (String, Unique, Indexed)
  - `hashed_password` (String)
  - `full_name` (String)
  - `role` (Enum: admin, citizen, department)
  - `created_at` (DateTime)

### `complaints`
- **Purpose:** Core table tracking civic issues.
- **Columns:**
  - `id` (UUID, Primary Key)
  - `title` (String)
  - `description` (Text)
  - `latitude` (Float)
  - `longitude` (Float)
  - `status` (Enum: pending, verified, rejected, in_progress, resolved)
  - `severity` (Enum: low, medium, high, critical)
  - `priority_score` (Float)
  - `ai_verification_confidence` (Float)
  - `category` (String)
  - `user_id` (UUID, Foreign Key -> users.id)
  - `department_id` (UUID, Foreign Key -> departments.id)
  - `duplicate_cluster_id` (UUID, Nullable)

### `complaint_images`
- **Purpose:** Stores paths to uploaded evidence.
- **Columns:**
  - `id` (UUID, Primary Key)
  - `complaint_id` (UUID, Foreign Key -> complaints.id)
  - `file_path` (String)

### `departments`
- **Purpose:** Civic departments resolving issues.
- **Columns:**
  - `id` (UUID, Primary Key)
  - `name` (String)

## Relationships
- A User can have many Complaints.
- A Complaint has one (primary) Image.
- A Complaint is assigned to one Department.

## Migration Strategy
- Alembic will be configured in Phase 2 for database migrations tracking schema changes natively.
