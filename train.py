"""Training script for sentiment analysis model."""
import argparse
from pathlib import Path
import logging

from src.mlops_pipeline import MLOpsPipeline
from src.config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train sentiment analysis model")
    parser.add_argument(
        "--data-path",
        type=str,
        default="NLP-Sentiment/data/aclImdb",
        help="Path to IMDB dataset"
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Name for the MLflow run"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Run full pipeline with conditional deployment"
    )
    
    args = parser.parse_args()
    
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"Data path does not exist: {data_path}")
        logger.info("Please download IMDB dataset from: https://ai.stanford.edu/~amaas/data/sentiment/")
        return
    
    # Initialize pipeline
    pipeline = MLOpsPipeline()
    
    if args.deploy:
        # Run full pipeline with conditional deployment
        logger.info("Running full pipeline with conditional deployment...")
        deployed = pipeline.run_full_pipeline(data_path)
        
        if deployed:
            logger.info("✓ Pipeline completed successfully - Model deployed to production")
        else:
            logger.warning("✗ Pipeline completed - Model NOT deployed (did not beat baseline)")
    else:
        # Just train and evaluate
        logger.info("Running training pipeline...")
        metrics = pipeline.run_training_pipeline(data_path, run_name=args.run_name)
        logger.info(f"Training completed. Metrics: {metrics}")
        logger.info("To deploy, run with --deploy flag")


if __name__ == "__main__":
    main()
