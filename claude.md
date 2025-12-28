# Fantasy Football League Analyzer - Project Context

## Project Overview

This is a monorepo application for analyzing fantasy football leagues. The project helps users analyze their fantasy football performance, make data-driven decisions, and gain insights from league data.

## Architecture

### Monorepo Structure
- **Backend**: FastAPI-based REST API
- **Frontend**: Vue 3 + TypeScript SPA with Vite

### Backend Architecture (Clean Architecture Pattern)

```
backend/app/
├── adapters/      # External service integrations (ESPN API, Sleeper API, etc.)
├── models/        # Domain models and Pydantic schemas
├── services/      # Business logic and domain services
├── api/           # API route handlers and endpoints
├── tasks/         # Background tasks (Celery, etc.)
├── config.py      # Application configuration
└── main.py        # FastAPI application entry point
```

**Key Patterns:**
- Adapters handle all external API calls and data transformations
- Services contain business logic and orchestrate adapter calls
- API layer is thin, delegating to services
- Models define data structures and validation

### Frontend Architecture

```
frontend/src/
├── api/           # API client and HTTP utilities
├── components/    # Reusable Vue components
├── views/         # Page-level components
├── stores/        # Pinia state management stores
├── router/        # Vue Router configuration
└── App.vue        # Root application component
```

**Key Patterns:**
- API client abstracts backend communication
- Stores manage global state
- Views are route-level components
- Components are reusable UI elements

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Server**: Uvicorn with auto-reload in dev
- **Configuration**: Pydantic Settings with .env support
- **Validation**: Pydantic v2
- **HTTP Client**: httpx
- **Testing**: pytest with async support
- **Code Quality**: Ruff for linting and formatting
- **Python**: 3.10+

### Frontend
- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Build Tool**: Vite 7.3+
- **Language**: TypeScript
- **Routing**: Vue Router 4
- **State Management**: Pinia
- **HTTP**: Native Fetch API

## Development Workflow

### Setting Up Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Setting Up Frontend
```bash
cd frontend
npm install
npm run dev
```

### Running Both
Run backend on http://localhost:8000 and frontend on http://localhost:5173

## API Design

### Current Endpoints
- `GET /` - API welcome and documentation links
- `GET /health` - Health check with app info
- `GET /docs` - Interactive Swagger UI

### Future API Structure
```
/api/v1/
├── /leagues          # League management
├── /players          # Player data and stats
├── /matchups         # Weekly matchup analysis
├── /analytics        # Advanced analytics endpoints
└── /sync             # Data synchronization from external sources
```

## Configuration

### Backend Environment Variables (.env)
```
DEBUG=true
API_PREFIX=/api/v1
```

### Frontend Environment Variables (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

## Testing Strategy

### Backend
- Unit tests for services and models
- Integration tests for API endpoints
- Test coverage with pytest-cov
- Run: `pytest --cov=app`

### Frontend
- Component tests for reusable components
- E2E tests for critical user flows
- Run: `npm run test`

## Data Flow

1. **Frontend** makes API request via `api/client.ts`
2. **API layer** receives request, validates input
3. **Service layer** processes business logic
4. **Adapter layer** fetches data from external APIs if needed
5. **Response** flows back through layers to frontend
6. **Store** (if needed) updates global state
7. **Components** reactively update UI

## Code Style

### Backend
- Line length: 100 characters
- Imports sorted and organized (Ruff)
- Type hints required for public functions
- Async/await for I/O operations

### Frontend
- TypeScript strict mode
- Composition API with `<script setup>`
- Props and emits typed
- Pinia stores for global state

## Deployment Considerations

### Backend
- Dockerfile provided for containerization
- Health check endpoint for orchestrators
- Environment-based configuration
- Runs on port 8000

### Frontend
- Static build output in `dist/`
- Can be served by any static file server
- Environment variables baked in at build time

## Project Status

**Current Phase**: Initial scaffolding complete

**Completed**:
- Monorepo structure
- Backend FastAPI skeleton with health endpoint
- Frontend Vue 3 skeleton with health check page
- Docker support for backend
- Development documentation

**Next Steps**:
- Implement fantasy platform adapters (ESPN, Sleeper, Yahoo)
- Create league data models
- Build player statistics services
- Develop analytics features
- Create frontend components for data visualization

## Related Linear Issues
- TSP-38: Initialize monorepo with FastAPI backend and Vue 3 frontend scaffolding
