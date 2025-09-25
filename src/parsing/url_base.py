from abc import ABC, abstractmethod
from typing import Optional
from multiprocessing import Manager, managers
'''
Metric imports
'''
# from metrics.dataset_quality import DatasetQualityMetric
# from metrics.busfactor import BusFactorMetric
# from metrics.license import License

class Site(ABC):
    '''
        Base class for all assets (Model, Dataset, Codebase)
    '''
    def __init__ (self, url):
        self.url: str = url

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

        if dataset := self._read_hf_metadat():
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