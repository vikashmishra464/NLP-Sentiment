"""Data loading and preprocessing utilities."""
import pandas as pd
from pathlib import Path
from typing import Tuple, List
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IMDBDataLoader:
    """Load and preprocess IMDB sentiment dataset."""
    
    def __init__(self, tokenizer_name: str, max_length: int = 512):
        """Initialize data loader.
        
        Args:
            tokenizer_name: Name of the tokenizer to use
            max_length: Maximum sequence length
        """
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length
    
    def load_from_files(self, data_path: Path) -> DatasetDict:
        """Load IMDB data from text files.
        
        Args:
            data_path: Path to IMDB dataset directory
            
        Returns:
            DatasetDict with train and test splits
        """
        logger.info(f"Loading data from {data_path}")
        
        # Load train data
        train_pos = list((data_path / "train" / "pos").glob("*.txt"))
        train_neg = list((data_path / "train" / "neg").glob("*.txt"))
        
        # Load test data
        test_pos = list((data_path / "test" / "pos").glob("*.txt"))
        test_neg = list((data_path / "test" / "neg").glob("*.txt"))
        
        # Create datasets
        train_texts, train_labels = self._read_files(train_pos, train_neg)
        test_texts, test_labels = self._read_files(test_pos, test_neg)
        
        # Create HuggingFace datasets
        train_dataset = Dataset.from_dict({
            "text": train_texts,
            "label": train_labels
        })
        
        test_dataset = Dataset.from_dict({
            "text": test_texts,
            "label": test_labels
        })
        
        dataset_dict = DatasetDict({
            "train": train_dataset,
            "test": test_dataset
        })
        
        logger.info(f"Loaded {len(train_dataset)} train and {len(test_dataset)} test samples")
        
        return dataset_dict
    
    def _read_files(self, pos_files: List[Path], neg_files: List[Path]) -> Tuple[List[str], List[int]]:
        """Read text files and create labels.
        
        Args:
            pos_files: List of positive review files
            neg_files: List of negative review files
            
        Returns:
            Tuple of (texts, labels)
        """
        texts = []
        labels = []
        
        # Read positive reviews
        for file_path in pos_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                texts.append(f.read())
                labels.append(1)
        
        # Read negative reviews
        for file_path in neg_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                texts.append(f.read())
                labels.append(0)
        
        return texts, labels
    
    def tokenize_dataset(self, dataset: DatasetDict) -> DatasetDict:
        """Tokenize the dataset.
        
        Args:
            dataset: Raw dataset
            
        Returns:
            Tokenized dataset
        """
        logger.info("Tokenizing dataset...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=self.max_length
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        
        return tokenized_dataset
