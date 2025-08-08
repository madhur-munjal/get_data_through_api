# get_data_through_api


src/
├── main.py                     # Entry point for FastAPI app
├── core/                       # Core config, settings, security
│   ├── config.py               # Environment variables & settings
│   ├── security.py             # JWT auth, password hashing
│   └── dependencies.py         # Common dependencies (e.g., DB session)
├── models/                     # Pydantic schemas (request/response)
│   ├── user.py
│   ├── response.py
│   └── token.py
├── schemas/                         # Database layer
│   ├── base.py                 # SQLAlchemy Base
│   ├── session.py              # DB engine & session
│   └── tables/
│       ├── user.py             # SQLAlchemy models
│       └── ...
├── api/                        # Route definitions
│   ├── deps.py                 # Route-specific dependencies
│   ├── v1/
│   │   ├── user.py             # /users endpoints
│   │   └── auth.py             # /auth endpoints
│   └── router.py               # Combines all routers
├── services/                   # Business logic layer
│   ├── user_service.py
│   └── auth_service.py
├── exceptions/                 # Custom exception handlers
│   ├── handlers.py
│   └── errors.py
├── utils/                      # Utility functions
│   ├── email.py                # SMTP helpers
│   └── hashing.py              # Password hashing
├── tests/                      # Unit & integration tests
│   ├── conftest.py
│   ├── test_user.py
│   └── test_auth.py
├── alembic/                    # DB migrations (if using Alembic)
│   └── ...
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md