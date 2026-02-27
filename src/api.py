"""FastAPI deployment wrapper for sentiment analysis model."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import mlflow
import mlflow.pytorch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging
from pathlib import Path

from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="Production-ready sentiment analysis using transformer models",
    version="2.0.0"
)

# Global model and tokenizer
model = None
tokenizer = None


class PredictionRequest(BaseModel):
    """Request model for sentiment prediction."""
    text: str = Field(..., description="Text to analyze", min_length=1)


class BatchPredictionRequest(BaseModel):
    """Request model for batch sentiment prediction."""
    texts: List[str] = Field(..., description="List of texts to analyze", min_items=1)


class PredictionResponse(BaseModel):
    """Response model for sentiment prediction."""
    text: str
    sentiment: str
    confidence: float
    label: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    model_name: str


def load_production_model():
    """Load the production model from MLflow registry."""
    global model, tokenizer
    
    try:
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        client = mlflow.MlflowClient()
        
        # Get production model
        production_versions = client.get_latest_versions(
            name=config.model_registry_name,
            stages=[config.production_stage]
        )
        
        if not production_versions:
            logger.error("No production model found")
            return False
        
        production_model = production_versions[0]
        model_uri = f"models:/{config.model_registry_name}/{config.production_stage}"
        
        logger.info(f"Loading model from: {model_uri}")
        
        # Load model
        model = mlflow.pytorch.load_model(model_uri)
        model.eval()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(config.model.model_name)
        
        logger.info("Model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    logger.info("Starting API server...")
    success = load_production_model()
    if not success:
        logger.warning("Failed to load production model. API will return errors.")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Sentiment Analysis API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/batch_predict"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_name=config.model.model_name
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict sentiment for a single text.
    
    Args:
        request: Prediction request with text
        
    Returns:
        Prediction response with sentiment and confidence
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Tokenize input
        inputs = tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            max_length=config.model.max_length,
            padding=True
        )
        
        # Get prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][predicted_class].item()
        
        sentiment = "positive" if predicted_class == 1 else "negative"
        
        return PredictionResponse(
            text=request.text,
            sentiment=sentiment,
            confidence=confidence,
            label=predicted_class
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/batch_predict", response_model=List[PredictionResponse])
async def batch_predict(request: BatchPredictionRequest):
    """Predict sentiment for multiple texts.
    
    Args:
        request: Batch prediction request with list of texts
        
    Returns:
        List of prediction responses
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        results = []
        
        for text in request.texts:
            # Tokenize input
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=config.model.max_length,
                padding=True
            )
            
            # Get prediction
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probs, dim=-1).item()
                confidence = probs[0][predicted_class].item()
            
            sentiment = "positive" if predicted_class == 1 else "negative"
            
            results.append(PredictionResponse(
                text=text,
                sentiment=sentiment,
                confidence=confidence,
                label=predicted_class
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
