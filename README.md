# Fantasy Football League Analyzer

A monorepo application for analyzing fantasy football leagues, built with FastAPI (backend) and Vue 3 (frontend).

## Project Structure

```
fantasy-analyzer/
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── config.py       # Application configuration
│   │   ├── adapters/       # External service adapters
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   ├── api/            # API endpoints
│   │   └── tasks/          # Background tasks
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/           # Vue 3 frontend application
│   ├── src/
│   │   ├── api/            # API client utilities
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page views
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router config
│   └── package.json
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

## Backend Setup

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. For development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running the Backend

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Running with Docker

Build and run the Docker container:
```bash
docker build -t fantasy-analyzer-backend .
docker run -p 8000:8000 fantasy-analyzer-backend
```

### Running Tests

```bash
pytest
```

For coverage report:
```bash
pytest --cov=app --cov-report=html
```

## Frontend Setup

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Frontend

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

### Building for Production

```bash
npm run build
```

The production-ready files will be in the `dist/` directory.

### Running Tests

```bash
npm run test
```

## Development Workflow

### Running Both Services

You'll need two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser to see the health check page.

## Environment Variables

### Backend

Create a `.env` file in the `backend/` directory:

```env
DEBUG=true
API_PREFIX=/api/v1
```

### Frontend

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API Endpoints

### Current Endpoints

- `GET /` - API welcome message
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **HTTP Server:** Uvicorn
- **Configuration:** Pydantic Settings
- **Testing:** pytest

### Frontend
- **Framework:** Vue 3
- **Build Tool:** Vite
- **Language:** TypeScript
- **Routing:** Vue Router
- **State Management:** Pinia
- **HTTP Client:** Fetch API

## License

MIT
