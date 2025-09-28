from abc import ABC, abstractmethod
from typing import Optional
# Removed circular import - metrics modules should import from parsing, not vice versa
# from parallel import *

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
        Dataset also has an internal property that automatically infers if a dataset is shared betweena model asset group
    ''' 
    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url):
        if not new_url:
            new_url = self._infer_shared()
        self._url = new_url

    def _infer_shared(self):
        pass
        #return 

    def run_metrics(self):
        dataset_quality.DataSetQualityMetric(self).calculate()
                
class Codebase(Site):
    def run_metrics(self):
        print(self.url)
'''
    Codebase inherits the url field from Site
'''


class Codebase(Site):
    def run_metrics(self):
        print(self.url)

'''
    ModelAssets ensures canonicity between links
'''

class ModelAssets():
    def __init__(self, model, dataset, codebase):
        self.model: Model =  model
        self.dataset: Dataset = dataset
        self.codebase: Codebase = codebase