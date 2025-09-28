# Run: python3 -m test.test_ramp_up
# Run: pip install -e if in venv

from src.metrics.ramp_up import RampUpScore
from src.parsing.url_base import Model
import time

if __name__ == "__main__":
    # Test URLs - updated to HuggingFace model URLs
    test_urls = [
        "https://huggingface.co/jhu-clsp/mmBERT-base", # excellent ramp up time
        "https://huggingface.co/tencent/HunyuanImage-2.1", # very good ramp up time
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest", # normal ramp up time
        "https://huggingface.co/bert-base-uncased", # good ramp up time
        "https://huggingface.co/google/flan-t5-small" # decent ramp up time
    ]
    
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        # Measure total latency including README fetching
        start_time = time.time()
        
        # Create Model object and ramp-up scorer
        model = Model(url)
        ramp_up_scorer = RampUpScore(model)
        
        # Calculate score
        score = ramp_up_scorer.calculate()
        
        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)
        
        print(f"Ramp-up Score: {score:.3f}")
        print(f"Analysis Latency: {ramp_up_scorer.latency} milliseconds")
        print(f"Total Latency (including README fetch): {total_latency} milliseconds")
        
        print("-" * 30)
    
    print("\nRampUpScore testing completed successfully")
