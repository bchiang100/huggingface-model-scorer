
# --------------------------------------Info--------------------------------------
# Input: README content as string
# Output: Ramp-up score (0.0 to 1.0) and latency in milliseconds
# Description: This script calculates a ramp-up score for an AI/ML model based on documentation quality, 
# instruction availability, and the types of dependencies used.
# How to use: Instantiate RampUpScore with README content and access the "score" attribute. Instantiating the object will automatically calculate the score.
#  ---------------------------------------------------------------------------------

import time
from typing import Optional
from .metrics_base import *

class RampUpScore(Metric):
    def calculate(self) -> float:
        start_time = time.time()
        try:
            # Get README content from the asset
            readme_content = self._get_readme_content()
            if not readme_content:
                self.latency = int((time.time() - start_time) * 1000)
                return 0.0
            
            doc_quality = self._analyze_documentation_quality(readme_content)
            instr_quality = self._analyze_instruction_quality(readme_content)
            ramp_up_score = (doc_quality * 0.40) + (instr_quality * 0.60)
            if (ramp_up_score >= 0.5):
                dependencies = self._analyze_dependencies(readme_content)
                ramp_up_score += (dependencies * 0.1)

            self.latency = int((time.time() - start_time) * 1000)
            self.score = max(0, min(1.0, ramp_up_score))
            return self.score
            
        except Exception:
            self.latency = int((time.time() - start_time) * 1000)
            return 0.0
            
    def _get_readme_content(self) -> Optional[str]:
        """
        Fetch README content from the model repository
        """
        try:
            # For HuggingFace models, try to get README from model card
            if 'huggingface.co' in self.url:
                readme_url = f"{self.url}/raw/main/README.md"
                import requests
                response = requests.get(readme_url)
                if response.status_code == 200:
                    return response.text
            
            return None
        except Exception:
            return None
        
        
    def _analyze_instruction_quality(self, readme: str) -> float:
            # Calculates documentation quality based on installation keywords
            if not readme:
                return 0.0
            readme_lower = readme.lower()
            score = 0.0

            installation_weights = {
                "usage": 0.30,
                "installation": 0.25,
                "requirements": 0.15,
                "quick start": 0.2,
                "quickstart": 0.2,
                "setup": 0.15,
                "getting started": 0.12,
                "just getting started": 0.12,
                "install": 0.1,
                "dependencies": 0.08,
                "how to install": 0.06,
                "prerequisites": 0.05,
                "download": 0.04,
                "example": 0.04,
                "examples": 0.04,
                "import": 0.04,
                "environment": 0.03
            }
            
            installation_score = 0
            found_install = []
            for keyword, weight in installation_weights.items():
                if keyword in readme_lower:
                    installation_score += weight
                    found_install.append(keyword)

            # Adjustments for overlapping keywords and redudancies
            if ("quick start" in found_install) and ("quickstart" in found_install):
                installation_score -= 0.2
                found_install.remove("quickstart")
                
            if ("installation" in found_install) and ("install" in found_install):
                installation_score -= 0.5
                found_install.remove("install")

            if ("installation" in found_install) and ("usage" in found_install):
                installation_score += 0.05

            if ("just getting started" in found_install) and ("getting started" in found_install):
                installation_score -= 0.12
                found_install.remove("just getting started")
                found_install.remove("getting started")

            if ("example" in found_install) and ("examples" in found_install):
                installation_score -= 0.04
                found_install.remove("example")

            score += min(0.6, installation_score)

            # weights for model parameters and signatures
            signature_weights = {
                "input": 0.15,
                "inputs": 0.15,
                "output": 0.15,
                "outputs": 0.15,
                "parameter": 0.08,
                "argument": 0.05
            }

            signature_score = 0.0

            # Small boost if installation section is strong
            if (score > 0.3): 
                signature_score += 0.1
            
            found_sigs = []
            for keyword, weight in signature_weights.items():
                if keyword in readme_lower:
                    signature_score += weight
                    found_sigs.append(keyword)

            # Adjustments for overlapping keywords and redundancies
            if "input" in found_sigs and "inputs" in found_sigs:
                signature_score -= 0.15

            if "output" in found_sigs and "outputs" in found_sigs:
                signature_score -= 0.15
            if(len(found_sigs) >= 3):
                signature_score += 0.1

            signatures_score = max(0.1, min(0.4, signature_score))

            score += signatures_score
            return min(1.0, score)
    
    def _analyze_documentation_quality(self, readme: str) -> float:
        # Calculate documentation quality based on presence of key sections for readability
        if not readme:
            return 0.0
        readme_lower = readme.lower()
        score = 0.0

        sections_weights = {
            "model description": 0.15,
            "overview": 0.12,
            "architecture": 0.1,
            "features": 0.1,
            "capabilities": 0.1,
            "performance": 0.08,
            "limitations": 0.05,
            "training": 0.05,
            "dataset": 0.03,
            "citation": 0.02
        }
        
        section_score = 0
        found_sections = []
        for section, weight in sections_weights.items():
            if section in readme_lower:
                section_score += weight
                found_sections.append(section)

        if (len(found_sections) >= 5):
            section_score += 0.1
        elif (len(found_sections) >= 3):
            section_score += 0.05

        score += min(0.5, section_score)
        
        # Check for code examples (0-0.3 points)
        code_indicators = ["```python", "```", "from transformers", "import"]
        has_code = any(indicator in readme for indicator in code_indicators)
        if has_code:
            score += 0.3
        
        # Length check (0-0.2 points)
        length = len(readme)
        if 5000 <= length <= 10000:
            score += 0.2
        elif length > 2000:
            score += 0.1
        elif length < 100:
            score -= -0.4
        
        return min(1.0, score)
    
        
    def _analyze_dependencies(self, readme: str) -> float:
        if not readme:
            return 0.0
        readme_lower = readme.lower()
        score = 0.0
        
        # Excellent setup (easy to use)
        excellent_deps = {
            "pip install transformers": 0.4,
            "transformers": 0.25,
            "pipeline": 0.2,
            "huggingface_hub": 0.15
        }
        
        excellent_found = []
        excellent_score = 0
        for dep, weight in excellent_deps.items():
            if dep in readme_lower:
                excellent_found.append(dep)
                excellent_score += weight
                break 

        score += excellent_score
        
        # Good setup (using standard ML libraries)
        good_deps = {
            "torch": 0.08,
            "tensorflow": 0.08,
            "numpy": 0.06,
            "scipy": 0.04,
            "pandas": 0.04
        }
        
        good_deps_found = []
        good_score = 0
        for dep, weight in good_deps.items():
            if dep in readme_lower:
                good_deps_found.append(dep)
                good_score += weight

        score += min(0.15, good_score)
            
        # Complex dependencies (harder to set up)
        complex_deps = {
            "build from source": 0.4,
            "cmake": 0.3,
            "docker": 0.2,
            "conda": 0.15,
            "compile": 0.3,
            "makefile": 0.25,
            "gcc": 0.3,
            "cuda": 0.1
        }
        
        penalties = []
        total_penalty = 0
        for dep, penalty in complex_deps.items():
            if dep in readme_lower:
                penalties.append(dep)
                total_penalty += penalty
        
        score -= min(0.4, total_penalty)

        return min(1.0, score)
