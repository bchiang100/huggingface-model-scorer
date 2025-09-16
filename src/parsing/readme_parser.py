import requests
import os
from typing import Optional

# loads environemental variables from .env file to get user token (optional)
# this allows access to gated and private models

from dotenv import load_dotenv
load_dotenv()

class ReadmeParser:
    # fetches README content from GitHub or HuggingFace repositories
    @staticmethod
    def fetch_readme(url: str) -> Optional[str]:
        # Input: URL of the repository (HuggingFace or GitHub)
        # Output: README content as a string, or None if not found
        # Usage: Call ReadmeParser.fetch_readme(url) with the repository URL
        model_id = ReadmeParser._extract_model_id(url)
        if not model_id:
            return None
            
        if "github.com" in url:
            return ReadmeParser._fetch_github_readme(model_id)
        elif "huggingface.co" in url:
            return ReadmeParser._fetch_huggingface_readme(model_id)
        else:
            return None
    
    @staticmethod
    def _fetch_huggingface_readme(model_id: str) -> Optional[str]:
        # Fetches README from HuggingFace raw files.
        try:
            # Add authentication if token is available (optional)
            headers = {}
            token = os.getenv('HUGGINGFACE_TOKEN')
            if token:
                headers['Authorization'] = f"Bearer {token}"
            
            # try main branch first
            readme_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
            response = requests.get(readme_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # request successful
                return response.text
            else:
                # Try master branch instead of main (for repos older than 2020)
                readme_url = f"https://huggingface.co/{model_id}/raw/master/README.md"
                response = requests.get(readme_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.text
                else:
                    return None
        except Exception as e:
            return None
    
    @staticmethod
    def _fetch_github_readme(repo_path: str) -> Optional[str]:
        # Fetches README from GitHub raw files.
        try:
            # Add authentication if token is available (optional)
            headers = {}
            token = os.getenv('GITHUB_TOKEN')
            if token:
                headers['Authorization'] = f"token {token}"
            
            # Different README naming conventions
            readme_variations = ['README.md', 'readme.md', 'Readme.md', 'README.MD', 'readme', 'README']
            branches = ['main', 'master']
            
            for branch in branches:
                for readme_name in readme_variations:
                    readme_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/{readme_name}"
                    response = requests.get(readme_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        return response.text
            
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def _extract_model_id(url: str) -> Optional[str]:
        # Extracts model id from both URLs
        if not url:
            return None
        
        try:
            if "huggingface.co" in url:
                # Handle HuggingFace URLs
                parts = url.split("huggingface.co/")
                if len(parts) > 1:
                    model_path = parts[1]
                    # Removes any trailing paths
                    model_path = model_path.split("/tree")[0]
                    model_path = model_path.split("/blob")[0]
                    model_path = model_path.rstrip("/")
                    return model_path
            
            elif "github.com" in url:
                # Handle GitHub URLs: https://github.com/owner/repo
                parts = url.split("github.com/")
                if len(parts) > 1:
                    repo_path = parts[1]
                    repo_path = repo_path.split("/tree")[0]
                    repo_path = repo_path.split("/blob")[0]
                    repo_path = repo_path.split("/issues")[0]
                    repo_path = repo_path.split("/pull")[0]
                    repo_path = repo_path.rstrip("/")
                    path_parts = repo_path.split("/")
                    if len(path_parts) >= 2:
                        return f"{path_parts[0]}/{path_parts[1]}"
                        
        except Exception:
            pass
        
        return None