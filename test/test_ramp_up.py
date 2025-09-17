# Run: python -m test.test_ramp_up

from src.metrics.ramp_up import RampUpScore
from src.parsing.readme_parser import ReadmeParser
import time

if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://huggingface.co/jhu-clsp/mmBERT-base/blob/main/README.md", # excellent ramp up time
        "https://huggingface.co/tencent/HunyuanImage-2.1", # very good ramp up time
        "https://github.com/MacPaw/OpenAI/blob/main/README.md", # github openai readme
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest/blob/main/README.md", # normal ramp up time
        "https://huggingface.co/Barytes/hellohf/blob/main/README.md" # poor ramp up time
    ]
    
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        # Measure total latency including README fetching
        start_time = time.time()
        
        # Fetch README content first
        readme_content = ReadmeParser.fetch_readme(url)
        
        # Create RampUpScore instance (score is calculated automatically)
        ramp_up_scorer = RampUpScore(readme_content)
        
        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)
        
        print(f"Ramp-up Score: {ramp_up_scorer.score:.3f}")
        print(f"Analysis Latency: {ramp_up_scorer.latency} milliseconds")
        print(f"Total Latency (including README fetch): {total_latency} milliseconds")
        
        print("-" * 30)
    
    print("\nRampUpScore testing completed successfully")
