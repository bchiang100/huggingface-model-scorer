import re
import os
import requests

from .metrics_base import *
from parsing.readme_parser import ReadmeParser
from typing import Dict, Any

class Documentation(Metric):
    def __init__(self, asset):
        super().__init__(asset)
        self.api_key = None
        
    def _setup_purdue_genai(self) -> bool:
        """
            Setup environment variable for PurdueGenAI Studio API key
        """
        api_key = os.getenv('PURDUE_GENAI_API_KEY')
        if not api_key:
            return False
            
        self.api_key = api_key
        return True
    
    def calculate(self) -> float:
        import time
        start_time = time.time()
        try:
            # Get README content from the asset
            readme_content = ReadmeParser.fetch_readme(self.url)
            if not readme_content:
                raise ValueError("README content not found.")
            
            # setup PurdueGenAI Studio and perform LLM analysis
            if not self._setup_purdue_genai():
                raise ValueError("PurdueGenAI Studio API key not found. Set PURDUE_GENAI_API_KEY environment variable.")

            result = self._analyze_with_llm(readme_content)
            # print(f"DEBUG: LLM extracted documentation score: {result['documentation_score']}")
            # # print(f"DEBUG: LLM extracted category scores: {result['category_scores']}")
            # print(f"DEBUG: LLM extracted confidence: {result['confidence']}")
            # print(f"DEBUG: LLM extracted rationale: {result['rationale']}")
            
        except Exception as e:
            print(f"Error extracting documentation score from README: {e}")
            raise

        self.score = float(result['documentation_score'])
        self.latency = int((time.time() - start_time) * 1000)
        return self.score
        
    def _analyze_with_llm(self, readme: str) -> Dict[str, Any]:
        """
            Analyzes README content with scenario specific prompt. Returns
            a Dict containing relevant metrics.
        """
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
                    {"role": "system", "content": "You are an AI assistant that analyzes README for how well documentation."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1, # controls randomness in model's output
                "max_tokens": 1000, # sets max number of tokens model can generate in response
                "stream": False # gets full response at once. do not print intermediate results
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
        return f"""
Analyze the provided README content and determine a documentation quality score between 0.0 and 1.0.

# EVALUATION CRITERIA:
- 0.9-1.0: Excellent - Exceeds requirements. Documentation is comprehensive, self-contained, and includes
detailed examples, benchmarking code/results, and a thorough analysis of limitations. Exceptionally clear 
and easy to follow.
- 0.8-0.89: Good - Covers all critical aspects thoroughly. Includes clear examples and procedures, with 
minor areas for improvement (e.g., one missing example or a slightly vague limitation).
- 0.7-0.79: Satisfactory - Covers all major requirements functionally. Contains essential examples and procedures, 
but lacks detail, requiring some user effort to fill in minor gaps.
- 0.5-0.69: Fair - Misses at least one major requirement or has significant gaps in multiple areas. 
Documentation is incomplete, requiring substantial user inference or external knowledge for basic use.
- 0.3-0.49: Poor - Severely lacking, offering only fragmented or minimal information.
- 0.1-0.19: Very Poor - No meaningful documentation provided or information is incorrect/misleading.

# README CONTEXT:
{readme}

# OUTPUT FORMAT REQUIREMENTS:
You MUST respond ONLY in this exact JSON format with no additional text:

{{
  "documentation_score": <float between 0.0 and 1.0>,
  "confidence": <float between 0.0 and 1.0>,
  "rationale": <brief explanation of score>
}}

Now analyze the README and provide your response in the required JSON format.
"""
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
            Parses LLM response_text into returned Dict.
        """
        try:
            import json

            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"documentation_score": 0.0, "confidence": 0.0, "rationale": "Failed to parse LLM response"}
            
        except Exception:
            self.llm_analysis = None
            return 0.0