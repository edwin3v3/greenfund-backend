# Backend Project Structure — GreenFund Backend

This file documents the current backend repository structure and a short description for important files and folders. Use this as a quick reference when navigating the codebase.

Root

```
GreenFund-test-Backend/
├── .env                     # Local environment file (secrets, DB url, OPENAI_API_KEY)
├── .env.example             # Example environment variables (placeholders)
├── README.md                # Project README (overview and setup)
├── Dockerfile               # Dockerfile for the backend service
├── docker-compose.yml       # Compose file for backend + postgres
├── requirements.txt         # Python dependencies
├── alembic/                 # Database migration scripts
├── alembic.ini              # Alembic configuration
├── app/                     # Application source
├── tests/                   # Pytest tests
└── venv/                    # Local virtual environment (not committed ideally)
```

Key top-level notes

- `docker-compose.yml` configures `backend` and `db` services (Postgres). The backend runs Uvicorn and depends on the DB service.
- `requirements.txt` lists runtime dependencies including `fastapi`, `sqlmodel`, `openai`, `bcrypt`, and `alembic`.

app/ (main application)

```
app/
├── __init__.py
├── main.py                 # FastAPI app, router registration and startup lifecycle
├── database.py             # DB engine & get_db dependency (SQLModel + SQLAlchemy)
├── models.py               # SQLModel/ORM models (User, Farm, SoilReport, etc.)
├── schemas.py              # Pydantic/SQLModel schemas (request/response models)
├── security.py             # Authentication (JWT), password hashing (bcrypt), dependencies
├── soil_model.py           # OpenAI client helper and AI soil analysis functions
├── climate_rules.py        # Rule-based assessments (water stress, pest risk, carbon trend)
├── recommendations.py      # Generates recommendations combining rules + AI
├── carbon_model.py         # (domain-specific carbon calculations)
├── utils.py                # Helper utilities
└── routers/
    ├── auth.py            # Registration / token endpoints (/api/auth)
    ├── users.py           # User profile endpoints (/api/users)
    ├── farms.py           # Farm CRUD endpoints (/api/farms)
    ├── activities.py      # Farm activity logging endpoints (/api/activities)
    ├── soil.py            # Soil reporting and image analysis endpoints (/api/soil)
    ├── climate.py         # Climate/weather related endpoints (/api/climate)
    ├── climate_actions.py # AI-assisted climate advice endpoints (/api/climate-actions)
    ├── chatbot.py         # Chatbot endpoint (/chatbot/ask)
    ├── badges.py          # Badge listing and user badge endpoints
    ├── notifications.py   # Notification endpoints and unread-count logic
    └── forum.py           # Forum threads and posts
```

Notable files and responsibilities

- `app/main.py`

  - Constructs the FastAPI app and registers an `APIRouter` with prefix `/api`.
  - Includes CORS middleware and a startup lifespan handler to create DB tables.

- `app/database.py`

  - Exposes the SQLModel engine and `get_db` dependency used across routers/tests.

- `app/models.py` & `app/schemas.py`

  - `models.py` contains the DB models (tables). `schemas.py` contains request/response Pydantic models used for validation and documentation.
  - Recent Pydantic config was migrated to `model_config = ConfigDict(from_attributes=True)` to comply with Pydantic v2.

- `app/security.py`

  - Password hashing & verification using `bcrypt`.
  - JWT creation and decoding via `python-jose`.
  - `get_current_user` dependency for protected endpoints.

- `app/soil_model.py` & `app/recommendations.py`

  - `soil_model.py` holds OpenAI client creation (`get_openai_client`) and wrappers for textual and image-based soil analysis.
  - `recommendations.py` combines rule-based logic with AI calls to generate farmer-facing recommendations.

- `app/climate_rules.py`

  - Simple, deterministic rules for pest/disease risks, water stress, and carbon trend assessments. Used to reduce reliance on AI for core checks and to provide structured prompts to AI.

- `app/routers/` endpoints
  - Auth: `/api/auth/register` and `/api/auth/token` (OAuth2PasswordBearer configured)
  - Users: `/api/users/me`, update and change password
  - Soil: `/api/soil/manual` (textual analysis) and `/api/soil/upload_soil_image/{farm_id}` (image analysis)
  - Climate Actions: `/api/climate-actions/*` (AI-enhanced alerts, carbon guidance, water advice)
  - Chatbot: `/chatbot/ask` (AI assistant)

tests/

```
tests/
├── conftest.py            # Test fixtures (test DB, client, test_user)
└── test_auth.py           # Authentication and user-related tests (pytest)
```

Useful commands

- Run locally (development):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Run tests:

```bash
DATABASE_URL=sqlite:/// pytest tests/ -v
```

- Run with Docker Compose:

```bash
docker-compose up --build
```

Tips & next steps

- Add `BACKEND_STRUCTURE.md` to source control (this file). Keep it updated as the project grows.
- Consider adding `API_DOCS.md` or linking to specific routers in the README for more granular documentation.
- Add integration tests for AI endpoints that mock `get_openai_client` to avoid calling the real OpenAI API during CI.

If you want, I can:

- add a `.env.example` file (placeholders for `OPENAI_API_KEY`, `DATABASE_URL`, `SECRET_KEY`), or
- generate a machine-readable JSON representation of the tree (useful for automation), or
- create an `API_DOCS.md` that maps each endpoint to the handler file and schema.

---

Generated on: 2025-10-27
