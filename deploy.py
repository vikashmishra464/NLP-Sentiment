"""Deployment script for promoting models to production."""
import argparse
import logging
from typing import Optional

from src.mlops_pipeline import MLOpsPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy sentiment analysis model")
    parser.add_argument(
        "--model-version",
        type=int,
        default=None,
        help="Specific model version to deploy (default: latest)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force deployment without baseline comparison"
    )
    
    args = parser.parse_args()
    
    pipeline = MLOpsPipeline()
    
    if args.force:
        logger.warning("Force deployment enabled - skipping baseline comparison")
        # Implement force deployment logic here if needed
        logger.info("Force deployment not yet implemented")
    else:
        # Get metrics from the specified version
        import mlflow
        client = mlflow.MlflowClient()
        
        if args.model_version:
            version = args.model_version
        else:
            # Get latest version
            versions = client.search_model_versions(
                f"name='{pipeline.config.model_registry_name}'"
            )
            if not versions:
                logger.error("No model versions found")
                return
            version = max([int(v.version) for v in versions])
        
        # Get run metrics
        model_version = client.get_model_version(
            name=pipeline.config.model_registry_name,
            version=version
        )
        run = client.get_run(model_version.run_id)
        metrics = run.data.metrics
        
        logger.info(f"Deploying model version {version} with metrics: {metrics}")
        
        # Conditional deployment
        deployed = pipeline.conditional_deployment(metrics, model_version=version)
        
        if deployed:
            logger.info("✓ Deployment successful")
        else:
            logger.warning("✗ Deployment blocked - model does not meet criteria")


if __name__ == "__main__":
    main()
