import os
from url_base import *
import regex as re

class UrlParser():
    def __init__ (self, file):
        try:
            with open(file, 'r') as f:
                self.model_asset_groups: list[ModelAssets] = self.extract_models(f)
        except IOError as e:
            print(f"Failed to open URL file: {e}")
            raise
        
    def extract_models(self, file) -> list[ModelAssets]:
        model_asset_group = []        
        for line in self.file:
            urls = line.strip('\n').split(',')
            model = Model(urls.pop() if self.validate_url(urls[-1]) else None)
            dataset = Dataset(urls.pop() if self.validate_url(urls[-1]) else None)
            codebase  = Codebase(urls.pop() if self.validate_url(urls[-1]) else None)
            model_asset_group.append(ModelAssets(model,dataset,codebase))
        return model_asset_group
    
    def validate_url(self, url) -> bool:
        url_pattern = re.compile(
            r'(?i)\b((?:https?://|[a-z0-9.\-]+[.][a-z]{2,4}/)'
            r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'
            r'(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
        )
        match = url_pattern.search(url)
        if match: return True
        else: return False


if __name__ == "__main__":
    parser = UrlParser(os.path.join(os.path.dirname(__file__), 'example.txt'))
    print([x.model.url for x in parser.model_asset_groups])
    print([x.dataset.url for x in parser.model_asset_groups])
    print([x.codebase.url for x in parser.model_asset_groups])