# Quick Reference Card

## 🚀 Essential Commands

### Training
```bash
# Basic training
python train.py --data-path NLP-Sentiment/data/aclImdb

# Train and deploy
python train.py --data-path NLP-Sentiment/data/aclImdb --deploy
```

### MLflow
```bash
# Start UI
mlflow ui

# Access at: http://localhost:5000
```

### API Server
```bash
# Development
uvicorn src.api:app --reload

# Production
uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up -d
```

### Monitoring
```bash
# Model status
python -m src.monitoring --action status

# Compare versions
python -m src.monitoring --action compare --version1 1 --version2 2
```

### Testing
```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📡 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Single Prediction
```bash
POST http://localhost:8000/predict
Content-Type: application/json

{
  "text": "Your text here"
}
```

### Batch Prediction
```bash
POST http://localhost:8000/batch_predict
Content-Type: application/json

{
  "texts": ["Text 1", "Text 2", "Text 3"]
}
```

---

## 🔧 Configuration

### Edit Model Settings
File: `src/config.py`

```python
class ModelConfig:
    model_name: str = "distilbert-base-uncased"
    batch_size: int = 16
    learning_rate: float = 2e-5
    num_epochs: int = 3
```

### Edit Deployment Threshold
```python
class PipelineConfig:
    min_f1_threshold: float = 0.85
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/mlops_pipeline.py` | Conditional deployment logic |
| `src/model.py` | Model wrapper |
| `src/api.py` | FastAPI endpoints |
| `src/config.py` | Configuration |
| `train.py` | Training script |
| `deploy.py` | Deployment script |

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
uvicorn src.api:app --port 8001

# Or kill process
lsof -ti:8000 | xargs kill -9  # Mac/Linux
```

### CUDA Out of Memory
```python
# Reduce batch size in src/config.py
batch_size: int = 8
```

### Model Not Found
```bash
# Train a model first
python train.py --data-path NLP-Sentiment/data/aclImdb
```

---

## 📊 Makefile Commands

```bash
make help          # Show all commands
make install       # Install dependencies
make train         # Train model
make deploy        # Deploy model
make api           # Start API
make mlflow-ui     # Start MLflow UI
make monitor       # Show model status
make test          # Run tests
make docker-up     # Start Docker
make full-pipeline # Train + deploy + API
```

---

## 🔍 Conditional Deployment Logic

**Location**: `src/mlops_pipeline.py` → `compare_with_baseline()`

**Logic**:
```
IF production_model exists:
    IF new_f1 >= baseline_f1:
        ✓ Deploy
    ELSE:
        ✗ Block
ELSE:
    IF new_f1 >= 0.85:
        ✓ Deploy
    ELSE:
        ✗ Block
```

---

## 📈 Expected Performance

| Metric | Value |
|--------|-------|
| Accuracy | 93-95% |
| F1-Score | 0.93-0.95 |
| Training Time | 30 min (GPU) |
| Inference Time | 50ms |

---

## 🔗 Documentation Links

- [README.md](README.md) - Overview
- [README_MLOPS.md](README_MLOPS.md) - Technical details
- [GETTING_STARTED.md](GETTING_STARTED.md) - Setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [REFLECTION.md](REFLECTION.md) - AI assistant experience
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete summary

---

## 💡 Quick Tips

1. **Always activate virtual environment first**
   ```bash
   source venv/bin/activate
   ```

2. **Check MLflow UI for all training runs**
   ```bash
   mlflow ui
   ```

3. **Use --deploy flag for conditional deployment**
   ```bash
   python train.py --deploy
   ```

4. **Monitor API health**
   ```bash
   curl http://localhost:8000/health
   ```

5. **View logs in Docker**
   ```bash
   docker-compose logs -f
   ```

---

## 🎯 Common Workflows

### First Time Setup
```bash
bash quickstart.sh
python train.py --data-path NLP-Sentiment/data/aclImdb
mlflow ui
```

### Development Cycle
```bash
# 1. Make changes to code
# 2. Train new model
python train.py --deploy

# 3. Check MLflow UI
mlflow ui

# 4. Test API
uvicorn src.api:app --reload
curl -X POST http://localhost:8000/predict -d '{"text":"test"}'
```

### Production Deployment
```bash
# 1. Train and validate
python train.py --deploy

# 2. Build Docker image
docker-compose build

# 3. Start containers
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health
```

---

## 📞 Need Help?

1. Check [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup
2. See [README_MLOPS.md](README_MLOPS.md) for technical details
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. Check logs: `docker-compose logs -f`
5. Run diagnostics: `pytest tests/ -v`

---

**Last Updated**: [Your Date]
**Version**: 2.0.0
