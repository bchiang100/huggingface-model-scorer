# --------------------------------------Info--------------------------------------
# Input: Model object with URL attribute
# Output: Performance claims score (0.0 to 1.0) and latency in milliseconds
# Description: This script calculates a performance claims score for an AI/ML model based on 
# benchmark mentions, evaluation methodology, and score credibility in README files using an LLM for evaluation.
# 
# How to use: 
# 1. Set PURDUE_GENAI_API_KEY environment variable with your PurdueGenAI Studio API key in .env file
# 2. Instantiate PerformanceClaimsScore with a Model object
# 3. Access the "score" attribute for the calculated score (0.0-1.0)
# 4. Check "llm_analysis" attribute for detailed LLM breakdown
#  ---------------------------------------------------------------------------------

import time
import os
import json
import re
from typing import Optional, Dict, Any

import requests

from dotenv import load_dotenv
load_dotenv()

class PerformanceClaimsScore:
    def __init__(self, readme_content: Optional[str]):
        self.readme_content = readme_content
        self.latency = 0.0
        self.llm_analysis: Optional[Dict[str, Any]] = None
        self.api_key = None
        self.score = self._calculateScore()
        
    def _setup_purdue_genai(self) -> bool:
        # setup environment variable for PurdueGenAI Studio API key
        api_key = os.getenv('PURDUE_GENAI_API_KEY')
        if not api_key:
            return False
            
        self.api_key = api_key
        return True

    def _calculateScore(self) -> float:
        start_time = time.time()
        try:
            if not self.readme_content:
                self.latency = int((time.time() - start_time) * 1000)
                return 0.0
            
            # setup PurdueGenAI Studio and perform LLM analysis
            if not self._setup_purdue_genai():
                raise ValueError("PurdueGenAI Studio API key not found. Set PURDUE_GENAI_API_KEY environment variable.")
                
            performance_score = self._analyze_with_llm(self.readme_content)

            self.latency = int((time.time() - start_time) * 1000)
            return max(0.0, min(1.0, performance_score))
            
        except Exception:
            self.latency = int((time.time() - start_time) * 1000)
            raise

    def _analyze_with_llm(self, readme: str) -> float:
        try:  
            
            prompt = self._create_prompt(readme)
            
            # calls PurdueGenAI Studio API
            url = "https://genai.rcac.purdue.edu/api/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json" 
            }
            body = {
                "model": "llama3.1:latest",
                "messages": [
                    {"role": "system", "content": "You are a ML researcher analyzing model documentation for benchmark evidence and credibility."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1, # controls randomness in model's output
                "max_tokens": 1000, # sets max number of tokens model can generate in response
                "stream": False # gets full response at once
            }
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code != 200:
                raise Exception(f"PurdueGenAI API Error: {response.status_code}, {response.text}")
            
            response_data = response.json()
            analysis_text = response_data['choices'][0]['message']['content']
            return self._parse_llm_response(analysis_text)
            
        except Exception as e:
            raise RuntimeError(f"LLM analysis failed: {str(e)}")
    
    def _create_prompt(self, readme: str) -> str:
        return f"""You are analyzing a machine learning model's README documentation. Analyze the following README for benchmark evidence and performance claims credibility.

Evaluate and provide scores (0.0 to 1.0) for:

1. BENCHMARK_PRESENCE: Does the README mention recognized benchmarks? Score based on quantity and recognition of benchmarks mentioned.

2. BENCHMARK_QUALITY: Are the benchmarks scores relevant to the model's tasks? Do they provide context to the model's performance?

3. SCORE_CREDIBILITY: Are the reported scores credible? Is there mention of evaluation methodology? 

4. REPRODUCIBILITY: Are sufficient information provided for benchmark reproduction (hyperparameters, training details, code availability)?

README CONTENT:
{readme}

Respond in this exact JSON format. Do not deviate from this format. Do not return in markdown format. You must keep the reasoning less than 50 characters:
{{
  "benchmark_presence": 0.0,
  "benchmark_quality": 0.0, 
  "score_credibility": 0.0,
  "reproducibility": 0.0,
  "reasoning": "Brief explanation of scores. If applicable, explain how the model is best used based on benchmarks."
}}"""
    
    def _parse_llm_response(self, response_text: str) -> float:
        # calculates overall score based on LLM analysis
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if not json_match:
                self.llm_analysis = None
                return 0.0
            
            analysis = json.loads(json_match.group())
            self.llm_analysis = analysis
            
            score = (
                float(analysis.get('benchmark_presence', 0)) * 0.40 + float(analysis.get('benchmark_quality', 0)) * 0.30 + float(analysis.get('score_credibility', 0)) * 0.20 + float(analysis.get('reproducibility', 0)) * 0.10
            )
            
            return score
            
        except Exception:
            self.llm_analysis = None
            return 0.0
