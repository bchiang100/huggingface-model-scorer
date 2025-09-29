# Run: python3 -m test.test_performance_claims
# Run: pip install -e if in venv

from metrics.size import SizeScore
from parsing.url_base import Model
import time

def test() -> None:
    test_urls = [
        "https://huggingface.co/tencent/HunyuanImage-2.1",
        "https://huggingface.co/driaforall/mem-agent", 
        "https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-Thinking",
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest",
        "https://huggingface.co/bytedance-research/HuMo"
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        start_time = time.time()
        
        # Create Model object and performance scorer
        model = Model(url)
        size_scorer = SizeScore(model)
        
        # Calculate score
        score = size_scorer.calculate()
        
        total_latency = int((time.time() - start_time) * 1000)
        
        print(f"Size Score: {score:.3f}")
        print(f"Analysis Latency: {size_scorer.latency} milliseconds")
        
        
        print("-" * 30)
    
    print("\nSize scoring testing ran successfully")

def run() -> None:
    test()
if __name__ == "__main__":
    run()