# Voice AI Backend - Flow Diagrams

## 1. Phone Call Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant T as Twilio
    participant D as Deepgram
    participant LLM as OpenAI
    participant KB as ChromaDB
    participant WS as WebSocket

    U->>API: POST /call/phone_call<br/>(assistant_id, phone_number)
    API->>T: Create call with webhook URL
    T->>U: Initiate phone call
    U->>T: Answer call & speak
    T->>WS: Stream audio to /call/stream
    WS->>D: Send audio for transcription
    D->>WS: Return transcribed text
    WS->>LLM: Send text + system prompt
    LLM->>KB: Query knowledge base
    KB->>LLM: Return relevant context
    LLM->>WS: Generate response
    WS->>D: Convert response to speech
    D->>WS: Return audio
    WS->>T: Send audio via media stream
    T->>U: Play audio response
    loop Conversation continues
        U->>T: Continue speaking
        T->>WS: Stream audio
        WS->>D: Transcribe
        D->>WS: Text
        WS->>LLM: Process with context
        LLM->>WS: Response
        WS->>D: TTS
        D->>WS: Audio
        WS->>T: Stream audio
        T->>U: Play response
    end
```

## 2. Web Call Flow Diagram

```mermaid
sequenceDiagram
    participant U as User Browser
    participant WS as WebSocket
    participant D as Deepgram
    participant LLM as OpenAI
    participant KB as ChromaDB

    U->>WS: Connect to /call/web_call<br/>(assistant_id)
    WS->>U: Send first message
    U->>WS: Stream audio via WebSocket
    WS->>D: Send audio for transcription
    D->>WS: Return transcribed text
    WS->>U: Send transcript
    WS->>LLM: Send text + system prompt
    LLM->>KB: Query knowledge base
    KB->>LLM: Return relevant context
    LLM->>WS: Generate response
    WS->>D: Convert response to speech
    D->>WS: Return audio
    WS->>U: Send audio response
    loop Conversation continues
        U->>WS: Continue streaming audio
        WS->>D: Transcribe
        D->>WS: Text
        WS->>U: Send transcript
        WS->>LLM: Process with context
        LLM->>WS: Response
        WS->>D: TTS
        D->>WS: Audio
        WS->>U: Send audio response
    end
```

## 3. Knowledge Base Processing Flow

```mermaid
flowchart TD
    A[User Uploads PDF] --> B[FastAPI Receives File]
    B --> C[Save to Temporary File]
    C --> D[PyPDFLoader Loads Document]
    D --> E[Extract Text Content]
    E --> F[RecursiveCharacterTextSplitter]
    F --> G[Split into 500-char Chunks<br/>with 100-char Overlap]
    G --> H[OpenAI Embeddings]
    H --> I[Vectorize Each Chunk]
    I --> J[Store in ChromaDB<br/>Assistant-specific Collection]
    J --> K[Return Success Response]
    
    style A fill:#e1f5fe
    style K fill:#c8e6c9
    style J fill:#fff3e0
```

## 4. Response Generation Flow

```mermaid
flowchart TD
    A[User Audio Input] --> B[Deepgram Transcription]
    B --> C[Extract Text]
    C --> D[Query ChromaDB<br/>Semantic Search]
    D --> E[Retrieve Relevant Context]
    E --> F[Combine: Context + User Text]
    F --> G[Add System Prompt]
    G --> H[Send to OpenAI LLM]
    H --> I[Generate Response]
    I --> J[Deepgram TTS]
    J --> K[Convert to Audio]
    K --> L[Send Audio Response]
    
    style A fill:#e1f5fe
    style L fill:#c8e6c9
    style D fill:#fff3e0
    style H fill:#f3e5f5
```

## 5. System Architecture Flow

```mermaid
graph TB
    subgraph "Client Layer"
        WC[Web Client]
        PC[Phone Client]
    end
    
    subgraph "API Gateway"
        API[FastAPI Application]
    end
    
    subgraph "Authentication"
        JWT[JWT Auth]
        USER[User Management]
    end
    
    subgraph "Core Services"
        ASS[Assistant Management]
        CALL[Call Processing]
        KB[Knowledge Base]
    end
    
    subgraph "External APIs"
        TW[Twilio API]
        DG[Deepgram API]
        OA[OpenAI API]
    end
    
    subgraph "Data Storage"
        PG[(PostgreSQL)]
        CD[(ChromaDB)]
    end
    
    WC --> API
    PC --> TW
    TW --> API
    
    API --> JWT
    API --> USER
    API --> ASS
    API --> CALL
    API --> KB
    
    CALL --> DG
    CALL --> OA
    ASS --> PG
    USER --> PG
    KB --> CD
    
    style API fill:#e3f2fd
    style DG fill:#fff3e0
    style OA fill:#f3e5f5
    style TW fill:#e8f5e8
```

## 6. Assistant Creation and Management Flow

```mermaid
flowchart TD
    A[User Login] --> B[Create Assistant]
    B --> C[Set Name & System Instructions]
    C --> D[Configure Voice Settings]
    D --> E[Set First Message]
    E --> F[Save to Database]
    F --> G[Assistant Ready]
    
    G --> H[Upload PDF Documents]
    H --> I[Process Documents]
    I --> J[Store in Vector DB]
    J --> K[Knowledge Base Ready]
    
    K --> L[Initiate Call]
    L --> M[Select Call Type]
    M --> N{Phone or Web?}
    N -->|Phone| O[Twilio Call Flow]
    N -->|Web| P[WebSocket Call Flow]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style K fill:#c8e6c9
    style O fill:#fff3e0
    style P fill:#fff3e0
```

## 7. Error Handling and Recovery Flow

```mermaid
flowchart TD
    A[System Operation] --> B{Operation Success?}
    B -->|Yes| C[Continue Processing]
    B -->|No| D[Log Error]
    D --> E{Error Type?}
    
    E -->|Network| F[Retry with Backoff]
    E -->|API Limit| G[Rate Limit Handling]
    E -->|Authentication| H[Re-authenticate]
    E -->|Database| I[Connection Reset]
    E -->|Audio| J[Audio Quality Check]
    
    F --> K{Retry Success?}
    G --> L[Wait & Retry]
    H --> M[Refresh Token]
    I --> N[Reconnect DB]
    J --> O[Adjust Audio Settings]
    
    K -->|Yes| C
    K -->|No| P[Fallback Response]
    L --> C
    M --> C
    N --> C
    O --> C
    P --> Q[Notify User]
    
    style A fill:#e1f5fe
    style C fill:#c8e6c9
    style P fill:#ffcdd2
    style Q fill:#ffcdd2
```

## 8. Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Sources"
        A1[Phone Audio]
        A2[Web Audio]
        A3[PDF Documents]
    end
    
    subgraph "Processing Layer"
        B1[Audio Processing]
        B2[Text Processing]
        B3[Vector Processing]
    end
    
    subgraph "AI Services"
        C1[Speech-to-Text]
        C2[Text-to-Speech]
        C3[LLM Processing]
        C4[Embedding Generation]
    end
    
    subgraph "Storage"
        D1[(PostgreSQL)]
        D2[(ChromaDB)]
    end
    
    subgraph "Output"
        E1[Phone Response]
        E2[Web Response]
        E3[API Responses]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B2
    
    B1 --> C1
    B2 --> C4
    C1 --> C3
    C3 --> C2
    
    C4 --> D2
    C3 --> D1
    
    C2 --> E1
    C2 --> E2
    D1 --> E3
    
    style A1 fill:#e1f5fe
    style A2 fill:#e1f5fe
    style A3 fill:#e1f5fe
    style E1 fill:#c8e6c9
    style E2 fill:#c8e6c9
    style E3 fill:#c8e6c9
```

These flow diagrams provide a comprehensive visual representation of how your Voice AI Backend system works, including:

1. **Phone Call Flow**: Complete sequence from call initiation to response
2. **Web Call Flow**: Real-time WebSocket-based communication
3. **Knowledge Base Processing**: PDF upload and vectorization process
4. **Response Generation**: AI processing pipeline
5. **System Architecture**: Overall system components and relationships
6. **Assistant Management**: Creation and configuration flow
7. **Error Handling**: Robust error management strategies
8. **Data Flow**: End-to-end data processing architecture

Each diagram uses different visual styles (sequence diagrams, flowcharts, and graphs) to best represent the different types of processes in your system. 