# Run: python3 -m test.test_documentation
from src.metrics.documentation import Documentation
from src.parsing.url_base import *

def run(examples):
    for i in range(len(examples)):
        m = Model(examples[i])
        documentation = Documentation(m)
        print(f"Calculated score #{i+1}: {documentation.calculate()}")
        print(f"Calculated latency #{i+1}: {documentation.latency}")
        print()

    return

if __name__ == "__main__":
    print("========== Dataset Documentation Score Tests ==========")
    dataset_examples = [
        "https://huggingface.co/datasets/xlangai/AgentNet", # AgentNet (provided ex)
        "https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan", # Nemotron-Personas-Japan
        "https://huggingface.co/datasets/smolagents/aguvis-stage-2",

        "https://huggingface.co/datasets/kentaterasaki/ball_in_cup_dataset_50_316lab", # Rough dataset
        "https://huggingface.co/datasets/zhenqingli/homedepot-search-anchor-positive-title-only" # No README
    ]
    run(dataset_examples)

    print("========== Code Documentation Score Tests ==========")
    code_examples = [
        "https://github.com/SkyworkAI/Matrix-Game", # Matrix Game (provided ex)
        "https://github.com/huggingface/transformers", # transformers
        "https://github.com/tensorflow/tensorflow", # tensorflow

        "https://github.com/bchiang100/huggingface-model-scorer/tree/feature/metrics_dataset-quality" # project github
    ]
    run(code_examples)

