# Run: python -m test.test_performance_claims

from src.metrics.performance_claims import PerformanceClaimsScore
from src.parsing.readme_parser import ReadmeParser
import time

if __name__ == "__main__":
    test_urls = [
        "https://huggingface.co/tencent/HunyuanImage-2.1/blob/main/README.md",
        "https://huggingface.co/driaforall/mem-agent/blob/main/README.md",
        "https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-Thinking",
        "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest/blob/main/README.md",
        "https://huggingface.co/bytedance-research/HuMo"
    ]
    
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        start_time = time.time()
        
        readme_content = ReadmeParser.fetch_readme(url)
        
        performance_scorer = PerformanceClaimsScore(readme_content)
        
        total_latency = int((time.time() - start_time) * 1000)
        
        print(f"Performance Claims Score: {performance_scorer.score:.3f}")
        print(f"Analysis Latency: {performance_scorer.latency} milliseconds")
        print(f"Total Latency (including README fetch): {total_latency} milliseconds")
        
        if performance_scorer.llm_analysis and performance_scorer.llm_analysis.get('reasoning'):
            print(f"LLM Analysis: {performance_scorer.llm_analysis['reasoning']}")
        else:
            print("LLM Analysis: Not available")
        
        print("-" * 30)
    
    print("\nPerformanceClaimsScore testing ran successfully")