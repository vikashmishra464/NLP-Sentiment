"""MLOps pipeline with model registry and conditional deployment."""
import mlflow
import mlflow.pytorch
from pathlib import Path
from typing import Optional, Dict
import logging
import json
from datetime import datetime

from .config import config
from .data_loader import IMDBDataLoader
from .model import SentimentModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLOpsPipeline:
    """End-to-end MLOps pipeline for sentiment analysis."""
    
    def __init__(self):
        """Initialize pipeline."""
        self.config = config
        self.setup_mlflow()
        
    def setup_mlflow(self):
        """Setup MLflow tracking and model registry."""
        mlflow.set_tracking_uri(self.config.mlflow_tracking_uri)
        mlflow.set_experiment(self.config.mlflow_experiment_name)
        logger.info(f"MLflow tracking URI: {self.config.mlflow_tracking_uri}")
        logger.info(f"MLflow experiment: {self.config.mlflow_experiment_name}")
    
    def get_production_baseline_metrics(self) -> Optional[Dict[str, float]]:
        """Retrieve metrics from the current production model.
        
        Returns:
            Dictionary of metrics or None if no production model exists
        """
        try:
            client = mlflow.MlflowClient()
            
            # Get production model version
            production_versions = client.get_latest_versions(
                name=self.config.model_registry_name,
                stages=[self.config.production_stage]
            )
            
            if not production_versions:
                logger.warning("No production model found in registry")
                return None
            
            production_model = production_versions[0]
            run_id = production_model.run_id
            
            # Get metrics from the run
            run = client.get_run(run_id)
            metrics = run.data.metrics
            
            logger.info(f"Production model metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.warning(f"Could not retrieve production baseline: {e}")
            return None
    
    def compare_with_baseline(self, new_metrics: Dict[str, float]) -> bool:
        """Compare new model with production baseline.
        
        This is the MANDATORY LOGIC GATE for the assessment.
        
        Args:
            new_metrics: Metrics from the newly trained model
            
        Returns:
            True if new model should be deployed, False otherwise
        """
        baseline_metrics = self.get_production_baseline_metrics()
        
        # If no baseline exists, deploy if meets minimum threshold
        if baseline_metrics is None:
            logger.info("No baseline model found. Checking minimum threshold...")
            should_deploy = new_metrics.get("eval_f1", 0) >= self.config.min_f1_threshold
            
            if should_deploy:
                logger.info(f"✓ New model F1 ({new_metrics.get('eval_f1'):.4f}) "
                          f"meets minimum threshold ({self.config.min_f1_threshold})")
            else:
                logger.warning(f"✗ New model F1 ({new_metrics.get('eval_f1'):.4f}) "
                             f"below minimum threshold ({self.config.min_f1_threshold})")
            
            return should_deploy
        
        # Compare with baseline
        baseline_f1 = baseline_metrics.get("eval_f1", 0)
        new_f1 = new_metrics.get("eval_f1", 0)
        
        should_deploy = new_f1 >= baseline_f1
        
        if should_deploy:
            logger.info(f"✓ New model F1 ({new_f1:.4f}) >= Baseline F1 ({baseline_f1:.4f})")
            logger.info("DEPLOYMENT APPROVED: Proceeding to model registration")
        else:
            logger.warning(f"✗ New model F1 ({new_f1:.4f}) < Baseline F1 ({baseline_f1:.4f})")
            logger.warning("DEPLOYMENT REJECTED: Model does not beat baseline")
        
        return should_deploy
    
    def run_training_pipeline(
        self,
        data_path: Path,
        run_name: Optional[str] = None
    ) -> Dict[str, float]:
        """Run the complete training pipeline.
        
        Args:
            data_path: Path to IMDB dataset
            run_name: Optional name for the MLflow run
            
        Returns:
            Dictionary of evaluation metrics
        """
        if run_name is None:
            run_name = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with mlflow.start_run(run_name=run_name) as run:
            logger.info(f"Starting MLflow run: {run.info.run_id}")
            
            # Log parameters
            mlflow.log_params({
                "model_name": self.config.model.model_name,
                "batch_size": self.config.model.batch_size,
                "learning_rate": self.config.model.learning_rate,
                "num_epochs": self.config.model.num_epochs,
                "max_length": self.config.model.max_length,
            })
            
            # Step 1: Load and preprocess data
            logger.info("Step 1: Loading and preprocessing data...")
            data_loader = IMDBDataLoader(
                tokenizer_name=self.config.model.model_name,
                max_length=self.config.model.max_length
            )
            
            dataset = data_loader.load_from_files(data_path)
            tokenized_dataset = data_loader.tokenize_dataset(dataset)
            
            mlflow.log_param("train_samples", len(tokenized_dataset["train"]))
            mlflow.log_param("test_samples", len(tokenized_dataset["test"]))
            
            # Step 2: Initialize and train model
            logger.info("Step 2: Training model...")
            sentiment_model = SentimentModel(
                model_name=self.config.model.model_name,
                num_labels=self.config.model.num_labels
            )
            sentiment_model.load_model()
            
            output_dir = self.config.artifacts_dir / f"run_{run.info.run_id}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            sentiment_model.setup_trainer(
                train_dataset=tokenized_dataset["train"],
                eval_dataset=tokenized_dataset["test"],
                output_dir=str(output_dir),
                learning_rate=self.config.model.learning_rate,
                num_epochs=self.config.model.num_epochs,
                batch_size=self.config.model.batch_size,
                warmup_steps=self.config.model.warmup_steps,
                weight_decay=self.config.model.weight_decay
            )
            
            train_result = sentiment_model.train()
            
            # Step 3: Evaluate model
            logger.info("Step 3: Evaluating model...")
            eval_metrics = sentiment_model.evaluate(tokenized_dataset["test"])
            
            # Log metrics
            for key, value in eval_metrics.items():
                mlflow.log_metric(key, value)
            
            logger.info(f"Evaluation metrics: {eval_metrics}")
            
            # Step 4: Save model artifacts
            logger.info("Step 4: Saving model artifacts...")
            model_path = output_dir / "model"
            sentiment_model.save_model(str(model_path))
            
            # Log model to MLflow
            mlflow.pytorch.log_model(
                sentiment_model.model,
                "model",
                registered_model_name=self.config.model_registry_name
            )
            
            # Save metrics to file
            metrics_file = output_dir / "metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(eval_metrics, f, indent=2)
            mlflow.log_artifact(str(metrics_file))
            
            logger.info(f"Training pipeline completed. Run ID: {run.info.run_id}")
            
            return eval_metrics
    
    def conditional_deployment(
        self,
        metrics: Dict[str, float],
        model_version: Optional[int] = None
    ) -> bool:
        """Conditionally deploy model based on comparison with baseline.
        
        This implements the MANDATORY LOGIC GATE.
        
        Args:
            metrics: Metrics from the new model
            model_version: Specific model version to promote (if None, uses latest)
            
        Returns:
            True if deployment succeeded, False otherwise
        """
        logger.info("=" * 60)
        logger.info("CONDITIONAL DEPLOYMENT LOGIC GATE")
        logger.info("=" * 60)
        
        # Compare with baseline
        should_deploy = self.compare_with_baseline(metrics)
        
        if not should_deploy:
            logger.warning("Deployment blocked: Model does not meet criteria")
            return False
        
        # Promote to production
        try:
            client = mlflow.MlflowClient()
            
            # Get latest version if not specified
            if model_version is None:
                versions = client.search_model_versions(
                    f"name='{self.config.model_registry_name}'"
                )
                if not versions:
                    logger.error("No model versions found")
                    return False
                model_version = max([int(v.version) for v in versions])
            
            # Transition to production
            client.transition_model_version_stage(
                name=self.config.model_registry_name,
                version=model_version,
                stage=self.config.production_stage,
                archive_existing_versions=True
            )
            
            logger.info(f"✓ Model version {model_version} promoted to {self.config.production_stage}")
            logger.info("Deployment successful!")
            
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    def run_full_pipeline(self, data_path: Path) -> bool:
        """Run complete pipeline: train, evaluate, and conditionally deploy.
        
        Args:
            data_path: Path to IMDB dataset
            
        Returns:
            True if model was deployed, False otherwise
        """
        logger.info("Starting full MLOps pipeline...")
        
        # Train and evaluate
        metrics = self.run_training_pipeline(data_path)
        
        # Conditional deployment
        deployed = self.conditional_deployment(metrics)
        
        return deployed
