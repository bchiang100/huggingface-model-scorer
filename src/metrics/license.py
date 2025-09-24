# --------------------------------------Info--------------------------------------
# Input: Model object with URL attribute
# Output: License score (0.0 to 1.0) and latency in milliseconds
# Description: This script calculates a license score using README content, with a fallback
# analysis using data from the model card.
# 
# How to use: 
# 1. Set PURDUE_GENAI_API_KEY environment variable with your PurdueGenAI Studio API key in .env file
# 2. Instantiate License with a Model object (containing Model URL)
# 3. Access the "score" attribute for the calculated score (0.0-1.0)
# 4. Use provided DEBUG print statements to track LLM output
#  ---------------------------------------------------------------------------------

import re
import os
import requests

from .metrics_base import *
from ..parsing.readme_parser import ReadmeParser
from typing import Dict, Any

class License(Metric):
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
        """
            Returns a license score (0-1) based on license clarity and permissiveness.
        """
        import time

        start_time = time.time()
        try:
            # Get README content from the asset
            readme_content = self._get_readme_content()
            if not readme_content:
                raise ValueError("README content not found.")
            
            # setup PurdueGenAI Studio and perform LLM analysis
            if not self._setup_purdue_genai():
                raise ValueError("PurdueGenAI Studio API key not found. Set PURDUE_GENAI_API_KEY environment variable.")

            result = self._analyze_with_llm(readme_content)
            # print(f"DEBUG: LLM extracted license score: {result['license_score']}")
            # print(f"DEBUG: LLM extracted license name: {result['license_name']}")
            # print(f"DEBUG: LLM extracted license confidence: {result['confidence']}")
            # print(f"DEBUG: LLM extracted license rationale: {result['rationale']}")
            
        except Exception as e:
            print(f"Error extracting license from README: {e}")
            raise
        
        if result['license_name'] == 'Unknown':
            # print(f"DEBUG: Using fallback analysis.")
            self._fallbackScore()
        else:
            self.score = float(result['license_score'])

        self.latency = int((time.time() - start_time) * 1000)
        return self.score
    
    def _get_readme_content(self) -> Optional[str]:
        """
            Fetch README content from the model repository.
        """
        try:
            return ReadmeParser.fetch_readme(self.url)
        except Exception as e:
            print(f"Error fetching README: {e}")
            return None
        
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
                    {"role": "system", "content": "You are an AI assistant that analyzes software licenses for compatibility with LGPLv2.1."},
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
Analyze the provided README content and determine a license compatibility score between 0.0 and 1.0.

# SCORING CRITERIA:
- 1.0: Fully compatible permissive licenses (MIT, Apache 2.0, BSD, ISC, LGPLv2.1 itself)
- 0.8-0.9: Clearly compatible with minor restrictions
- 0.5-0.7: Likely compatible but requires verification
- 0.2-0.4: Potentially problematic licenses (GPLv2, custom restrictions)
- 0.0-0.1: Incompatible (proprietary, no license, non-commercial)

# README CONTEXT:
{readme}

# OUTPUT FORMAT REQUIREMENTS:
You MUST respond ONLY in this exact JSON format with no additional text:

{{
  "license_score": <float between 0.0 and 1.0>,
  "license_name": "<detected license name or 'Unknown'>",
  "confidence": <float between 0.0 and 1.0>,
  "rationale": "<brief explanation of score>"
}}

# LICENSE DETECTION PRIORITY:
1. Look for explicit "License" section in README
2. Check for SPDX identifiers in headers or metadata
3. Look for common license phrases and names
4. If no license found, assume "No License"

# IMPORTANT:
- If no license information is found, use license_score: 0.0
- Be conservative when license is ambiguous
- Prefer specific version mentions over generic names
- For multiple licenses, use the most restrictive one found

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
                return {"license_score": 0.0, "license_name": "Parse Error", "confidence": 0.0, "rationale": "Failed to parse LLM response"}
            
        except Exception:
            self.llm_analysis = None
            return 0.0

#   ==========================
#   Fallback Analysis (using direct model card mapping)
#   ==========================

    def _fallbackScore(self) -> float:
        """
            Fallback: Calculates score using license mapping from model card.
        """
        license_name = self._fallbackGetLicense()
        if not license_name:
            return 0.0

        license = license_name.lower()

        # Mapping of license keywords to scores
        license_scores = {
            # Perfect scores
            "lgpl-2.1": 1.0, "lgplv2.1": 1.0,
            "mit": 1.0, "mit license": 1.0,
            "apache-2.0": 1.0, "apache 2.0": 1.0, "apache license 2.0": 1.0,
            "bsd-2-clause": 1.0, "bsd-3-clause": 1.0,
            "isc": 1.0, "unlicense": 0.9,
            
            # Good scores
            "lgpl-3.0": 0.7, "lgplv3": 0.7,
            "mpl-2.0": 0.7,
            "epl-1.0": 0.6,
            
            # Problematic scores
            "gpl-2.0": 0.4, "gplv2": 0.4,
            "gpl-3.0": 0.3, "gplv3": 0.3,
            "agpl-3.0": 0.2,
            
            # Zero scores
            "proprietary": 0.0, "none": 0.0, "no license": 0.0,
        }

        for key, score in license_scores.items():
            if key in license:
                self.score = score
                break

        return self.score
    
    def _fallbackGetLicense(self) -> str:
        """
            Fallback: Returns license extracted from HuggingFace API
        """
        from huggingface_hub import HfApi

        # extract model_id from the site.url
        # Example: https://huggingface.co/google/gemma-3-270m/tree/main
        model_id = None
        match = re.search(r"huggingface\.co/([^/]+/[^/]+|[^/]+)", self.url)
        if match:
            model_id = match.group(1)
        if not model_id:
            return None
        

        # get model info
        api = HfApi()
        try:
            info = api.model_info(model_id)
            # print(info)
        except Exception as e:
            print(f"Error fetching model info: {e}")
            return None

        license = None
        # license is usually stored in info.card_data
        if getattr(info, "card_data", None):
            # card_data might be a dataclass or dict-like
            cd = info.card_data
            license = getattr(cd, "license", None) or (cd.get("license") if hasattr(cd, "get") else None)

        if not license:
            # fallback: check top-level fields
            license = getattr(info, "license", None) or (info.get("license") if hasattr(info, "get") else None)
        
        return license