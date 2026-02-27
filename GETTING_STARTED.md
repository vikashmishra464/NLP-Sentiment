# Getting Started Guide

## Welcome! 👋

This guide will help you get the sentiment analysis MLOps pipeline up and running in under 10 minutes.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] pip package manager
- [ ] Git (for cloning the repository)
- [ ] 4GB+ free disk space
- [ ] (Optional) Docker for containerized deployment
- [ ] (Optional) GPU for faster training

---

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd sentiment-analysis-mlops
```

### 2. Download IMDB Dataset

The project requires the IMDB movie review dataset:

**Option A: Manual Download**
1. Visit: https://ai.stanford.edu/~amaas/data/sentiment/
2. Download `aclImdb_v1.tar.gz`
3. Extract to `NLP-Sentiment/data/aclImdb/`

**Option B: Command Line (Linux/Mac)**
```bash
cd NLP-Sentiment/data
wget https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz
tar -xzf aclImdb_v1.tar.gz
cd ../..
```

**Verify Dataset Structure**:
```
NLP-Sentiment/data/aclImdb/
├── train/
│   ├── pos/  (12,500 files)
│   └── neg/  (12,500 files)
└── test/
    ├── pos/  (12,500 files)
    └── neg/  (12,500 files)
```

### 3. Setup Python Environment

**Option A: Using the Quick Start Script (Recommended)**
```bash
bash quickstart.sh
```

**Option B: Manual Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list | grep -E "torch|transformers|mlflow|fastapi"

# Run tests
pytest tests/ -v
```

---

## Your First Training Run

### Train a Model

```bash
python train.py --data-path NLP-Sentiment/data/aclImdb
```

**What happens**:
1. Loads IMDB dataset (50,000 reviews)
2. Tokenizes text using DistilBERT tokenizer
3. Trains model for 3 epochs (~30 minutes on GPU, 2-3 hours on CPU)
4. Logs metrics to MLflow
5. Registers model in Model Registry

**Expected Output**:
```
Starting MLflow run: abc123...
Step 1: Loading and preprocessing data...
Step 2: Training model...
Epoch 1/3: 100%|████████| 1563/1563 [10:23<00:00]
Step 3: Evaluating model...
Evaluation metrics: {'eval_accuracy': 0.9456, 'eval_f1': 0.9451}
Training pipeline completed.
```

### View Results in MLflow UI

```bash
# Start MLflow UI
mlflow ui

# Open browser: http://localhost:5000
```

**What to look for**:
- Experiments tab: See all training runs
- Models tab: View registered models
- Compare runs: Select multiple runs to compare metrics

---

## Deploy Your Model

### Option 1: Conditional Deployment (Recommended)

```bash
python train.py --data-path NLP-Sentiment/data/aclImdb --deploy
```

**What happens**:
1. Trains new model
2. Compares F1-score with production baseline
3. **Deploys ONLY if new model is better**
4. Promotes to Production stage in registry

**Expected Output**:
```
CONDITIONAL DEPLOYMENT LOGIC GATE
✓ New model F1 (0.9451) >= Baseline F1 (0.8500)
DEPLOYMENT APPROVED: Proceeding to model registration
✓ Model version 1 promoted to Production
Deployment successful!
```

### Option 2: Manual Deployment

```bash
# Deploy specific version
python deploy.py --model-version 1
```

---

## Start the API Server

### Option 1: Direct (Development)

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker (Production)

```bash
# Build and start
docker-compose up --build

# Or use Makefile
make docker-up
```

**Verify API is running**:
```bash
curl http://localhost:8000/health
```

---

## Make Your First Prediction

### Using curl

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was absolutely fantastic! I loved every minute of it."}'
```

**Expected Response**:
```json
{
  "text": "This movie was absolutely fantastic! I loved every minute of it.",
  "sentiment": "positive",
  "confidence": 0.9876,
  "label": 1
}
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "This movie was terrible."}
)

print(response.json())
# {'sentiment': 'negative', 'confidence': 0.9654, 'label': 0}
```

### Batch Prediction

```bash
curl -X POST "http://localhost:8000/batch_predict" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great movie!",
      "Terrible film.",
      "It was okay."
    ]
  }'
```

---

## Common Commands

### Training & Deployment

```bash
# Train only
python train.py --data-path NLP-Sentiment/data/aclImdb

# Train and deploy
python train.py --data-path NLP-Sentiment/data/aclImdb --deploy

# Custom run name
python train.py --data-path NLP-Sentiment/data/aclImdb --run-name "experiment-1"
```

### MLflow

```bash
# Start UI
mlflow ui

# View specific experiment
mlflow ui --backend-store-uri mlruns --port 5000
```

### Monitoring

```bash
# View model registry status
python -m src.monitoring --action status

# Compare versions
python -m src.monitoring --action compare --version1 1 --version2 2

# View experiment summary
python -m src.monitoring --action summary
```

### API Server

```bash
# Development mode (auto-reload)
uvicorn src.api:app --reload

# Production mode
uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_api.py::test_health_endpoint -v
```

---

## Using the Makefile

The project includes a Makefile for convenience:

```bash
# View all commands
make help

# Install dependencies
make install

# Train model
make train

# Deploy model
make deploy

# Start API
make api

# Start MLflow UI
make mlflow-ui

# View model status
make monitor

# Run tests
make test

# Build Docker image
make docker-build

# Start Docker containers
make docker-up

# Full pipeline (train + deploy + api)
make full-pipeline
```

---

## Troubleshooting

### Issue: "No module named 'src'"

**Solution**: Ensure you're in the project root directory and virtual environment is activated.

```bash
# Check current directory
pwd  # Should show .../sentiment-analysis-mlops

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Issue: "IMDB dataset not found"

**Solution**: Download and extract the dataset to the correct location.

```bash
# Verify path exists
ls NLP-Sentiment/data/aclImdb/train/pos/  # Should show .txt files
```

### Issue: "CUDA out of memory"

**Solution**: Reduce batch size in `src/config.py`:

```python
class ModelConfig:
    batch_size: int = 8  # Reduce from 16
```

### Issue: "MLflow model not found"

**Solution**: Ensure you've trained at least one model:

```bash
# Train a model first
python train.py --data-path NLP-Sentiment/data/aclImdb

# Then start API
uvicorn src.api:app --reload
```

### Issue: "Port 8000 already in use"

**Solution**: Use a different port or kill the existing process:

```bash
# Use different port
uvicorn src.api:app --port 8001

# Or kill existing process (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Or kill existing process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Next Steps

### 1. Explore MLflow UI
- Compare different training runs
- View model lineage
- Analyze metrics and parameters

### 2. Experiment with Hyperparameters
Edit `src/config.py`:
```python
class ModelConfig:
    learning_rate: float = 3e-5  # Try different values
    num_epochs: int = 5          # More epochs
    batch_size: int = 32         # Larger batches
```

### 3. Test the Conditional Deployment
```bash
# First deployment
python train.py --deploy  # Should deploy (no baseline)

# Second deployment with worse model
# Edit config to use fewer epochs (worse performance)
python train.py --deploy  # Should block deployment
```

### 4. Integrate with Your Application
```python
import requests

def analyze_sentiment(text: str) -> dict:
    response = requests.post(
        "http://localhost:8000/predict",
        json={"text": text}
    )
    return response.json()

# Use in your app
result = analyze_sentiment("This product is amazing!")
print(f"Sentiment: {result['sentiment']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### 5. Deploy to Production
- Set up cloud infrastructure (AWS, GCP, Azure)
- Configure CI/CD pipeline (GitHub Actions included)
- Set up monitoring and alerting
- Implement A/B testing

---

## Learning Resources

### Documentation
- [README_MLOPS.md](README_MLOPS.md) - Technical documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [REFLECTION.md](REFLECTION.md) - AI assistant experience

### External Resources
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Docker Documentation](https://docs.docker.com/)

---

## Getting Help

### Check Logs
```bash
# API logs
docker-compose logs -f sentiment-api

# MLflow logs
cat mlruns/0/<run-id>/artifacts/logs/events.out.tfevents.*
```

### Run Diagnostics
```bash
# Check system info
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# Check MLflow
mlflow --version

# Check API health
curl http://localhost:8000/health
```

### Common Questions

**Q: How long does training take?**
A: ~30 minutes on GPU, 2-3 hours on CPU for 3 epochs.

**Q: Can I use a different model?**
A: Yes! Edit `src/config.py` and change `model_name` to any Hugging Face model (e.g., "bert-base-uncased").

**Q: How do I deploy to AWS/GCP/Azure?**
A: See [README_MLOPS.md](README_MLOPS.md) for cloud deployment guides.

**Q: Can I use this for other languages?**
A: Yes! Use a multilingual model like "bert-base-multilingual-cased".

---

## Success Checklist

You're ready to go when you can:

- [ ] Train a model successfully
- [ ] View results in MLflow UI
- [ ] Deploy with conditional logic
- [ ] Start the API server
- [ ] Make predictions via API
- [ ] Run tests successfully
- [ ] View model registry status

---

**Congratulations! You're all set up.** 🎉

For more details, see:
- [README.md](README.md) - Project overview
- [README_MLOPS.md](README_MLOPS.md) - Technical details
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

Happy coding! 🚀
