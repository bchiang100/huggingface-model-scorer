# Run: python3 -m test.test_license
from src.metrics.license import License
from src.parsing.url_base import *

if __name__ == "__main__":
    # Example HuggingFace model URLs
    example_url = [
        "https://huggingface.co/google/gemma-3-270m/tree/main",
        "https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k",
        "https://huggingface.co/tencent/SRPO"
    ]

    for i, url in enumerate(example_url):
        m = Model(example_url[i])
        license = License(m)
        print(f"Extracted license #{i+1}: {license._getLicense()}")
        print(f"Calculated score #{i+1}: {license.calculate()}")
        # print(f"Stored score #{i+1}: {license.score}")
        print(f"Calculated latency #{i+1}: {license.latency}")
        print()