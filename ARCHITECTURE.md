# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MLOps Pipeline                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Training   │─────▶│  Evaluation  │─────▶│ Conditional  │
│   Pipeline   │      │   & Metrics  │      │  Deployment  │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                      │
       │                     │                      │
       ▼                     ▼                      ▼
┌──────────────────────────────────────────────────────────┐
│                    MLflow Tracking                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ Experiment │  │   Model    │  │  Artifact  │        │
│  │  Tracking  │  │  Registry  │  │  Storage   │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────────────────────────────────────┘
                          │
                          │
                          ▼
              ┌───────────────────────┐
              │  Production Model     │
              │  (Stage: Production)  │
              └───────────────────────┘
                          │
                          │
                          ▼
              ┌───────────────────────┐
              │     FastAPI Server    │
              │  ┌─────────────────┐  │
              │  │  /predict       │  │
              │  │  /batch_predict │  │
              │  │  /health        │  │
              │  └─────────────────┘  │
              └───────────────────────┘
                          │
                          │
                          ▼
              ┌───────────────────────┐
              │   Docker Container    │
              │   (Port 8000)         │
              └───────────────────────┘
```

## Component Details

### 1. Training Pipeline
**File**: `train.py`, `src/mlops_pipeline.py`

**Responsibilities**:
- Load and preprocess IMDB dataset
- Train DistilBERT model
- Log hyperparameters and metrics to MLflow
- Save model artifacts

**Key Features**:
- Hugging Face Transformers integration
- Automatic tokenization
- Early stopping
- GPU support

### 2. Evaluation & Metrics
**File**: `src/model.py`

**Metrics Tracked**:
- Accuracy
- Precision
- Recall
- F1-Score (primary metric)

**Evaluation Strategy**:
- Hold-out test set (25,000 samples)
- Per-epoch evaluation
- Best model selection based on F1

### 3. Conditional Deployment Logic
**File**: `src/mlops_pipeline.py` → `compare_with_baseline()`

**Decision Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Conditional Deployment Gate                │
└─────────────────────────────────────────────────────────┘

                    New Model Trained
                           │
                           ▼
              ┌────────────────────────┐
              │ Get Production Model   │
              │ Metrics from Registry  │
              └────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
    ┌───────────────────┐   ┌──────────────────┐
    │ Production Exists │   │ No Production    │
    └───────────────────┘   └──────────────────┘
                │                     │
                ▼                     ▼
    ┌───────────────────┐   ┌──────────────────┐
    │ Compare F1 Scores │   │ Check Minimum    │
    │ new_f1 >= base_f1?│   │ new_f1 >= 0.85?  │
    └───────────────────┘   └──────────────────┘
                │                     │
        ┌───────┴───────┐     ┌───────┴───────┐
        │               │     │               │
        ▼               ▼     ▼               ▼
    ┌─────┐        ┌─────┐ ┌─────┐      ┌─────┐
    │ YES │        │ NO  │ │ YES │      │ NO  │
    └─────┘        └─────┘ └─────┘      └─────┘
        │               │     │               │
        ▼               ▼     ▼               ▼
    ┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ DEPLOY  │   │ BLOCK   │ │ DEPLOY  │ │ BLOCK   │
    └─────────┘   └─────────┘ └─────────┘ └─────────┘
```

### 4. MLflow Integration
**Components**:

**Experiment Tracking**:
- Run ID, timestamps
- Hyperparameters (learning rate, batch size, etc.)
- Metrics (accuracy, F1, precision, recall)
- Training curves

**Model Registry**:
- Model versioning (v1, v2, v3, ...)
- Stage management (None → Staging → Production)
- Model metadata and lineage
- Artifact storage

**Artifact Storage**:
- Trained model weights
- Tokenizer configuration
- Training logs
- Metrics JSON

### 5. FastAPI Deployment
**File**: `src/api.py`

**Endpoints**:

```
GET /
├─ Returns: API information and available endpoints

GET /health
├─ Returns: Health status and model information
├─ Used by: Docker health checks, monitoring

POST /predict
├─ Input: {"text": "string"}
├─ Returns: {"sentiment": "positive/negative", "confidence": float}
├─ Used by: Single prediction requests

POST /batch_predict
├─ Input: {"texts": ["string1", "string2", ...]}
├─ Returns: [{"sentiment": "...", "confidence": ...}, ...]
├─ Used by: Batch processing
```

**Features**:
- Automatic production model loading
- Request validation with Pydantic
- Error handling and logging
- CORS support (configurable)

### 6. Docker Deployment
**Files**: `Dockerfile`, `docker-compose.yml`

**Container Structure**:
```
sentiment-api:latest
├─ Base: python:3.10-slim
├─ Working Dir: /app
├─ Exposed Port: 8000
├─ Health Check: curl /health every 30s
├─ Volumes:
│  └─ ./mlruns:/app/mlruns (read-only)
└─ Command: uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## Data Flow

### Training Flow
```
IMDB Dataset
    │
    ├─ train/ (25,000 reviews)
    │   ├─ pos/ (12,500 positive)
    │   └─ neg/ (12,500 negative)
    │
    └─ test/ (25,000 reviews)
        ├─ pos/ (12,500 positive)
        └─ neg/ (12,500 negative)
            │
            ▼
    ┌───────────────┐
    │ Data Loader   │
    │ - Tokenize    │
    │ - Pad/Truncate│
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ DistilBERT    │
    │ - Embedding   │
    │ - Transformer │
    │ - Classifier  │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ Training Loop │
    │ - 3 epochs    │
    │ - Early stop  │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ Evaluation    │
    │ - Test set    │
    │ - Metrics     │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ MLflow Log    │
    │ - Params      │
    │ - Metrics     │
    │ - Model       │
    └───────────────┘
```

### Inference Flow
```
Client Request
    │
    ▼
┌─────────────────┐
│ FastAPI         │
│ /predict        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Input Validation│
│ (Pydantic)      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Tokenization    │
│ (AutoTokenizer) │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Model Inference │
│ (DistilBERT)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Post-processing │
│ - Softmax       │
│ - Argmax        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Response        │
│ {sentiment,     │
│  confidence}    │
└─────────────────┘
```

## Technology Stack

### Core ML
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face library for DistilBERT
- **Datasets**: Data loading and preprocessing
- **scikit-learn**: Metrics and utilities

### MLOps
- **MLflow**: Experiment tracking and model registry
- **DVC**: Data version control (optional)

### API & Deployment
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

### Development
- **pytest**: Testing framework
- **GitHub Actions**: CI/CD
- **flake8**: Linting

## Scalability Considerations

### Current Implementation
- Single model serving
- Synchronous inference
- Local artifact storage
- Single container deployment

### Production Enhancements
1. **Horizontal Scaling**:
   - Multiple API containers behind load balancer
   - Kubernetes deployment with auto-scaling
   - Redis for request queuing

2. **Model Serving**:
   - TorchServe or TensorFlow Serving
   - Model batching for throughput
   - GPU acceleration

3. **Storage**:
   - S3/Azure Blob for artifacts
   - PostgreSQL for MLflow backend
   - Redis for caching

4. **Monitoring**:
   - Prometheus for metrics
   - Grafana for dashboards
   - ELK stack for logging

## Security Considerations

### Current Implementation
- Basic input validation
- Docker container isolation
- Read-only volume mounts

### Production Enhancements
1. **Authentication**: API key or OAuth2
2. **Rate Limiting**: Prevent abuse
3. **Input Sanitization**: XSS/injection prevention
4. **HTTPS**: TLS encryption
5. **Secrets Management**: Vault or AWS Secrets Manager
6. **Network Policies**: Kubernetes network policies

## Performance Metrics

### Model Performance
- **Accuracy**: 93-95%
- **F1-Score**: 0.93-0.95
- **Inference Latency**: ~50ms (CPU), ~10ms (GPU)
- **Throughput**: ~20 req/s (single container)

### Resource Usage
- **Memory**: ~2GB (model loaded)
- **CPU**: 1-2 cores
- **GPU**: Optional (4GB VRAM)
- **Disk**: ~1GB (model + artifacts)

## Monitoring & Observability

### Metrics to Track
1. **Model Metrics**:
   - Accuracy, F1, precision, recall
   - Prediction distribution
   - Confidence scores

2. **System Metrics**:
   - Request latency (p50, p95, p99)
   - Throughput (req/s)
   - Error rate
   - CPU/Memory usage

3. **Business Metrics**:
   - Prediction volume
   - User satisfaction
   - Model drift indicators

### Logging
- Structured JSON logs
- Request/response logging
- Error tracking
- Audit trail

## Disaster Recovery

### Backup Strategy
1. **Model Artifacts**: Daily backup to S3
2. **MLflow Database**: Continuous replication
3. **Configuration**: Version controlled in Git

### Rollback Procedure
1. Identify issue in production
2. Retrieve previous model version from registry
3. Transition previous version to Production stage
4. Restart API containers
5. Verify health checks
6. Monitor metrics

**Rollback Time**: < 5 minutes
