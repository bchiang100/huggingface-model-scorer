from metrics.busfactor import BusFactorMetric
from parsing.url_base import *

def test_code(examples):
    for i,e in enumerate(examples):
        m = Codebase(e)
        busfactor = BusFactorMetric(m)
        print(f"Calculated score #{i+1}: {busfactor.calculate()}")
        print(f"Calculated latency #{i+1}: {busfactor.latency}")
        print()

    return

def test_model(examples):
    for i,e in enumerate(examples):
        m = Model(e)
        busfactor = BusFactorMetric(m)
        print(f"Calculated score #{i+1}: {busfactor.calculate()}")
        print(f"Calculated latency #{i+1}: {busfactor.latency}")
        print()

    return

def run():
    print("========== Codebase Busfactor Score Tests ==========")
    examples = [
        "https://github.com/SkyworkAI/Matrix-Game", # Matrix Game (provided ex)
        "https://github.com/huggingface/transformers", # transformers
        "https://github.com/tensorflow/tensorflow", # tensorflow
        "https://github.com/bchiang100/huggingface-model-scorer" # project github
        ]
    test_code(examples)

    print("========== Model Busfactor Score Tests ==========")
    examples = [
        "https://huggingface.co/bigcode/santacoder", # SantaCoder (provided ex)
        "https://huggingface.co/google/flan-t5-base", # google flan-t5-base
        "https://huggingface.co/facebook/blenderbot-3B" # facebook blenderbot-3B
        ]
    test_model(examples)

if __name__ == "__main__":
    run()