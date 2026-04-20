# BetesBot - Medical AI Assistant

A medical AI assistant for diabetes education. BetesBot allows users to ask questions about diabetes, view health information, and manage their chat history.

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, React Router DOM
- **Backend**: Django 6, Django REST Framework, SimpleJWT
- **Database**: PostgreSQL
- **Authentication**: Google OAuth2 with JWT cookies
- **Containerization**: Docker & Docker Compose

## Project Structure

```
.
├── docker-compose.yml          # Docker Compose configuration
├── server/                   # Django backend
│   ├── authentication/       # User authentication, OAuth, JWT
│   ├── analytics/            # Query tracking, admin analytics
│   ├── core/                 # Core views (chat endpoint)
│   ├── pdf_processing/       # PDF to Markdown conversion
│   ├── betesbot/             # Django project settings
│   └── pyproject.toml        # Python dependencies
└── frontend/                # React frontend
    ├── src/
    │   ├── pages/
    │   │   ├── Page1.tsx     # Chat interface
    │   │   ├── Page2.tsx     # Document library
    │   │   ├── Page3.tsx    # Additional page
    │   │   └── AdminAnalytics.tsx
    │   ├── context/          # Auth context
    │   ├── constants/        # API configuration
    │   └── App.tsx           # Main app routing
    └── package.json
```

## Features

- **Chat Interface**: Ask diabetes-related questions with AI-powered responses
- **Quick Prompts**: Pre-configured questions for common topics
- **Document Library**: Upload and manage PDF documents
- **Chat History**: View, export, and delete past conversations
- **Admin Analytics**: Track user queries (admin only)
- **Authentication**: Google OAuth2 login with JWT cookie authentication

## Setup

### Prerequisites

- Docker and Docker Compose
- Google OAuth2 credentials (client ID and secret)

### Environment Variables

Create `server/.env` with the following variables:

```env
SECRET_KEY=your-secret-key
DEBUG=1
DATABASE_ENGINE=postgresql
DATABASE_NAME=postgres
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=pgdb
DATABASE_PORT=5432
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
DJANGO_BASE_FRONTEND_URL=http://localhost:3000
```

### Running the Application

```bash
docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- PostgreSQL: localhost:5432

### Stopping the Application

```bash
docker compose down -v
```

## API Endpoints

- `POST /api/chat/` - Send a chat message
- `POST /api/auth/google/` - Google OAuth login
- `GET /api/auth/user/` - Get current user
- `POST /api/auth/logout/` - Logout user
- `GET /api/analytics/queries/` - List queries (admin)
- `GET /api/analytics/stats/` - Get analytics stats (admin)
- `POST /api/core/upload/` - Upload PDF document
