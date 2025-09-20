# Run: python3 test_performance_claims_direct.py
# Direct test that bypasses import issues

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly to avoid __init__.py issues
from metrics.performance_claims import PerformanceClaimsScore
from parsing.url_base import Model
import time

if __name__ == "__main__":
    test_urls = [
        "https://huggingface.co/tencent/HunyuanImage-2.1",
        "https://huggingface.co/driaforall/mem-agent", 
        "https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-Thinking",
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest",
        "https://huggingface.co/bytedance-research/HuMo"
    ]
    
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        start_time = time.time()
        
        # Create Model object and performance scorer
        model = Model(url)
        performance_scorer = PerformanceClaimsScore(model)
        
        # Calculate score
        score = performance_scorer.calculate()
        
        total_latency = int((time.time() - start_time) * 1000)
        
        print(f"Performance Claims Score: {score:.3f}")
        print(f"Analysis Latency: {performance_scorer.latency} milliseconds")
        print(f"Total Latency (including README fetch): {total_latency} milliseconds")
        
        if performance_scorer.llm_analysis and performance_scorer.llm_analysis.get('reasoning'):
            print(f"LLM Analysis: {performance_scorer.llm_analysis['reasoning']}")
        else:
            print("LLM Analysis: Not available")
        
        print("-" * 30)
    
    print("\nPerformanceClaimsScore testing ran successfully")