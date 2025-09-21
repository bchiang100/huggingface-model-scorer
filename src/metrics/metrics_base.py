from abc import ABC, abstractmethod
from parsing.url_base import *
import urllib.parse


class Metric(ABC):
    '''
    Metrics can expect that it will only run on Site objects (Model, Dataset, Codebase)

    Each metric must implement the abstract method calculate()  
    
    '''
    def __init__(self, asset):

        self.asset: Site = asset
        self.latency: float = 0.0
        self.score: float = 0.0
        self.owner: str = ""
        self.asset_id: str = ""

    @property
    def url(self):
        return self.asset.url

    @property
    def asset_type(self):
        return type(self.asset)
    
    @property
    def api_endpoint(self):
        if self.asset_type == Model:
            if 'huggingface.co' in self.url:
                parsed_url = urllib.parse.urlparse(self.url)
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    owner, model = path_parts[0], path_parts[1]
                    self.owner = owner
                    self.asset_id = model
                    return f"https://huggingface.co/api/models/{owner}/{model}"
                else:
                    raise ValueError("Invalid Hugging Face Model URL format.")
        elif self.asset_type == Dataset:
            if 'huggingface.co' in self.url:
                parsed_url = urllib.parse.urlparse(self.url)
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    owner, dataset = path_parts[0], path_parts[1]
                    self.owner = owner
                    self.asset_id = dataset
                    return f"https://huggingface.co/api/datasets/{owner}/{dataset}"
                else:
                    raise ValueError("Invalid Hugging Face Dataset URL format.")
        elif self.asset_type == Codebase:
            if 'github.com' in self.url:
                parsed_url = urllib.parse.urlparse(self.url)
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    owner, repo = path_parts[0], path_parts[1]
                    self.owner = owner
                    self.asset_id = repo
                    return f"https://api.github.com/repos/{owner}/{repo}"
                else:
                    raise ValueError("Invalid GitHub URL format.")
            elif 'huggingface.co' in self.url:
                pass
        else:
            raise ValueError("Unsupported asset type for API endpoint extraction.")

    @abstractmethod
    def calculate(self):
        '''
            Each subclass of metric must implement the calculation
        '''
        pass
