# Sentiment Analysis MLOps Pipeline

## TechsaraConsultancy Assessment Submission

This project extends an open-source sentiment analysis system with modern MLOps practices, including automated model versioning, conditional deployment logic, and production-ready API deployment.

---

## What Was Implemented and Why

### 1. Model Improvement: Transformer-Based Architecture
**What:** Replaced the original RNN/CNN models with DistilBERT, a state-of-the-art transformer model.

**Why:** 
- The original baseline RNN achieved ~85% accuracy with significant training instability
- DistilBERT provides 92-95% accuracy out-of-the-box with transfer learning
- Faster inference time compared to full BERT while maintaining performance
- Better handling of long-range dependencies in text

### 2. MLOps Lifecycle Automation
**What:** Implemented a complete MLOps pipeline using MLflow for experiment tracking and model registry.

**Components:**
- **Experiment Tracking**: All training runs logged with hyperparameters, metrics, and artifacts
- **Model Registry**: Centralized model versioning with stage transitions (Staging → Production)
- **Artifact Management**: Automatic logging of models, metrics, and training outputs

**Why:** Enables reproducibility, model lineage tracking, and systematic comparison of experiments.

### 3. Conditional Deployment Logic (MANDATORY REQUIREMENT)
**What:** Implemented a logic gate that compares new model F1-score against the production baseline.

**Logic Flow:**
```
IF production_model exists:
    IF new_f1 >= baseline_f1:
        ✓ Deploy to production
    ELSE:
        ✗ Block deployment
ELSE:
    IF new_f1 >= minimum_threshold (0.85):
        ✓ Deploy to production
    ELSE:
        ✗ Block deployment
```

**Implementation:** See `src/mlops_pipeline.py` → `compare_with_baseline()` and `conditional_deployment()`

**Why:** Prevents model degradation in production by ensuring only improvements are deployed.

### 4. Production-Ready API Deployment
**What:** FastAPI wrapper with Docker containerization for model serving.

**Features:**
- RESTful endpoints for single and batch predictions
- Health check endpoint for monitoring
- Automatic loading of production model from registry
- Request validation with Pydantic
- Docker Compose for easy deployment

**Why:** Provides a production-grade interface for model consumption with proper error handling and observability.

### 5. Modular Code Structure
**What:** Refactored notebook code into a proper Python package structure.

**Structure:**
```
src/
├── __init__.py
├── config.py          # Configuration management
├── data_loader.py     # Data preprocessing
├── model.py           # Model definition
├── mlops_pipeline.py  # MLOps orchestration
└── api.py             # FastAPI deployment

train.py               # Training script
deploy.py              # Deployment script
tests/                 # Unit tests
```

**Why:** Improves maintainability, testability, and enables CI/CD integration.

---

## How to Run

### Prerequisites
```bash
# Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Download IMDB Dataset
```bash
# Download from: https://ai.stanford.edu/~amaas/data/sentiment/
# Extract to: NLP-Sentiment/data/aclImdb/
```

### 1. Train Model (Without Deployment)
```bash
python train.py --data-path NLP-Sentiment/data/aclImdb
```

This will:
- Train a DistilBERT model on IMDB dataset
- Log metrics and artifacts to MLflow
- Register model in MLflow Model Registry
- NOT deploy to production

### 2. Train and Deploy (With Conditional Logic)
```bash
python train.py --data-path NLP-Sentiment/data/aclImdb --deploy
```

This will:
- Train the model
- Compare with production baseline
- **Only deploy if F1 >= baseline F1** (CONDITIONAL LOGIC GATE)
- Promote to production if criteria met

### 3. Deploy Specific Model Version
```bash
python deploy.py --model-version 2
```

### 4. View MLflow UI
```bash
mlflow ui --backend-store-uri mlruns
# Open: http://localhost:5000
```

### 5. Start API Server
```bash
# Option 1: Direct
uvicorn src.api:app --host 0.0.0.0 --port 8000

# Option 2: Docker
docker-compose up --build

# Test API
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was absolutely fantastic!"}'
```

### 6. Run Tests
```bash
pytest tests/ -v
```

---

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── data_loader.py         # Data loading and preprocessing
│   ├── model.py               # Model wrapper
│   ├── mlops_pipeline.py      # MLOps orchestration (CONDITIONAL LOGIC HERE)
│   └── api.py                 # FastAPI deployment
├── tests/
│   ├── __init__.py
│   └── test_api.py            # API tests
├── train.py                   # Training script
├── deploy.py                  # Deployment script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-container orchestration
├── .gitignore
├── .dockerignore
├── README_MLOPS.md           # This file
└── REFLECTION.md             # Coding assistant reflection

# Original project files
├── NLP-Sentiment/
│   ├── data/
│   ├── notebooks/
│   ├── models/
│   └── README.md
```

---

## Key Features

### 1. Experiment Tracking
- All training runs logged to MLflow
- Hyperparameters, metrics, and artifacts tracked
- Easy comparison of model versions

### 2. Model Registry
- Centralized model versioning
- Stage-based promotion (None → Staging → Production)
- Model lineage and metadata

### 3. Conditional Deployment (MANDATORY LOGIC)
- Automatic comparison with production baseline
- F1-score based decision making
- Prevents model degradation

### 4. API Deployment
- RESTful API with FastAPI
- Docker containerization
- Health checks and monitoring
- Batch prediction support

### 5. Reproducibility
- Pinned dependencies
- Configuration management
- Seed setting for deterministic training

---

## Assumptions and Limitations

### Assumptions
1. **Dataset Availability**: IMDB dataset is downloaded and available at specified path
2. **Compute Resources**: Training requires GPU for reasonable speed (CPU works but slower)
3. **MLflow Storage**: Local file system used for MLflow tracking (can be configured for remote)
4. **Production Metric**: F1-score chosen as primary metric for deployment decision

### Limitations
1. **Single Dataset**: Currently configured for IMDB binary sentiment only
2. **No A/B Testing**: Deployment is immediate; no gradual rollout
3. **Limited Monitoring**: No production inference monitoring or drift detection
4. **Local Storage**: MLflow artifacts stored locally (should use S3/Azure Blob in production)
5. **No CI/CD**: Manual execution required (should integrate with GitHub Actions/Jenkins)

### Future Improvements
- Add data drift detection
- Implement A/B testing framework
- Add production inference monitoring
- Integrate with cloud storage (S3, GCS)
- Add automated retraining triggers
- Implement shadow deployment mode
- Add model explainability endpoints (SHAP/LIME)

---

## Metrics Comparison

### Original Models (from README)
- **Baseline RNN**: ~85% accuracy, unstable training
- **AvgNet**: ~92% accuracy
- **CNet**: ~92% accuracy

### New Model (DistilBERT)
- **Expected Performance**: 93-95% accuracy, 0.93-0.95 F1-score
- **Training Time**: ~30 minutes on GPU (3 epochs)
- **Inference Speed**: ~50ms per sample

---

## API Endpoints

### Health Check
```bash
GET /health
```

### Single Prediction
```bash
POST /predict
{
  "text": "This movie was great!"
}
```

### Batch Prediction
```bash
POST /batch_predict
{
  "texts": ["Great movie!", "Terrible film."]
}
```

---

## Conditional Deployment Logic Details

The conditional deployment logic is implemented in `src/mlops_pipeline.py`:

```python
def compare_with_baseline(self, new_metrics: Dict[str, float]) -> bool:
    """
    MANDATORY LOGIC GATE
    
    Compares new model F1-score with production baseline.
    Returns True only if new_f1 >= baseline_f1
    """
    baseline_metrics = self.get_production_baseline_metrics()
    
    if baseline_metrics is None:
        # No baseline exists - check minimum threshold
        return new_metrics.get("eval_f1", 0) >= self.config.min_f1_threshold
    
    # Compare with baseline
    baseline_f1 = baseline_metrics.get("eval_f1", 0)
    new_f1 = new_metrics.get("eval_f1", 0)
    
    return new_f1 >= baseline_f1  # GATE CONDITION
```

**Execution Flow:**
1. Train new model → Get F1 score
2. Retrieve production model F1 from registry
3. Compare: `new_f1 >= baseline_f1`
4. If True → Promote to production
5. If False → Block deployment, log warning

---

## Contact & Support

For questions or issues, please refer to the original project:
- Original Project: [NLP-Sentiment](https://github.com/[original-repo])
- MLOps Extension: This fork

---

## License

This project extends an open-source sentiment analysis project. Please refer to the original project's license.
