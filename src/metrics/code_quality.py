from metrics.metrics_base import *
import requests
import ast
import re
from datetime import datetime, timezone
from typing import List


class CodeQualityMetric(Metric):
    def calculate(self) -> float:
        """
        Calculate code quality score based on function length, coding style, and recency
        Returns a float between 0 and 1, where 1 is excellent code quality
        """
        if self.asset_type != Codebase:
            return 0.0  # Only applicable to code repositories
        
        function_score = self._analyze_function_length()
        style_score = self._analyze_coding_style()
        recency_score = self._analyze_repository_recency()
        
        # Weighted combination: 40% function length + 40% style + 20% recency
        return 0.4 * function_score + 0.4 * style_score + 0.2 * recency_score

    def _analyze_function_length(self) -> float:
        """
        Analyze function lengths across Python files in the repository
        Returns score where 1.0 = all functions are reasonable length
        """
        python_files = self._get_python_files()
        if not python_files:
            return 1.0  # No Python files to analyze
        
        total_functions = 0
        good_functions = 0
        
        for file_content in python_files:
            try:
                tree = ast.parse(file_content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        # Calculate function length
                        length = (node.end_lineno or node.lineno) - node.lineno + 1
                        # Consider functions under 50 lines as "good"
                        if length <= 50:
                            good_functions += 1
            except SyntaxError:
                # Skip files with syntax errors
                continue
        
        if total_functions == 0:
            return 1.0
        
        return good_functions / total_functions

    def _analyze_coding_style(self) -> float:
        """
        Analyze coding style consistency across Python files
        Returns score where 1.0 = excellent style consistency
        """
        python_files = self._get_python_files()
        if not python_files:
            return 1.0
        
        style_violations = 0
        total_checks = 0
        
        for file_content in python_files:
            lines = file_content.split('\n')
            
            for line in lines:
                if line.strip():  # Skip empty lines
                    total_checks += 1
                    
                    # Check for multiple statements on one line
                    if ';' in line and not line.strip().startswith('#'):
                        style_violations += 1
                    
                    # Check for trailing whitespace
                    if line.endswith(' ') or line.endswith('\t'):
                        style_violations += 1
                    
                    # Check for inconsistent spacing around operators
                    if re.search(r'[a-zA-Z0-9]\+[a-zA-Z0-9]|[a-zA-Z0-9]\=[a-zA-Z0-9]', line):
                        style_violations += 1
        
        if total_checks == 0:
            return 1.0
        
        # Convert violations to a quality score
        violation_rate = style_violations / total_checks
        return max(0.0, 1.0 - violation_rate * 2)  # Multiply by 2 to be more strict

    def _analyze_repository_recency(self) -> float:
        """
        Analyze how recently the repository has been updated
        Returns score where 1.0 = very recent updates
        """
        try:
            response = requests.get(self.api_endpoint)
            response.raise_for_status()
            repo_data = response.json()
            
            updated_at = repo_data.get('updated_at')
            if not updated_at:
                return 0.0
            
            # Parse the updated timestamp
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_since_update = (now - last_update).days
            
            # Score based on recency: 1.0 for updates within 30 days, decreasing
            if days_since_update <= 30:
                return 1.0
            elif days_since_update <= 90:
                return 0.8
            elif days_since_update <= 180:
                return 0.6
            elif days_since_update <= 365:
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.5  # Default score if unable to check recency

    def _get_python_files(self) -> List[str]:
        """
        Fetch Python file contents from the repository
        Returns list of file contents as strings
        """
        try:
            # Get repository contents
            contents_url = f"{self.api_endpoint}/contents"
            response = requests.get(contents_url)
            response.raise_for_status()
            contents = response.json()
            
            python_files = []
            for item in contents:
                if item['type'] == 'file' and item['name'].endswith('.py'):
                    # Fetch file content
                    file_response = requests.get(item['download_url'])
                    if file_response.status_code == 200:
                        python_files.append(file_response.text)
            
            return python_files
            
        except Exception:
            return []


if __name__ == "__main__":
    codebase = Codebase("https://github.com/bchiang100/huggingface-model-scorer")
    cq_metric = CodeQualityMetric(codebase)
    print(f"Code Quality Score: {cq_metric.calculate()}")