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

import json
import logging
import sys
import time
import re
import os
from regex import Match
import requests
from huggingface_hub import HfApi

from metrics.metrics_base import *
from parsing.readme_parser import ReadmeParser
from typing import Dict, Any

class License(Metric):
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
        """
            Returns a license score (0-1) based on license clarity and permissiveness.
        """
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
        
        if result['license_name'] == 'Unknown':
            logging.debug("Using fallback analysis for license; unable to find LLM response")
            self._fallbackScore()
        else:
            logging.debug("Successfully used LLM to analyze README for license")
            self.score: float = float(result['license_score'])

        self.latency: int = int((time.time() - start_time) * 1000)
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
            # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            logging.debug(f"Successfully parsed LLM response for documentation of {self.url}")
            return json.loads(json_match.group())
        else:
            logging.info(f"Failed to generate proper LLM response for documentation of {self.url}")
            self.llm_analysis = None
            return {"license_score": 0.0, "license_name": "Parse Error", "confidence": 0.0, "rationale": "Failed to parse LLM response"}
            

#   ==========================
#   Fallback Analysis (using direct model card mapping)
#   ==========================

    def _fallbackScore(self) -> float:
        """
            Fallback: Calculates score using license mapping from model card.
        """
        license_name: str = self._fallbackGetLicense()
        if not license_name:
            logging.info(f"Unable to retrieve license of {self.url}")
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

        logging.info(f"Successful fallback license analysis for {self.url}")
        return self.score
    
    def _fallbackGetLicense(self) -> str:
        """
            Fallback: Returns license extracted from HuggingFace API
        """

        # extract model_id from the site.url
        # Example: https://huggingface.co/google/gemma-3-270m/tree/main
        model_id: str = None
        match: Match[str] = re.search(r"huggingface\.co/([^/]+/[^/]+|[^/]+)", self.url)
        if match:
            model_id = match.group(1)
        if not model_id:
            logging.info(f"Unable to find model id from url for {self.url}")
            return None
        

        # get model info
        api = HfApi()
        try:
            info = api.model_info(model_id)
            # print(info)
        except Exception as e:
            print(f"Error fetching model info: {e}")
            logging.info(f"Unable to find model information for {self.url}")
            return None

        license: Any = None
        # license is usually stored in info.card_data
        if getattr(info, "card_data", None):
            # card_data might be a dataclass or dict-like
            cd = info.card_data
            license = getattr(cd, "license", None) or (cd.get("license") if hasattr(cd, "get") else None)

        if not license:
            # fallback: check top-level fields
            license = getattr(info, "license", None) or (info.get("license") if hasattr(info, "get") else None)
        
        logging.debug(f"Fallback license obtained for {self.url}")
        return license