# Run: python3 -m test.test_license
from metrics.license import License
from parsing.url_base import *

def test():
    # Example HuggingFace model URLs
    print("========== High License Score Tests ==========")
    high_examples = [
        "https://huggingface.co/a32fsdf23/mytest12345", # LGPL 2.1
        "https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k", # apache 2.0
        "https://huggingface.co/FacebookAI/roberta-large", # mit
    ]

    for i, url in enumerate(high_examples):
        m = Model(high_examples[i])
        license = License(m)
        # print(f"Extracted license #{i+1}: {license._getLicense()}")
        print(f"Calculated score #{i+1}: {license.calculate()}")
        # print(f"Stored score #{i+1}: {license.score}")
        print(f"Calculated latency #{i+1}: {license.latency}")
        print()

    print("========== Low License Score Tests ==========")
    low_examples = [
        "https://huggingface.co/tencent/SRPO", #tencent-hunyuan
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest", # cc-by-4.0
        "https://huggingface.co/driaforall/mem-agent" # not mentioned
    ]

    for i, url in enumerate(low_examples):
        m = Model(low_examples[i])
        license = License(m)
        # print(f"Extracted license #{i+1}: {license._getLicense()}")
        print(f"Calculated score #{i+1}: {license.calculate()}")
        # print(f"Stored score #{i+1}: {license.score}")
        print(f"Calculated latency #{i+1}: {license.latency}")
        print()

def run():
    test() 

if __name__ == "__main__":
    # Example HuggingFace model URLs
    print("========== High License Score Tests ==========")
    high_examples = [
        "https://huggingface.co/a32fsdf23/mytest12345", # LGPL 2.1
        "https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k", # apache 2.0
        "https://huggingface.co/FacebookAI/roberta-large", # mit
    ]

    for i, url in enumerate(high_examples):
        m = Model(high_examples[i])
        license = License(m)
        # print(f"Extracted license #{i+1}: {license._getLicense()}")
        print(f"Calculated score #{i+1}: {license.calculate()}")
        # print(f"Stored score #{i+1}: {license.score}")
        print(f"Calculated latency #{i+1}: {license.latency}")
        print()

    print("========== Low License Score Tests ==========")
    low_examples = [
        "https://huggingface.co/tencent/SRPO", #tencent-hunyuan
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest", # cc-by-4.0
        "https://huggingface.co/driaforall/mem-agent" # not mentioned
    ]

    for i, url in enumerate(low_examples):
        m = Model(low_examples[i])
        license = License(m)
        # print(f"Extracted license #{i+1}: {license._getLicense()}")
        print(f"Calculated score #{i+1}: {license.calculate()}")
        # print(f"Stored score #{i+1}: {license.score}")
        print(f"Calculated latency #{i+1}: {license.latency}")
        print()    