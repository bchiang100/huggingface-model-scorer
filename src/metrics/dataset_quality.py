from parsing.url_base import *
from metrics.base import *
from contextlib import contextmanager
from datasets import load_dataset, get_dataset_config_names
from itertools import islice
import pandas as pd
import requests
import regex as re
import time
import logging

class DatasetQualityMetric(Metric):
    def calculate(self) -> float:
        '''
        Calculate implementation of the dataset quality metric
        A measure of quality associated with a dataset

        Judged by:
        - Size of dataset
        - % of missing or null values
        - Variety of features
        - Label consistency

        Fetches dataset from Hugging Face API, uses pandas to query and analyze the dataset

        Returns a float between 0 and 1, where 0 is low quality and 1 is high quality
        '''
        start_time = time.perf_counter()
        self._validate_input()
        r = self._analyze_dataset(self._fetch_dataset())
        self.latency = (time.perf_counter() - start_time) * 1000
        self.score = r
        logging.debug("Obtained dataset quality score")
        return r

    def _validate_input(self) -> bool:
        if self.asset_type != Dataset:
            raise ValueError("DatasetQualityMetric can only be applied to Dataset assets.")
        if 'huggingface.co' not in self.url:
            raise ValueError("DatasetQualityMetric can only be applied to Hugging Face datasets.")
        logging.debug("Input validated for dataset")
        return True

    def _fetch_dataset(self) -> pd.DataFrame:
        try:
                # Check available configs
            configs = get_dataset_config_names(f"{self.owner}/{self.asset_id}")
            if configs:
                # Prefer the requested config if available
                config_to_use = 'en' if 'en' in configs else configs[0]
                print(f"Using config: {config_to_use}")
                ds = load_dataset(f"{self.owner}/{self.asset_id}", config_to_use, split = "train", streaming=True)
            else:
                # No configs available
                print("No configs available, loading default dataset")
                ds = load_dataset(f"{self.owner}/{self.asset_id}", split = "train",streaming=True)
            logging.debug("Successfully loaded dataset")
        except Exception as e:
            logging.info("Failed to load dataset")
            raise RuntimeError(f"Failed to load dataset '{f"{self.owner}/{self.asset_id}"}': {e}")

        data_list = list(islice(ds, 10000))
        if not data_list:
            return pd.DataFrame
        df = pd.DataFrame.from_records(data_list)
        return df
    
    def _analyze_dataset(self, df: pd.DataFrame) -> float:
        '''
        Dataset size will have the highest weight of 0.35
        Missing values will have a weight of 0.25
        Variety of features will have a weight of 0.20
        Label consistency will have a weight of 0.20
        '''
        size_score = min(len(df) / 10000, 1.0) * 0.35           # Assuming 10,000 rows is excellent
        missing_score = (1 - df.isnull().mean().mean()) * 0.25  # Average missing value percentage
        variety_score = min(len(df.columns) / 50, 1.0) * 0.20   # Assuming 50 features is excellent
        label_score = self._label_consistency(df) * 0.20        # Custom function to evaluate label consistency
        total_score = size_score + missing_score + variety_score + label_score
        self.socore = total_score
        return total_score
    
    def _label_consistency(self, df: pd.DataFrame) -> float:
        '''
        read all column names, determine if their fields are consistently typed, determine if names follow a similar writing conveniton

        Returns a float between 0 and 1
        
        '''
        
        lc_score = 1.0
        print(df)
        label_columns = [col for col in df.columns]
        if not label_columns:
            return 0                    # no labels found
        
        for l in label_columns:
            if df[l].dtype == 'object': # objects are mixed columns
                types = dict()
                for x in df[l]:
                    types[type(x)] = types.get(type(x), 0) + 1
                if len(types) > 3:      # more than 3 types is bad
                    lc_score -= 0.3333 * (len(types) - 3) / len(types)
        
        naming_conventions = {
            'snake_case': re.compile(r'^[a-z]+(_[a-z]+)*$'),
            'camelCase': re.compile(r'^[a-z]+([A-Z][a-z]+)*$'),
            'PascalCase': re.compile(r'^[A-Z][a-z]+([A-Z][a-z]+)*$'),
            'kebab-case': re.compile(r'^[a-z]+(-[a-z]+)*$'),
            'UPPER_CASE': re.compile(r'^[A-Z]+(_[A-Z]+)*$')
        }

        conventions = dict()

        for l in label_columns:
            matched = False
            for name, pattern in naming_conventions.items():
                if pattern.match(l):
                    conventions[name] = conventions.get(name, 0) + 1
                    matched = True
                    break
            if not matched:
                conventions['other'] = conventions.get('other', 0) + 1
        
        if len(conventions) > 2:
            lc_score -= 0.3333 * (len(conventions) - 2) / len(conventions)

        if pct_msg := df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) > 0.35:
            lc_score -= 0.3333 * (pct_msg - 0.35) / 0.65                    # penalize if more than 35% missing values

        return max(lc_score, 0.0)
    
if __name__ == "__main__":
    d = Dataset("https://huggingface.co/datasets/xlangai/AgentNet")
    # d = Dataset("https://huggingface.co/datasets/allenai/c4")
    dq = DatasetQualityMetric(d)
    dq.calculate()
    print(dq.score)
    print(dq.latency)