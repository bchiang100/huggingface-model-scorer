from metrics.dataset_quality import DatasetQualityMetric
from parsing.url_base import *

def test_code(examples):
    for i,e in enumerate(examples):
        m = Dataset(e)
        dq = DatasetQualityMetric(m)
        print(f"Calculated score #{i+1}: {dq.calculate()}")
        print(f"Calculated latency #{i+1}: {dq.latency}")
        print()

    return

def run():
    print("========== Dataset Quality Score Tests ==========")
    examples = [
        "https://huggingface.co/datasets/allenai/c4", # c4 (provided ex)
        "https://huggingface.co/datasets/mteb/STS", # mteb/STS
        "https://huggingface.co/datasets/bigcode/the-stack", # bigcode/the-stack
        ]
    test_code(examples)

if __name__ == "__main__":
    run()