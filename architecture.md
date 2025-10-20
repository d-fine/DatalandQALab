# Architecture Diagram

```mermaid
graph TB
    subgraph "Code Hosting"
        GH[GitHub<br/>d-fine/DatalandQALab]
    end

    subgraph "CI/CD - GitHub Actions"
        CI[CI Pipeline<br/>Tests, Linting, Coverage]
        CD[CD Pipeline<br/>Docker Build & Deploy]
        GHCR[GitHub Container Registry<br/>ghcr.io]
    end

    subgraph "Deployment - Ubuntu Server"
        APP[QA Lab Server<br/>FastAPI + Uvicorn<br/>Port 5051]
        PG[PostgreSQL 17.2<br/>Port 5432]
        PGA[pgAdmin<br/>Port 5050]
        SCH[Background Scheduler<br/>APScheduler - 10min cron]
    end

    subgraph "External APIs"
        DL[Dataland API]
        AZ1[Azure OpenAI<br/>GPT-4]
        AZ2[Azure Document Intelligence]
        SLACK[Slack Webhooks]
    end

    subgraph "Tech Stack"
        FW[Python 3.12<br/>FastAPI, SQLAlchemy<br/>PDM, Ruff, Pytest]
    end

    GH -->|Push| CI
    CI -->|Pass| CD
    CD -->|Build & Push Images| GHCR
    CD -->|SSH Deploy| APP

    APP --> PG
    APP --> PGA
    SCH -.->|Scheduled Jobs| APP

    APP <-->|REST API| DL
    APP <-->|LLM Queries| AZ1
    APP <-->|Document Processing| AZ2
    APP -->|Alerts| SLACK

    style GH fill:#f9f,stroke:#333
    style APP fill:#bbf,stroke:#333
    style AZ1 fill:#0078d4,stroke:#333,color:#fff
    style AZ2 fill:#0078d4,stroke:#333,color:#fff
```

## Key Architecture Components

### Code Hosting
- **GitHub Repository**: d-fine/DatalandQALab

### Deployment
- **Platform**: Ubuntu server
- **Deployment Method**: SSH-based deployment via GitHub Actions
- **Container Orchestration**: Docker Compose
- **Container Registry**: GitHub Container Registry (ghcr.io)

### Application Stack
- **Framework**: FastAPI with Uvicorn (Python 3.12)
- **Database**: PostgreSQL 17.2
- **Database Management**: pgAdmin
- **Package Manager**: PDM
- **Linting/Formatting**: Ruff
- **Testing**: Pytest with coverage
- **Scheduler**: APScheduler (runs every 10 minutes)

### External APIs
- **Dataland API**: Primary data source for quality assurance
- **Azure OpenAI**: GPT-4 for automated review generation
- **Azure Document Intelligence**: Document processing and analysis
- **Slack**: Alerting and notifications

### CI/CD Pipeline
- **CI**: Automated testing, linting, formatting checks, and SonarCloud analysis
- **CD**: Docker image build and push to GHCR, followed by SSH deployment to production server

### Ports
- **5051**: QA Lab Server API
- **5432**: PostgreSQL Database
- **5050**: pgAdmin Web Interface

---

## Dataset Review Flow

```mermaid
flowchart TD
    Start([Trigger]) --> Sched{Trigger Type}
    Sched -->|Scheduled<br/>Every 10min| Fetch[Fetch Unreviewed<br/>Datasets from Dataland API]
    Sched -->|Manual<br/>API Call| GetDS[Get Dataset by ID]

    Fetch --> Loop{Any<br/>Datasets?}
    Loop -->|Yes| GetDS
    Loop -->|No| End([End])

    GetDS --> Check{Already<br/>Reviewed?}
    Check -->|Yes| Return[Return Existing Report ID]
    Check -->|No| DB[(Save to PostgreSQL<br/>review_start_time)]

    DB --> Extract[Extract Page Numbers<br/>from Data Sources]
    Extract --> PDF[Fetch & Extract<br/>Relevant PDF Pages]

    PDF --> DocInt[Azure Document Intelligence<br/>Convert PDF to Markdown]
    DocInt --> Gen[Generate QA Report]

    Gen --> YN[Yes/No Questions<br/>via Azure OpenAI]
    Gen --> Num[Numeric Values<br/>via Azure OpenAI]
    Gen --> Denom[Denominator Report<br/>via Azure OpenAI]
    Gen --> Numer[Numerator Report<br/>via Azure OpenAI]
    Gen --> Elig[Eligible/Non-Eligible<br/>via Azure OpenAI]

    YN --> Assemble[Assemble Complete Report]
    Num --> Assemble
    Denom --> Assemble
    Numer --> Assemble
    Elig --> Assemble

    Assemble --> Post[Post Report to<br/>Dataland QA API]
    Post --> Update[(Update PostgreSQL<br/>review_end_time<br/>report_id)]

    Update --> Notify[Send Slack Alert<br/>Success ✅]
    Notify --> Return
    Return --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style DB fill:#87CEEB
    style Update fill:#87CEEB
    style DocInt fill:#0078d4,color:#fff
    style YN fill:#0078d4,color:#fff
    style Num fill:#0078d4,color:#fff
    style Denom fill:#0078d4,color:#fff
    style Numer fill:#0078d4,color:#fff
    style Elig fill:#0078d4,color:#fff
    style Notify fill:#8B008B,color:#fff
```

### Review Process Steps

1. **Trigger**: Either scheduled (every 10 minutes) or manual API call to `/review/{data_id}`
2. **Fetch Dataset**: Retrieve unreviewed datasets or specific dataset by ID from Dataland API
3. **Check Database**: Verify if dataset already has a review to avoid duplicate processing
4. **Extract Pages**: Identify relevant pages from data source references
5. **Process Document**: Convert PDF pages to markdown using Azure Document Intelligence
6. **Generate Reports**: Use Azure OpenAI (GPT-4) to generate QA reports for:
   - Yes/No questions
   - Numeric values
   - Taxonomy-aligned denominator
   - Taxonomy-aligned numerator
   - Eligible/Non-eligible classifications
7. **Post Report**: Submit complete QA report back to Dataland API
8. **Update & Notify**: Update database and send Slack notification
