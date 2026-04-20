# SmartSeason Field Monitoring System — Backend

REST API built with **Django 6 + PostgreSQL** for tracking crop progress across multiple fields during a growing season.

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+

### Steps

```bash
# 1. Clone and enter the repo
git clone git@github.com:waltertaya/SmartSeason-Field-Monitoring-Backend-Assessment.git
cd SmartSeason-Field-Monitoring-Backend-Assessment

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your DB credentials

# 5. Create the database
createdb smartseason_db   # or via psql

# 6. Run migrations
python manage.py migrate

# 7. Create demo users (optional)
python manage.py create_demo_users

# 8. Start the server
python manage.py runserver
```

## Demo Credentials

| Role        | Username | Password   |
|-------------|----------|------------|
| Admin       | admin    | admin@2026?|
| Field Agent | agent    | agent@2026?|

## API Endpoints

### Auth
| Method | Endpoint              | Description               | Access |
|--------|-----------------------|---------------------------|--------|
| POST   | /api/auth/register/   | Register a new user       | Public |
| POST   | /api/auth/login/      | Obtain JWT tokens         | Public |
| POST   | /api/auth/token/refresh/ | Refresh access token   | Public |
| GET    | /api/auth/me/         | Get current user profile  | Auth   |
| GET    | /api/auth/agents/     | List all field agents     | Admin  |

### Fields
| Method | Endpoint                     | Description                  | Access              |
|--------|------------------------------|------------------------------|---------------------|
| GET    | /api/fields/                 | List fields                  | Admin (all) / Agent (assigned) |
| POST   | /api/fields/                 | Create a field               | Admin               |
| GET    | /api/fields/{id}/            | Get field detail             | Admin / Assigned Agent |
| PUT    | /api/fields/{id}/            | Update a field               | Admin               |
| DELETE | /api/fields/{id}/            | Delete a field               | Admin               |
| GET    | /api/fields/{id}/updates/    | List updates for a field     | Admin / Assigned Agent |
| POST   | /api/fields/{id}/updates/    | Add an update                | Assigned Agent      |
| GET    | /api/fields/dashboard/       | Dashboard summary            | Auth (role-scoped)  |

## Design Decisions

### Field Status Logic

Each field has a **computed status** (`active`, `at_risk`, `completed`) derived from its stage and update history:

- **Completed** — field is in the `harvested` stage.
- **At Risk** — the field has gone too long without an update relative to its current stage:
  - `planted` → no update in **7 days**
  - `growing` → no update in **14 days**
  - `ready` → no update in **5 days** (time-sensitive — ready to harvest)
- **Active** — everything else.

The reference date used is the date of the most recent update; if there are no updates yet, the planting date is used. This ensures newly planted fields start as Active and only become At Risk if they are neglected.

### Roles & Permissions

- Admins can create/edit fields, assign agents, and see everything.
- Field Agents can only see their assigned fields and add updates to them.
- JWT tokens (Bearer) are used for stateless auth. Access tokens last 12 hours; refresh tokens last 7 days.

### Field Stages

`planted → growing → ready → harvested` — when an agent submits an update, the field's stage is automatically advanced to the stage indicated in the update.

## Assumptions

- A field can only be assigned to one agent at a time.
- Only admins can register other users (post-MVP: self-registration can be enabled per need).
- Status is computed on-the-fly (not stored) to always reflect current reality without needing a background job.
