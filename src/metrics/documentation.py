import logging
import json
import time
import re
import os
import sys
import requests

from metrics.metrics_base import *
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
        api_key: str = os.getenv('GEN_AI_STUDIO_API_KEY')
        if not api_key:
            logging.debug("Unable to obtain Purdue GenAI Studio API key")
            print("ERROR: Unable to obtain Purdue GenAI Studio API key")
            sys.exit(1)
            
        self.api_key: str = api_key
        logging.debug("Obtained Purdue GenAI Studio API key")
        return True
    
    def calculate(self) -> float:
        start_time: float = time.time()

        # Get README content from the asset
        readme_content: str = ReadmeParser.fetch_readme(self.url)
        if not readme_content:
            logging.debug(f"Unable to find README for {self.URL}")
            print(f"ERROR: unable to find README content for {self.url}")
            sys.exit(1)
        
        # setup PurdueGenAI Studio and perform LLM analysis
        if not self._setup_purdue_genai():
            logging.debug("PurdueGenAI Studio API key not found. Set GEN_AI_STUDIO_API_KEY environment variable.")
            print("PurdueGenAI Studio API key not found. Set GEN_AI_STUDIO_API_KEY environment variable.")
            sys.exit(1)

        result: Dict[str, Any] = self._analyze_with_llm(readme_content)
        logging.debug(f"Successful README analysis via LLM for {self.url}")
            

        self.score: float = float(result['documentation_score'])
        self.latency: int = int((time.time() - start_time) * 1000)
        logging.info(f"Documentation score & latency determined for {self.url}")
        return self.score
        
    def _analyze_with_llm(self, readme: str) -> Dict[str, Any]:
        """
            Analyzes README content with scenario specific prompt. Returns
            a Dict containing relevant metrics.
        """
        prompt: str = self._create_prompt(readme)
        
        # calls PurdueGenAI Studio API
        url: str = "https://genai.rcac.purdue.edu/api/chat/completions"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json" 
        }
        body: dict[str, Any] = {
            "model": "llama3.1:latest",
            "messages": [
                {"role": "system", "content": "You are an AI assistant that analyzes README for how well documentation."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1, # controls randomness in model's output
            "max_tokens": 1000, # sets max number of tokens model can generate in response
            "stream": False # gets full response at once. do not print intermediate results
        }
        
        response: Any = requests.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            print(f"ERROR: PurdueGenAI API Error: {response.status_code}, {response.text}")
            logging.info(f"ERROR: PurdueGenAI API Error: {response.status_code}, {response.text}")
            sys.exit(1)
        
        response_data: Any = response.json()
        analysis_text: Any = response_data['choices'][0]['message']['content']
        return self._parse_llm_response(analysis_text)
            
        
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
            # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            logging.debug(f"Successfully parsed LLM response for documentation of {self.url}")
            return json.loads(json_match.group())
        else:
            logging.info(f"Failed to generate proper LLM response for documentation of {self.url}")
            return {"documentation_score": 0.0, "confidence": 0.0, "rationale": "Failed to parse LLM response"}
            