"""Configuration management for the sentiment analysis pipeline."""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Model configuration."""
    model_name: str = "distilbert-base-uncased"
    num_labels: int = 2
    max_length: int = 512
    batch_size: int = 16
    learning_rate: float = 2e-5
    num_epochs: int = 3
    warmup_steps: int = 500
    weight_decay: float = 0.01


class PipelineConfig(BaseModel):
    """Pipeline configuration."""
    # Paths
    data_dir: Path = Path("data")
    models_dir: Path = Path("models")
    artifacts_dir: Path = Path("artifacts")
    
    # MLflow
    mlflow_tracking_uri: str = "mlruns"
    mlflow_experiment_name: str = "sentiment-analysis"
    
    # Model Registry
    model_registry_name: str = "sentiment-classifier"
    production_stage: str = "Production"
    
    # Deployment threshold
    min_f1_threshold: float = 0.85  # Minimum F1 to beat baseline
    
    # Model config
    model: ModelConfig = ModelConfig()
    
    class Config:
        arbitrary_types_allowed = True


# Global config instance
config = PipelineConfig()
