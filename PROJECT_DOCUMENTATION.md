# Voice AI Backend - Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [API Endpoints](#api-endpoints)
6. [Database Schema](#database-schema)
7. [Call Flow](#call-flow)
8. [Knowledge Base Management](#knowledge-base-management)
9. [Deployment](#deployment)
10. [Development Setup](#development-setup)

## Project Overview

This is a sophisticated Voice AI Backend system built with FastAPI that enables real-time voice conversations with AI assistants. The system supports both web-based calls and phone calls via Twilio, with advanced features including:

- **AI Assistant Management**: Create, configure, and manage AI assistants with custom system prompts
- **Real-time Voice Processing**: Live transcription and speech synthesis using Deepgram
- **Knowledge Base Integration**: Upload PDF documents that are vectorized and used for context-aware responses
- **Multi-channel Support**: Web-based calls and phone calls via Twilio
- **Secure Authentication**: JWT-based user authentication and authorization

## Architecture

The system follows a microservices architecture with the following main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │   ChromaDB      │
│   (Container)   │◄──►│   (Container)   │    │   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twilio API    │    │   Deepgram API  │    │   OpenAI API    │
│   (Phone Calls) │    │ (Transcription) │    │   (LLM)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Architectural Features:
- **Containerized Deployment**: Docker containers for app and database
- **WebSocket Communication**: Real-time audio streaming and processing
- **Vector Database**: ChromaDB for storing and retrieving knowledge base embeddings
- **External API Integration**: Twilio, Deepgram, and OpenAI APIs

## Technology Stack

### Backend Framework
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization

### Database & Storage
- **PostgreSQL**: Primary relational database
- **ChromaDB**: Vector database for knowledge base storage
- **LangChain**: Framework for LLM integration and document processing

### External Services
- **Twilio**: Phone call management and media streaming
- **Deepgram**: Real-time speech-to-text and text-to-speech
- **OpenAI**: Large Language Model (GPT-4o-mini) for response generation

### Development Tools
- **Docker & Docker Compose**: Containerization and orchestration
- **Pytest**: Testing framework
- **Ruff**: Code linting and formatting
- **Pre-commit hooks**: Code quality automation

## System Components

### 1. Authentication System
- JWT-based authentication
- Password hashing with bcrypt
- User session management
- Protected API endpoints

### 2. Assistant Management
- CRUD operations for AI assistants
- Custom system prompts configuration
- Voice selection for speech synthesis
- User-specific assistant ownership

### 3. Call Processing Engine
- Real-time audio streaming via WebSocket
- Live transcription using Deepgram
- Context-aware response generation
- Speech synthesis and audio playback

### 4. Knowledge Base System
- PDF document upload and processing
- Document chunking and vectorization
- Semantic search for relevant context
- Assistant-specific knowledge collections

## API Endpoints

### Authentication
```
POST /api/v1/auth/login          # User login
POST /api/v1/auth/register       # User registration
```

### User Management
```
GET  /api/v1/user/me             # Get current user profile
PUT  /api/v1/user/me             # Update user profile
```

### Assistant Management
```
POST   /api/v1/assistant                    # Create new assistant
GET    /api/v1/assistant                    # Get all user assistants
GET    /api/v1/assistant/{assistant_id}     # Get specific assistant
PUT    /api/v1/assistant/{assistant_id}     # Update assistant
DELETE /api/v1/assistant/{assistant_id}     # Delete assistant
```

### Knowledge Base
```
POST /api/v1/assistant/{assistant_id}/upload_document    # Upload PDF
GET  /api/v1/assistant/{assistant_id}/knowledge_base     # List documents
```

### Call Management
```
POST      /api/v1/call/phone_call    # Initiate phone call
WebSocket /api/v1/call/stream        # Twilio media stream
WebSocket /api/v1/call/web_call      # Web-based call
```

## Database Schema

### User Model
```sql
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Assistant Model
```sql
CREATE TABLE assistant (
    id UUID PRIMARY KEY,
    name VARCHAR,
    system_instructions TEXT NOT NULL,
    first_message VARCHAR,
    voice VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES user(id) ON DELETE CASCADE
);
```

## Call Flow

### Phone Call Flow
1. **Call Initiation**: User calls `/api/v1/call/phone_call` with assistant ID and phone number
2. **Twilio Integration**: System creates Twilio call with webhook URL pointing to `/api/v1/call/stream`
3. **Media Streaming**: Twilio streams audio data to the webhook endpoint
4. **Real-time Processing**:
   - Audio data is sent to Deepgram for transcription
   - Transcribed text is processed by LLM with context from knowledge base
   - Response is converted to speech via Deepgram
   - Audio is sent back to Twilio for playback

### Web Call Flow
1. **WebSocket Connection**: Client connects to `/api/v1/call/web_call`
2. **Audio Streaming**: Browser streams audio directly to the server
3. **Processing Pipeline**: Same as phone call flow but with direct WebSocket communication

### Response Generation Process
```
User Audio → Deepgram Transcription → LLM Processing → Knowledge Base Context → Response Generation → Deepgram TTS → Audio Response
```

## Knowledge Base Management

### Document Processing Pipeline
1. **Upload**: PDF files uploaded via `/api/v1/assistant/{assistant_id}/upload_document`
2. **Processing**: 
   - Document loaded using PyPDFLoader
   - Text split into chunks using RecursiveCharacterTextSplitter
   - Chunks vectorized using OpenAI embeddings
   - Stored in ChromaDB with assistant-specific collection
3. **Retrieval**: During conversations, relevant chunks retrieved based on semantic similarity

### Vector Store Configuration
- **Chunk Size**: 500 characters with 100 character overlap
- **Embedding Model**: OpenAI text-embedding-ada-002
- **Search Strategy**: Similarity search with relevance scores
- **Collection Management**: Each assistant has its own ChromaDB collection

## Deployment

### Docker Setup
The application is containerized using Docker Compose with two main services:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5442:5432"

  app:
    build: .
    container_name: "app"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      POSTGRES_SERVER: "db"
    env_file: .env
    depends_on:
      - db
```

### Environment Variables
Required environment variables:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `DEEPGRAM_API_KEY`
- `OPENAI_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `NGROK_URL` (for Twilio webhooks)

## Development Setup

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- PostgreSQL (if running locally)

### Installation Steps
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd voice_ai_backend
   ```

2. **Environment Setup**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys and configuration
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Run Migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Access Application**
   - API Documentation: http://localhost:8000/docs
   - API Base URL: http://localhost:8000/api/v1

### Development Commands
```bash
# Run tests
docker-compose exec app pytest

# Code formatting
docker-compose exec app ruff format .

# Code linting
docker-compose exec app ruff check .

# Database migrations
docker-compose exec app alembic revision --autogenerate -m "description"
docker-compose exec app alembic upgrade head
```

## Key Features Summary

1. **Real-time Voice AI**: Live transcription and response generation
2. **Multi-channel Support**: Web and phone call capabilities
3. **Knowledge Base Integration**: PDF document processing and semantic search
4. **Scalable Architecture**: Containerized microservices design
5. **Secure Authentication**: JWT-based user management
6. **Developer Friendly**: Comprehensive API documentation and testing

This system provides a complete solution for building voice-enabled AI assistants with context-aware responses and multi-modal interaction capabilities. 