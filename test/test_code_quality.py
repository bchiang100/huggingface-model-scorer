
# Run: PYTHONPATH=src python3 test/test_code_quality.py 
from metrics.code_quality import CodeQuality


def test_code_quality():
    from parsing.url_base import Codebase

    test_repos = [
        "https://github.com/huggingface/transformers.git",
        "https://github.com/pytorch/pytorch.git",
        "https://github.com/tensorflow/tensorflow.git"
    ]

    print("Testing Code Quality Analyzer")
    print("=" * 50)

    for repo_url in test_repos:
        print(f"\nAnalyzing: {repo_url}")
        try:
            asset = Codebase(repo_url)
            analyzer = CodeQuality(asset)
            score = analyzer.calculate()

            print(f"  Code Quality Score: {score:.3f}")
            print(f"  Latency: {analyzer.latency}ms")
            print(f"  Function Length Score: {analyzer.function_length_score:.3f}")
            print(f"  Style Score: {analyzer.style_score:.3f}")
            print(f"  Recency Score: {analyzer.recency_score:.3f}")
            print(f"  Total Functions: {analyzer.total_functions}")
            print(f"  Style Violations: {analyzer.style_violations}")
            print(f"  Days Since Last Commit: {analyzer.days_since_last_commit}")

        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    test_code_quality()