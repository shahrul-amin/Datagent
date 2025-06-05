import os
import pandas as pd
import json
from typing import Dict, Optional, List

class DatasetManager:
    def __init__(self, datasets_path: str = "datasets"):
        self.datasets_path = datasets_path
        self.current_dataset_path = None
        self.datasets_cache = {}
        
    def load_dataset(self, filename: str) -> Optional[pd.DataFrame]:
        """Load a dataset from the datasets folder."""
        filepath = os.path.join(self.datasets_path, filename)
        
        if not os.path.exists(filepath):
            return None
            
        try:
            if filepath not in self.datasets_cache:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                elif filename.endswith('.xlsx'):
                    df = pd.read_excel(filepath)
                elif filename.endswith('.json'):
                    df = pd.read_json(filepath)
                else:
                    return None
                    
                self.datasets_cache[filepath] = df
                
            self.current_dataset_path = filepath
            return self.datasets_cache[filepath]
            
        except Exception:
            return None
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available datasets in the datasets folder."""
        if not os.path.exists(self.datasets_path):
            return []
            
        datasets = []
        for filename in os.listdir(self.datasets_path):
            if filename.endswith(('.csv', '.xlsx', '.json')):
                datasets.append(filename)
                
        return datasets
    
    def get_current_dataset(self) -> Optional[pd.DataFrame]:
        """Get the currently loaded dataset."""
        if self.current_dataset_path and self.current_dataset_path in self.datasets_cache:
            return self.datasets_cache[self.current_dataset_path]
        return None
    
    def auto_detect_dataset(self) -> Optional[pd.DataFrame]:
        """Auto-detect and load the most recently modified dataset."""
        datasets = self.get_available_datasets()
        
        if not datasets:
            return None
            
        # Find the most recently modified dataset
        latest_file = None
        latest_time = 0
        
        for filename in datasets:
            filepath = os.path.join(self.datasets_path, filename)
            mod_time = os.path.getmtime(filepath)
            if mod_time > latest_time:
                latest_time = mod_time
                latest_file = filename
                
        if latest_file:
            return self.load_dataset(latest_file)
            
        return None
    
    def get_dataset_info(self, df: pd.DataFrame) -> Dict:
        """Get basic information about a dataset."""
        if df is None:
            return {}
            
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'head': df.head().to_dict('records'),
            'description': df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {}
        }
