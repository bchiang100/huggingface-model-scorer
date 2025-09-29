# --------------------------------------Info--------------------------------------
# Input: Repository URL
# Output: Code quality score (0.0 to 1.0) and latency in milliseconds
# Description: Calculates code quality score for a repository based on function length, code style compliance using flake8, and repository recency (time from last commit).
# How to use: Instantiate CodeQuality with an asset. Make sure to install GitPython dependency (pip3 install GitPython)
#  ---------------------------------------------------------------------------------

import ast
import subprocess
import tempfile
from typing import Optional
from datetime import datetime
import time
from pathlib import Path
import git
from git import Repo
from metrics.base import Metric


class CodeQuality(Metric):
    # analyzes code quality for machine learning model repositories

    def __init__(self, asset, max_function_lines: int = 50, max_days_old: int = 365):
        super().__init__(asset)
        self.max_function_lines = max_function_lines
        self.max_days_old = max_days_old

    def calculate(self) -> float:
        import signal
        import os

        start_time = time.time()
        timeout_seconds = 15

        # Track which analyses completed successfully
        function_score = None
        style_score = None
        recency_score = None
        violations = 0
        days_old = 999
        repo = None

        def timeout_handler(_signum, _frame):
            raise TimeoutError("Code quality calculation timed out after 15 seconds")

        try:
            if os.name != 'nt':  # Not Windows
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)

            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    repo = self._clone_repository(self.url, temp_dir)
                except:
                    pass  # Continue with analysis even if clone fails

                # Try each analysis step, only store real results
                try:
                    function_score = self._analyze_function_lengths(temp_dir)
                except:
                    pass

                try:
                    style_score, violations = self._analyze_code_style(temp_dir)
                except:
                    pass

                try:
                    if repo is not None:
                        recency_score, days_old = self._analyze_repository_recency(repo)
                except:
                    pass

                # Calculates final score using only completed analyses
                final_score = self._calculate_partial_weighted_score(
                    function_score, style_score, recency_score
                )

                self.function_length_score = function_score if function_score is not None else 0.5
                self.style_score = style_score if style_score is not None else 0.5
                self.recency_score = recency_score if recency_score is not None else 0.5
                self.total_functions = self._count_total_functions(temp_dir) if temp_dir else 0
                self.style_violations = violations
                self.days_since_last_commit = days_old

                if os.name != 'nt':
                    signal.alarm(0)  # Cancel the alarm

                self.latency = int((time.time() - start_time) * 1000)
                self.score = max(0.0, min(1.0, final_score))
                return self.score

        except TimeoutError:
            # Timeout occurred - return with whatever scores were actually calculated
            if os.name != 'nt':
                signal.alarm(0)

            final_score = self._calculate_partial_weighted_score(
                function_score, style_score, recency_score
            )

            self.function_length_score = function_score if function_score is not None else 0.5
            self.style_score = style_score if style_score is not None else 0.5
            self.recency_score = recency_score if recency_score is not None else 0.5
            self.total_functions = 0
            self.style_violations = violations
            self.days_since_last_commit = days_old

            self.latency = int((time.time() - start_time) * 1000)
            self.score = max(0.0, min(1.0, final_score))
            return self.score

        except Exception:
            if os.name != 'nt':
                signal.alarm(0)
            self.latency = int((time.time() - start_time) * 1000)
            self.score = 0.5
            return self.score

    def _clone_repository(self, repo_url: str, temp_dir: str, timeout: int = 5) -> Optional[Repo]:
        # clone repo using GitPython library with timeout
        import signal
        import os

        def timeout_handler(_signum, _frame):
            raise TimeoutError("Repository cloning timed out")

        try:
            if os.name != 'nt': # not Windows based
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)

            try:
                repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True, branch='main')
            except git.exc.GitCommandError:
                try:
                    repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True, branch='master')
                except git.exc.GitCommandError:
                    repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)

            if os.name != 'nt':
                signal.alarm(0)  # Cancel the alarm

            return repo

        except TimeoutError:
            if os.name != 'nt':
                signal.alarm(0)
            # Check if partial clone exists
            if os.path.exists(temp_dir) and os.listdir(temp_dir):
                try:
                    return Repo(temp_dir)
                except:
                    return None
            return None
        except Exception:
            if os.name != 'nt':
                signal.alarm(0)
            raise ValueError(f"Failed to clone repository: {repo_url}")

    def _analyze_function_lengths(self, repo_path: str) -> float:
        # scores function lengths in code files
        python_files = list(Path(repo_path).rglob("*.py"))
        if not python_files:
            return 0.5

        # Sample files if too many to speed up analysis
        if len(python_files) > 50:
            import random
            python_files = random.sample(python_files, 50)

        total_functions = 0
        long_functions = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            func_length = node.end_lineno - node.lineno
                            if func_length > self.max_function_lines:
                                long_functions += 1

            except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
                continue

        if total_functions == 0:
            return 0.5

        good_functions = total_functions - long_functions
        return good_functions / total_functions

    def _analyze_code_style(self, repo_path: str) -> tuple:
        # Returns tuple of (style_score, violation_count)

        try:
            result = subprocess.run(
                ['flake8', repo_path, '--count', '--statistics', '--max-line-length=100', '--ignore=E501,W503,E203'],
                capture_output = True,
                text = True,
                timeout = 10
            )

            violations = 0
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and line[0].isdigit():
                        violations += int(line.split()[0])

            total_lines = self._count_python_lines(repo_path)

            # neutral score if no lines detected
            if total_lines == 0:
                return 0.5, violations

            violation_rate = violations / total_lines
            style_score = max(0.0, 1.0 - (violation_rate * 10))

            return style_score, violations

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return 0.5, 0

    def _analyze_repository_recency(self, repo: Repo) -> tuple:
        # scores based on how recently the repository was updated.
       
        try:
            latest_commit = next(repo.iter_commits(max_count=1))
            commit_date = datetime.fromtimestamp(latest_commit.committed_date)

            days_old = (datetime.now() - commit_date).days

            if days_old <= 0:
                recency_score = 1.0
            elif days_old >= self.max_days_old:
                recency_score = 0.0
            else:
                recency_score = 1.0 - (days_old / self.max_days_old)

            return recency_score, days_old

        except Exception:
            return 0.1, 999 # low score, very old

    def _calculate_weighted_score(self, function_score: float, style_score: float,
                                 recency_score: float) -> float:
        return (function_score * 0.4) + (style_score * 0.4) + (recency_score * 0.2)

    def _calculate_partial_weighted_score(self, function_score, style_score, recency_score) -> float:
        completed_analyses = []
        total_weight = 0
        weighted_sum = 0

        if function_score is not None:
            completed_analyses.append(('function', function_score, 0.4))
            total_weight += 0.4
            weighted_sum += function_score * 0.4

        if style_score is not None:
            completed_analyses.append(('style', style_score, 0.4))
            total_weight += 0.4
            weighted_sum += style_score * 0.4

        if recency_score is not None:
            completed_analyses.append(('recency', recency_score, 0.2))
            total_weight += 0.2
            weighted_sum += recency_score * 0.2

        if total_weight == 0:
            return 0.5

        return weighted_sum / total_weight

    def _count_total_functions(self, repo_path: str) -> int:
        # counts total number of functions in the repo
        python_files = list(Path(repo_path).rglob("*.py"))

        # Sample files if too many to speed up analysis
        if len(python_files) > 50:
            import random
            python_files = random.sample(python_files, 50)

        total_functions = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1

            except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
                continue

        return total_functions

    def _count_python_lines(self, repo_path: str) -> int:
        # counts total lines of Python code
        python_files = list(Path(repo_path).rglob("*.py"))

        if len(python_files) > 50:
            import random
            python_files = random.sample(python_files, 50)

        total_lines = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except (UnicodeDecodeError, FileNotFoundError):
                continue

        return total_lines


