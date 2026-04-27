# BetesBot - Medical AI Assistant

A medical AI assistant for diabetes education. BetesBot allows users to ask questions about diabetes, view health information, and manage their chat history.

## Live Demo
[Demo](https://capstone-medical-gen-ai-fe-524283018158.us-east1.run.app/)

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, React Router DOM
- **Backend**: Django 6, Django REST Framework, SimpleJWT
- **Database**: PostgreSQL
- **Authentication**: Google OAuth2 with JWT cookies
- **Containerization**: Docker & Docker Compose

## Project Structure

```
.
├── docker-compose.yml        # Docker Compose configuration
├── server/                   # Django backend
│   ├── authentication/       # User authentication, OAuth, JWT
│   ├── analytics/            # Query tracking, admin analytics
│   ├── core/                 # Core views (chat endpoint)
│   ├── pdf_processing/       # PDF to Markdown conversion
│   ├── betesbot/             # Django project settings
│   └── pyproject.toml        # Python dependencies
└── frontend/                 # React frontend
    ├── src/
    │   ├── pages/
    │   │   ├── Page1.tsx     # Chat interface
    │   │   ├── Page2.tsx     # Document library
    │   │   ├── Page3.tsx     # History page
    │   │   └── AdminAnalytics.tsx
    │   ├── context/          # Auth context
    │   ├── constants/        # API configuration
    │   └── App.tsx           # Main app routing
    └── package.json
```

## Features

- **Login/Signup**: Login with email and password or with Google
- **Chat Interface**: Ask diabetes-related questions with AI-powered responses
- **Document Library**: Upload and manage PDF documents
- **Domain Specific**: Only responds with context from uploaded documents
- **Chat History**: View past conversations
- **Admin Analytics**: Track user queries and manage documents (admin only)

## Known Bugs

- **Signup without confirmation**: Signup with email does not require email confirmation
- **PDF extraction accuracy**: PDF to text conversion has approximately a 1 in 30 chance of missing information due to the way PyMuPDF extracts PDF pages
- **API cold start timeout**: Chat requests may timeout on the first attempt due to AI infrastructure API cold starts (retry typically succeeds)

## Build, Install, and Configuration

### Prerequisites

- Docker and Docker Compose
- Google OAuth2 credentials (client ID and secret)

### Environment Variables

Create `server/.env` in the project root with the following variables:

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

Navigate to `frontend/constants/constants.ts` and change:
```
const USE_LOCAL = true
```

### Building the Project

1. Ensure Docker Desktop or Docker daemon is running
2. Navigate to the project root directory
3. Build and start all containers:

```bash
docker compose up --build
```

The Docker Compose configuration handles:
- PostgreSQL database initialization
- Django database migrations (`migrate`)
- Gunicorn server setup with 4 workers
- Frontend and backend serving

### Stopping the Application

To stop all containers and remove volumes:

```bash
docker compose down -v
```

To stop without removing volumes (preserves data):

```bash
docker compose down
```

### Accessing the Application

After successful build, the services are available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### Troubleshooting

- **Database connection issues**: Ensure PostgreSQL container is running (`docker compose ps`)
- **Frontend not loading**: Check that the django-api container started successfully first
- **JWT authentication failures**: Verify `SECRET_KEY` and `DEBUG` settings in `.env`

## API Endpoints

- `POST /api/chat/` - Send a chat message
- `POST /api/auth/google/` - Google OAuth login
- `GET /api/auth/user/` - Get current user
- `POST /api/auth/logout/` - Logout user
- `GET /api/history/` - List user's chat history
- `GET /api/history/?chat_id={id}` - Get specific chat messages
- `DELETE /api/history/?chat_id={id}` - Delete a chat
- `GET /api/analytics/queries/` - List queries (admin)
- `GET /api/analytics/stats/` - Get analytics stats (admin)
- `GET /api/analytics/admin/` - Get admin dashboard data including failed documents
- `GET /api/analytics/document/?source={name}` - Get document details
- `DELETE /api/analytics/document/?source={name}` - Delete a document (admin)
- `POST /api/core/upload/` - Upload PDF document
