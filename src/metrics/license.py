from src.parsing.url_base import Site
from huggingface_hub import HfApi
import re

class License:
    def getLicense(self, site: Site) -> str:
        """
        Returns license extracted from HuggingFace API
        """
        # extract model_id from the site.url
        # Example: https://huggingface.co/google/gemma-3-270m/tree/main
        model_id = None
        if hasattr(site, "url"):
            match = re.search(r"huggingface\.co/([^/]+/[^/]+|[^/]+)", site.url)
            if match:
                model_id = match.group(1)
        if not model_id:
            return None
        

        # get model info
        api = HfApi()
        try:
            info = api.model_info(model_id)
            # print(info)
        except Exception as e:
            print(f"Error fetching model info: {e}")
            return None

        license = None
        # license is usually stored in info.card_data
        if getattr(info, "card_data", None):
            # card_data might be a dataclass or dict-like
            cd = info.card_data
            license = getattr(cd, "license", None) or (cd.get("license") if hasattr(cd, "get") else None)

        if not license:
            # fallback: check top-level fields
            license = getattr(info, "license", None) or (info.get("license") if hasattr(info, "get") else None)

        # print("license:", license)
        return license
    
    def score(self, site: Site) -> float:
        """
        Returns a license score (0-1) based on license clarity and permissiveness.
        """
        license_name = self.getLicense(site)
        if not license_name:
            return 0.0

        license = license_name.lower()

        # Mapping of license keywords to scores
        license_scores = {
            "apache": 1.0,
            "mit": 1.0,
            "bsd": 0.9,
            "cc-by": 0.8,
            "gpl": 0.6,
            "lgpl": 0.7,
            "mozilla": 0.7,
            "gemma": 0.7,
            "cc-by-nc": 0.3,
            "cc0": 1.0,
            "openrail": 0.7,
            "proprietary": 0.0,
            "unknown": 0.0,
            "other": 0.0,
            "none": 0.0,
            "research": 0.3,
            "non-commercial": 0.3,
        }

        for key, score in license_scores.items():
            if key in license:
                return score
        
        return 0.0
    
if __name__ == "__main__":
    # Example HuggingFace model URLs
    example_url = [
        "https://huggingface.co/google/gemma-3-270m/tree/main",
        "https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k",
        "https://huggingface.co/tencent/SRPO"
    ]
    
    class DummySite:
        def __init__(self, url):
            self.url = url

    license_checker = License()
    for i, url in enumerate(example_url):
        site = DummySite(url)
        print(f"Extracted license #{i+1}: {license_checker.getLicense(site)}")
        print(f"Calculated score #{i+1}: {license_checker.score(site)}")
        print()