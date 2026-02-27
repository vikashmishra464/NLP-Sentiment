"""Monitoring utilities for model performance tracking."""
import mlflow
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelMonitor:
    """Monitor model performance and registry status."""
    
    def __init__(self, tracking_uri: str = "mlruns"):
        """Initialize monitor.
        
        Args:
            tracking_uri: MLflow tracking URI
        """
        mlflow.set_tracking_uri(tracking_uri)
        self.client = mlflow.MlflowClient()
    
    def get_all_model_versions(self, model_name: str) -> List[Dict]:
        """Get all versions of a registered model.
        
        Args:
            model_name: Name of the registered model
            
        Returns:
            List of model version information
        """
        try:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            
            version_info = []
            for version in versions:
                run = self.client.get_run(version.run_id)
                
                version_info.append({
                    "version": version.version,
                    "stage": version.current_stage,
                    "run_id": version.run_id,
                    "created_at": version.creation_timestamp,
                    "metrics": run.data.metrics,
                    "params": run.data.params
                })
            
            return sorted(version_info, key=lambda x: int(x["version"]), reverse=True)
            
        except Exception as e:
            logger.error(f"Error retrieving model versions: {e}")
            return []
    
    def get_production_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about the current production model.
        
        Args:
            model_name: Name of the registered model
            
        Returns:
            Production model information or None
        """
        try:
            production_versions = self.client.get_latest_versions(
                name=model_name,
                stages=["Production"]
            )
            
            if not production_versions:
                logger.warning("No production model found")
                return None
            
            version = production_versions[0]
            run = self.client.get_run(version.run_id)
            
            return {
                "version": version.version,
                "run_id": version.run_id,
                "created_at": datetime.fromtimestamp(version.creation_timestamp / 1000),
                "metrics": run.data.metrics,
                "params": run.data.params
            }
            
        except Exception as e:
            logger.error(f"Error retrieving production model: {e}")
            return None
    
    def compare_models(self, model_name: str, version1: int, version2: int) -> pd.DataFrame:
        """Compare two model versions.
        
        Args:
            model_name: Name of the registered model
            version1: First version number
            version2: Second version number
            
        Returns:
            DataFrame comparing the two versions
        """
        try:
            v1 = self.client.get_model_version(model_name, version1)
            v2 = self.client.get_model_version(model_name, version2)
            
            run1 = self.client.get_run(v1.run_id)
            run2 = self.client.get_run(v2.run_id)
            
            comparison = {
                "Metric": [],
                f"Version {version1}": [],
                f"Version {version2}": [],
                "Difference": []
            }
            
            # Compare metrics
            all_metrics = set(run1.data.metrics.keys()) | set(run2.data.metrics.keys())
            
            for metric in sorted(all_metrics):
                val1 = run1.data.metrics.get(metric, 0)
                val2 = run2.data.metrics.get(metric, 0)
                diff = val2 - val1
                
                comparison["Metric"].append(metric)
                comparison[f"Version {version1}"].append(f"{val1:.4f}")
                comparison[f"Version {version2}"].append(f"{val2:.4f}")
                comparison["Difference"].append(f"{diff:+.4f}")
            
            return pd.DataFrame(comparison)
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            return pd.DataFrame()
    
    def get_experiment_summary(self, experiment_name: str, top_n: int = 10) -> pd.DataFrame:
        """Get summary of top runs in an experiment.
        
        Args:
            experiment_name: Name of the experiment
            top_n: Number of top runs to return
            
        Returns:
            DataFrame with run summaries
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if not experiment:
                logger.error(f"Experiment '{experiment_name}' not found")
                return pd.DataFrame()
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["metrics.eval_f1 DESC"],
                max_results=top_n
            )
            
            # Select relevant columns
            columns = [
                "run_id",
                "start_time",
                "metrics.eval_f1",
                "metrics.eval_accuracy",
                "metrics.eval_precision",
                "metrics.eval_recall",
                "params.learning_rate",
                "params.batch_size"
            ]
            
            available_columns = [col for col in columns if col in runs.columns]
            
            return runs[available_columns]
            
        except Exception as e:
            logger.error(f"Error getting experiment summary: {e}")
            return pd.DataFrame()
    
    def print_model_registry_status(self, model_name: str):
        """Print formatted model registry status.
        
        Args:
            model_name: Name of the registered model
        """
        print("=" * 70)
        print(f"Model Registry Status: {model_name}")
        print("=" * 70)
        print()
        
        # Production model
        prod_info = self.get_production_model_info(model_name)
        if prod_info:
            print("PRODUCTION MODEL:")
            print(f"  Version: {prod_info['version']}")
            print(f"  Created: {prod_info['created_at']}")
            print(f"  Metrics:")
            for metric, value in prod_info['metrics'].items():
                print(f"    {metric}: {value:.4f}")
        else:
            print("PRODUCTION MODEL: None")
        
        print()
        print("-" * 70)
        print()
        
        # All versions
        versions = self.get_all_model_versions(model_name)
        if versions:
            print(f"ALL VERSIONS ({len(versions)} total):")
            print()
            for v in versions:
                print(f"  Version {v['version']} [{v['stage']}]")
                print(f"    F1: {v['metrics'].get('eval_f1', 0):.4f}")
                print(f"    Accuracy: {v['metrics'].get('eval_accuracy', 0):.4f}")
                print()
        else:
            print("No model versions found")
        
        print("=" * 70)


def main():
    """CLI for monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor model performance")
    parser.add_argument(
        "--model-name",
        type=str,
        default="sentiment-classifier",
        help="Name of the registered model"
    )
    parser.add_argument(
        "--action",
        type=str,
        choices=["status", "compare", "summary"],
        default="status",
        help="Action to perform"
    )
    parser.add_argument(
        "--version1",
        type=int,
        help="First version for comparison"
    )
    parser.add_argument(
        "--version2",
        type=int,
        help="Second version for comparison"
    )
    
    args = parser.parse_args()
    
    monitor = ModelMonitor()
    
    if args.action == "status":
        monitor.print_model_registry_status(args.model_name)
    
    elif args.action == "compare":
        if not args.version1 or not args.version2:
            print("Error: --version1 and --version2 required for comparison")
            return
        
        df = monitor.compare_models(args.model_name, args.version1, args.version2)
        print(df.to_string(index=False))
    
    elif args.action == "summary":
        df = monitor.get_experiment_summary("sentiment-analysis")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
