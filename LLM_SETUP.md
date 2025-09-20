# LLM Setup for PerformanceClaimsScore

The PerformanceClaimsScore class **requires** LLM analysis for sophisticated evaluation of performance claims in README files using **PurdueGenAI Studio** (free for Purdue students).

## Required Setup

1. **Get PurdueGenAI Studio API Key**:
   - Go to https://genai.rcac.purdue.edu/
   - Click on your user avatar → Settings → Account
   - Expand "API Keys" section
   - Create and copy your API key

2. **Set Environment Variable** (REQUIRED):
   ```bash
   export PURDUE_GENAI_API_KEY="your_api_key_here"
   ```
   
   Or create a `.env` file in the project root:
   ```
   PURDUE_GENAI_API_KEY=your_api_key_here
   ```

## How it Works

### LLM Analysis (REQUIRED):
- Uses **Llama 3.1** via PurdueGenAI Studio to analyze README content
- **FREE** for Purdue students (no usage costs)
- Provides structured analysis of:
  - **Benchmark Presence**: Recognition of standard benchmarks
  - **Benchmark Quality**: Appropriateness and numerical results  
  - **Score Credibility**: Evidence of proper validation methodology
  - **Reproducibility**: Availability of implementation details
- **No Fallback**: Implementation will raise errors if PurdueGenAI API key is not available

## Usage

```python
from src.metrics.performance_claims import PerformanceClaimsScore
from src.parsing.url_base import Model

model = Model("https://huggingface.co/google/flan-t5-base")
scorer = PerformanceClaimsScore(model)

print(f"Score: {scorer.score:.3f}")
print(f"Latency: {scorer.latency}ms")

# If LLM was used, detailed analysis is available
if scorer.llm_analysis:
    print("LLM Analysis:", scorer.llm_analysis)
else:
    print("Used rule-based fallback analysis")
```

## Benefits of LLM Analysis

- **Context Understanding**: Better comprehension of nuanced claims
- **Credibility Assessment**: More sophisticated evaluation of methodology
- **Adaptive Analysis**: Can handle non-standard benchmark reporting
- **Quality Judgment**: Better assessment of benchmark appropriateness