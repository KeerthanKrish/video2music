# video2music

A full-stack application that analyzes uploaded videos to generate mood-based music recommendations using AI/ML models.

## Architecture

- **Backend**: Python FastAPI with Supabase integration
- **Frontend**: React with TypeScript
- **Processing**: Supabase Edge Functions with LangGraph orchestration
- **Database**: Supabase (Postgres + Auth + Storage + Queues)
- **AI/ML**: Gemini 2.5 Pro, Whisper, YAMNet, ambient audio analysis

## Features

- User authentication via Supabase Auth
- Video upload with progress tracking
- Automated processing pipeline:
  - Frame extraction for scene analysis
  - Voice transcription using Whisper
  - Ambient audio tagging with YAMNet
  - Scene analysis with Gemini 2.5 Pro
  - Music recommendation reasoning
  - Music database querying
- Request history and status tracking
- Audio preview functionality

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase CLI
- FFmpeg

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Edge Function Setup

```bash
cd supabase/functions
supabase functions serve
```

## Project Structure

```
video2music/
├── app/                    # FastAPI backend
│   ├── models/            # Pydantic models
│   ├── routes/            # API routes
│   ├── services/          # Business logic
│   ├── auth.py           # JWT authentication
│   └── main.py           # FastAPI app
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
├── supabase/
│   ├── functions/        # Edge Functions
│   └── migrations/       # Database migrations
├── tests/                # Test files
├── requirements.txt      # Python dependencies
└── .env.example         # Environment template
```

## API Endpoints

- `POST /requests/` - Upload video and create processing request
- `GET /requests/` - Get user's request history
- `GET /requests/{id}` - Get specific request details

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
```

Type checking:
```bash
mypy app/
```
