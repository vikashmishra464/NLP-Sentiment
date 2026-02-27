"""Model definition and training utilities."""
import torch
from transformers import (
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import numpy as np
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentModel:
    """Wrapper for sentiment classification model."""
    
    def __init__(self, model_name: str, num_labels: int = 2):
        """Initialize model.
        
        Args:
            model_name: Name of the pre-trained model
            num_labels: Number of classification labels
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.model = None
        self.trainer = None
    
    def load_model(self):
        """Load pre-trained model."""
        logger.info(f"Loading model: {self.model_name}")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )
        return self.model
    
    def setup_trainer(
        self,
        train_dataset,
        eval_dataset,
        output_dir: str,
        learning_rate: float = 2e-5,
        num_epochs: int = 3,
        batch_size: int = 16,
        warmup_steps: int = 500,
        weight_decay: float = 0.01
    ):
        """Setup Hugging Face Trainer.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset
            output_dir: Directory to save model checkpoints
            learning_rate: Learning rate
            num_epochs: Number of training epochs
            batch_size: Batch size
            warmup_steps: Number of warmup steps
            weight_decay: Weight decay
        """
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=warmup_steps,
            weight_decay=weight_decay,
            learning_rate=learning_rate,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            save_total_limit=2,
        )
        
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
        )
    
    @staticmethod
    def compute_metrics(eval_pred) -> Dict[str, float]:
        """Compute evaluation metrics.
        
        Args:
            eval_pred: Predictions and labels
            
        Returns:
            Dictionary of metrics
        """
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        
        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='binary'
        )
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    def train(self):
        """Train the model."""
        logger.info("Starting training...")
        train_result = self.trainer.train()
        return train_result
    
    def evaluate(self, dataset):
        """Evaluate the model.
        
        Args:
            dataset: Dataset to evaluate on
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating model...")
        metrics = self.trainer.evaluate(dataset)
        return metrics
    
    def save_model(self, path: str):
        """Save model to disk.
        
        Args:
            path: Path to save model
        """
        logger.info(f"Saving model to {path}")
        self.model.save_pretrained(path)
    
    def load_from_path(self, path: str):
        """Load model from disk.
        
        Args:
            path: Path to load model from
        """
        logger.info(f"Loading model from {path}")
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        return self.model
