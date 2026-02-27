"""Example usage of the sentiment analysis pipeline."""
import requests
import json


def example_api_usage():
    """Demonstrate API usage."""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Sentiment Analysis API - Example Usage")
    print("=" * 60)
    print()
    
    # 1. Health check
    print("1. Health Check")
    print("-" * 60)
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # 2. Single prediction
    print("2. Single Prediction")
    print("-" * 60)
    text = "This movie was absolutely fantastic! I loved every minute of it."
    response = requests.post(
        f"{base_url}/predict",
        json={"text": text}
    )
    print(f"Input: {text}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # 3. Batch prediction
    print("3. Batch Prediction")
    print("-" * 60)
    texts = [
        "Great movie, highly recommended!",
        "Terrible waste of time.",
        "It was okay, nothing special."
    ]
    response = requests.post(
        f"{base_url}/batch_predict",
        json={"texts": texts}
    )
    print(f"Input: {len(texts)} texts")
    results = response.json()
    for i, result in enumerate(results, 1):
        print(f"\nText {i}: {result['text'][:50]}...")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Confidence: {result['confidence']:.4f}")
    print()
    
    print("=" * 60)


def example_mlflow_usage():
    """Demonstrate MLflow usage."""
    import mlflow
    from src.monitoring import ModelMonitor
    
    print("=" * 60)
    print("MLflow Model Registry - Example Usage")
    print("=" * 60)
    print()
    
    # Initialize monitor
    monitor = ModelMonitor()
    
    # Show model registry status
    monitor.print_model_registry_status("sentiment-classifier")


def example_training_workflow():
    """Demonstrate training workflow."""
    print("=" * 60)
    print("Training Workflow Example")
    print("=" * 60)
    print()
    
    print("Step 1: Train a new model")
    print("-" * 60)
    print("Command: python train.py --data-path NLP-Sentiment/data/aclImdb")
    print()
    print("This will:")
    print("  - Load and preprocess IMDB dataset")
    print("  - Train DistilBERT model")
    print("  - Log metrics to MLflow")
    print("  - Register model in Model Registry")
    print()
    
    print("Step 2: View results in MLflow UI")
    print("-" * 60)
    print("Command: mlflow ui")
    print("URL: http://localhost:5000")
    print()
    
    print("Step 3: Deploy with conditional logic")
    print("-" * 60)
    print("Command: python train.py --data-path NLP-Sentiment/data/aclImdb --deploy")
    print()
    print("This will:")
    print("  - Train the model")
    print("  - Compare F1 score with production baseline")
    print("  - Deploy ONLY if new_f1 >= baseline_f1")
    print()
    
    print("Step 4: Start API server")
    print("-" * 60)
    print("Command: uvicorn src.api:app --reload")
    print("URL: http://localhost:8000")
    print()
    
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "api":
            example_api_usage()
        elif sys.argv[1] == "mlflow":
            example_mlflow_usage()
        elif sys.argv[1] == "workflow":
            example_training_workflow()
        else:
            print("Usage: python example_usage.py [api|mlflow|workflow]")
    else:
        print("Available examples:")
        print("  python example_usage.py api       - API usage examples")
        print("  python example_usage.py mlflow    - MLflow usage examples")
        print("  python example_usage.py workflow  - Training workflow example")
