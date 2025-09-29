from metrics.base import *
from parsing.url_base import Model
import numpy as np
import requests
import urllib.parse
import time
import logging

from dotenv import load_dotenv
load_dotenv()

class BusFactorMetric(Metric):
    def calculate(self) -> float:
        '''
        Calculate implementation of the bus factor metric
        A measure of risk associated by knowledge distribution of a codebase, model, or dataset

        Returns a float between 0 and 1, where 0 is low risk (many contributors) and 1 is high risk (few contributors)
        '''
        start_time = time.perf_counter()
        commit_map = self._get_commit_map()
        r = self._distribution_function(commit_map)
        self.latency = (time.perf_counter() - start_time) * 1000
        self.score = r
        return r

    def _get_commit_map(self) -> dict: 
        commits = dict()
        if self.asset_type == Model:
            pass
        elif self.asset_type == Dataset:
            pass
        elif self.asset_type == Codebase:
            for x in self._get_github_commits(self.api_endpoint + '/commits'):
                commits[x["commit"]["author"]["name"]] = commits.get(x["commit"]["author"]["name"], 0) + 1
        else:
            raise ValueError("Unsupported asset type for commit map extraction.")
        return commits if commits else None
    
    def _get_github_commits(self, url):
        '''
        Get the commits from a github repo using the github api
        '''
        commits = []
        for page in range(1, 4):
            r = requests.get(url, params={"per_page":100, "page":page})
            r.raise_for_status()
            data = r.json()
            if not data:
                break
            commits.extend(data)
        return commits
    
    def _get_huggingface_commits(self, url):
        '''
        Get the commits from a huggingface repo or dataset using the huggingface api
        '''
        pass

    def _distribution_function(self,commit_map: dict) -> float:
        '''
        Based on the shannon entropy of the commit distribution across authors.
        
        '''
        N = len(commit_map)
        H = 0
        H_max = np.log2(N)
        for x in commit_map.values():
            H -= x/N * np.log2(x/N)
        H_norm = H/H_max
        return H_norm

if __name__ == "__main__":
    m = Codebase("https://github.com/bchiang100/huggingface-model-scorer")
    bfm = BusFactorMetric(m)
    bfm.calculate()
    print(bfm.score)
    print(bfm.latency)
    # print(bfm.asset_type)