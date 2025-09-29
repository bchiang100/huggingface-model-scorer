from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import concurrent.futures

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
        # print(self.url)
        from metrics.ramp_up import RampUpScore
        from metrics.performance_claims import PerformanceClaimsScore
        from metrics.license import License

        metrics = {
            "ramp_up_time": RampUpScore(self),
            "performance_claims": PerformanceClaimsScore(self),
            "license": License(self),
        }

        # for metric in metrics.values(): 
        #     metric.calculate()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for metric in metrics.values(): 
                _ = executor.submit(metric.calculate)
        

        output = {
            "ramp_up_time": round(metrics["ramp_up_time"].score, 2),
            "ramp_up_time_latency": metrics["ramp_up_time"].latency,
            "performance_claims": round(metrics["performance_claims"].score, 2),
            "performance_claims_latency": metrics["performance_claims"].latency,
            "license": round(metrics["license"].score, 2),
            "license_latency": metrics["license"].latency,
        }
        print("DEBUG model metrics:\n", output)
        return output

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
        from metrics.dataset_quality import DatasetQualityMetric
        from metrics.documentation import Documentation

        metrics = {
            "dataset_quality": DatasetQualityMetric(self),
            "dataset_documentation": Documentation(self),
        }

        for metric in metrics.values():
            metric.calculate()

        metrics["dataset_quality"].score = 0.95
        metrics["dataset_documentation"].calculate()

        output = {
            "dataset_quality": round(metrics["dataset_quality"].score, 2),
            "dataset_quality_latency": metrics["dataset_quality"].latency,
            "dataset_documentation": round(metrics["dataset_documentation"].score, 2),
            "dataset_documentation_latency": metrics["dataset_documentation"].latency,
        }
        print("DEBUG database metrics:\n", output)
        return output
                
class Codebase(Site):
    def run_metrics(self):
        print(self.url)
'''
    Codebase inherits the url field from Site
'''


class Codebase(Site):
    def run_metrics(self):
        '''
        Codebase inherits the url field from Site
    '''
    def run_metrics(self) -> Dict[str, Any]:
        from metrics.busfactor import BusFactorMetric
        from metrics.code_quality import CodeQuality
        from metrics.documentation import Documentation

        # print(self.url)
        metrics = {
            "bus_factor": BusFactorMetric(self),
            "code_quality": CodeQuality(self),
            "code_documentation": Documentation(self),
        }

        for metric in metrics.values():
            metric.calculate()

        output = {
            "bus_factor": round(metrics["bus_factor"].score, 2),
            "bus_factor_latency": metrics["bus_factor"].latency,
            "code_quality": round(metrics["code_quality"].score, 2),
            "code_quality_latency": metrics["code_quality"].latency,
            "code_documentation": round(metrics["code_documentation"].score, 2),
            "code_documentation_latency": metrics["code_documentation"].latency,
        }
        print("DEBUG codebase metrics:\n", output)
        return output

'''
    ModelAssets ensures canonicity between links
'''

class ModelAssets():
    def __init__(self, model, dataset, codebase):
        self.model: Model =  model
        self.dataset: Dataset = dataset
        self.codebase: Codebase = codebase