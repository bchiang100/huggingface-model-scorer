import os
import regex as re

class UrlParser():
    def __init__ (self, file):
        try:
            self.file = open(file, 'r')
        except IOError as e:
            print(f"Failed to open URL file: {e}")
            raise
        self.urls = self.extract_urls()
        self.units = self.categorize_urls()
        
    def extract_urls(self) -> list[str]:
        urls = []
        url_pattern = re.compile(
            r'(?i)\b((?:https?://|[a-z0-9.\-]+[.][a-z]{2,4}/)'
            r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'
            r'(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
        )
        
        for line in self.file:
            match = url_pattern.findall(line)
            for m in match:
                urls.append(m[0])
        self.file.close()
        return urls
    
    def categorize_urls(self) -> list[set]:
        units = []
        model_pattern = re.compile(r"https://huggingface\.co", re.IGNORECASE)
        dataset_pattern = re.compile(r"https://huggingface\.co/datasets/", re.IGNORECASE)
        codebase_pattern = re.compile(r"https://github.com", re.IGNORECASE)
        for u in self.urls:
            url_set = set()
            if model_pattern.match(u):
                if dataset_pattern.match(u):
                    url_set.add(('dataset', u))
                else:
                    url_set.add(('model',u))
            elif codebase_pattern.match(u):
                url_set.add(('codebase', u))
            if url_set: units.append(url_set)
        return units

if __name__ == "__main__":
    parser = UrlParser(os.path.join(os.path.dirname(__file__), 'example.ndjson'))
    print(parser.urls)
    print(parser.units)