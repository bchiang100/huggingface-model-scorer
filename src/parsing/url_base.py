from abc import ABC, abstractmethod
from typing import Optional
from multiprocessing import Manager, managers
import urllib
import huggingface_hub as hfb
'''
Metric imports
'''
# from metrics.dataset_quality import DatasetQualityMetric
# from metrics.busfactor import BusFactorMetric
# from metrics.license import License
# from parallel import *

class Site(ABC):
    '''
        Base class for all assets (Model, Dataset, Codebase)
    '''
    def __init__ (self, url):
        self.url: str = url
        self.api_endpoint

    @property
    def api_endpoint(self):
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
        elif 'huggingface.co' in self.url:
            parsed_url = urllib.parse.urlparse(self.url)
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:
                owner, dataset = path_parts[1], path_parts[2]
                self.owner = owner
                self.asset_id = dataset
                return f"https://huggingface.co/api/datasets/{owner}/{dataset}"
            else:
                raise ValueError("Invalid Hugging Face Dataset URL format.")
        elif 'github.com' in self.url:
            parsed_url = urllib.parse.urlparse(self.url)
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2:
                owner, repo = path_parts[0], path_parts[1]
                self.owner = owner
                self.asset_id = repo
                return f"https://api.github.com/repos/{owner}/{repo}"
            else:
                raise ValueError("Invalid GitHub URL format.")
        else:
            raise ValueError("Unsupported asset type for API endpoint extraction.")
        
    @abstractmethod
    def run_metrics(self):
        pass

class Model(Site):
    '''
        Model inherits the url field from Site
    '''
    def run_metrics(self):
        print(self.url)

class Dataset(Site):
    '''
        Dataset inherits the url field from Site
        Dataset also has an internal property that automatically infers if a dataset is shared between a model asset group
    ''' 
    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url):
        if not new_url:
            new_url = self._infer_shared()
        self._url = new_url

    def run_metrics(self):
        # DatasetQualityMetric().calculate()
        pass

class Codebase(Site):
    '''
        Codebase inherits the url field from Site
    '''
    def run_metrics(self):
        print(self.url)

class Codebase(Site):
    def run_metrics(self):
        print(self.url)


class ModelAssets():
    '''
        ModelAssets ensures canonicity between links
    '''
    def __init__(self, model: Model, dataset: Dataset, codebase:Codebase, registry: managers.DictProxy):
        self.model: Model =  model
        self._dataset: Dataset = dataset
        self.codebase: Codebase = codebase
        self.registry: managers.DictProxy = registry

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self):
        if self._dataset.url != "" or self._dataset != None:
            return self._dataset
        else:
            return self._infer_shared_dataset(self._dataset)

    def _register_dataset(self):
        registry = self.registry
        if dataset := self.dataset.asset_id != "":
            registry[dataset] = 1
        else:
            registry[dataset] = None
        self.registry = registry

    def _infer_shared_dataset(self):
        '''
        First, read the huggingface api's metadata to determine the dataset, 
        if not found, attempt a to scan the readme for it
        '''

        api = hfb.HfApi()
        if dataset := api.dataset_info(repo_id = f"{self.dataset.owner}/{self.dataset.asset_id}"):
            return dataset
        else:
            return self._read_hf_readme()
        
    def _read_hf_metadat(self):
        '''
        Returns a URL or a None only
        '''
        pass
    
    def _read_hf_readme(self):
        '''
        Returns a URL or a None 
        '''
        pass