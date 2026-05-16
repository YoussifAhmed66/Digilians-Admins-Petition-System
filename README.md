# Admin Petitions — Backend

FastAPI backend for the admin petitions dashboard. Handles petition review, decision-making, and document management.

## Tech Stack

- **Framework:** FastAPI (Python 3.11)
- **Database:** Supabase (PostgreSQL)
- **Storage:** Supabase Storage (attachments + generated PDFs)
- **PDF Generation:** LibreOffice Writer
- **Deployment:** Google Cloud Run

## Project Structure

```
admin_project/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, Supabase client
│   │   ├── routes/        # API endpoints (admin router)
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # Business logic, PDF generation
│   │   └── main.py        # App factory
│   └── requirements.txt
├── docs/
│   ├── external.docx      # Template for external petitions
│   └── internal.docx      # Template for internal petitions
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Local Development

### 1. Copy and fill environment variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

API will be available at: `http://localhost:8000`

### 3. Run without Docker

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

> ⚠️ Running without Docker requires LibreOffice to be installed locally for PDF generation.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/admin/petitions` | List all petitions (with filters) |
| `GET` | `/api/admin/petitions/{id}` | Get petition details |
| `POST` | `/api/admin/petitions/{id}/decision` | Approve or decline a petition |
| `POST` | `/api/admin/petitions/{id}/log-action` | Log a manual action |

## Deployment (Google Cloud Run)

### Prerequisites

- Google Cloud SDK installed and authenticated
- Docker installed
- A Google Cloud project with Cloud Run enabled

### Deploy

```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1
export SERVICE_NAME=admin-petitions-backend

# Build and push the image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=...,SUPABASE_KEY=...,ALLOWED_ORIGINS=https://your-admin-frontend.vercel.app
```

## Environment Variables

See `.env.example` for all required variables.

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (for admin ops) |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend URLs (e.g. `https://admin.vercel.app`) |
| `DOCX_TEMPLATE_PATH` | Path to the Word template file (default: `docs/external.docx`) |
| `TIMEZONE` | Timezone for date formatting (default: `Africa/Cairo`) |
