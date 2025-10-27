# GreenFund Backend Structure

GreenFund-test-Backend/
├── app/
│ ├── routers/
│ │ ├── **init**.py
│ │ ├── activities.py
│ │ ├── auth.py
│ │ ├── badges.py
│ │ ├── chatbot.py
│ │ ├── climate_actions.py
│ │ ├── climate.py
│ │ ├── farms.py
│ │ ├── forum.py
│ │ ├── notifications.py
│ │ ├── soil.py
│ │ ├── test_router.py
│ │ └── users.py
│ ├── **init**.py
│ ├── carbon_model.py
│ ├── climate_rules.py
│ ├── database.py
│ ├── main.py
│ ├── models.py
│ ├── recommendations.py
│ ├── schemas.py
│ ├── security.py
│ ├── soil_model.py
│ └── utils.py
├── tests/
│ ├── **init**.py
│ ├── conftest.py
│ └── test_auth.py
├── alembic/
│ ├── versions/
│ │ ├── 03ae600d10ce_add_badge_and_userbadge_tables.py
│ │ ├── 8dc493c306c7_add_badge_models_and_user_relationship.py
│ │ └── f078b8a06b59_add_notification_model.py
│ ├── env.py
│ ├── README
│ └── script.py.mako
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── BACKEND_STRUCTURE.md
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt

````

## Key Components

### API Routers (`app/routers/`)
- `activities.py`: Handles farm activity logging and tracking
- `auth.py`: User authentication and authorization
- `badges.py`: User achievement and gamification system
- `chatbot.py`: AI-powered farming assistant
- `climate_actions.py`: Climate-smart farming recommendations
- `farms.py`: Farm management and data
- `forum.py`: Community discussion platform
- `notifications.py`: User notification system
- `soil.py`: Soil health analysis and reporting

### Core Modules (`app/`)
- `carbon_model.py`: Carbon footprint calculation logic
- `climate_rules.py`: Climate risk assessment rules
- `database.py`: Database connection and configuration
- `models.py`: Database models (SQLModel)
- `schemas.py`: API request/response schemas
- `security.py`: Authentication and security utilities
- `soil_model.py`: AI-powered soil analysis
- `recommendations.py`: Smart farming recommendations

### Database Migrations (`alembic/`)
Tracks database schema changes including:
- Badge system implementation
- Notification system addition
- User relationships and models

### Testing (`tests/`)
- `conftest.py`: Test fixtures and configurations
- `test_auth.py`: Authentication system tests

## Configuration Files
- `requirements.txt`: Python package dependencies
- `docker-compose.yml`: Multi-container Docker setup
- `Dockerfile`: Backend service container configuration
- `alembic.ini`: Database migration settings

## Environment Setup
Required environment variables (defined in `.env`):
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT encryption key
- `OPENAI_API_KEY`: OpenAI API authentication
- Other service-specific configurations

## Development Commands

### Local Development
```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
DATABASE_URL=sqlite:/// pytest tests/ -v

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
````

### Docker Development

```bash
# Build and start services
docker-compose up --build

# Stop services
docker-compose down
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The backend implements a RESTful API with the following main features:

- User authentication and authorization
- Farm management and monitoring
- Soil health analysis with AI
- Climate-smart farming recommendations
- Community forum and notifications
- Achievement/badge system
- AI-powered chatbot assistance
