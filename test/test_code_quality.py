import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics.code_quality import CodeQualityMetric
from parsing.url_base import Codebase


class TestCodeQualityMetric(unittest.TestCase):
    def setUp(self):
        self.test_repo = Codebase("https://github.com/bchiang100/huggingface-model-scorer")
        self.metric = CodeQualityMetric(self.test_repo)

    def test_calculate_returns_float(self):
        """Test that calculate returns a float between 0 and 1"""
        score = self.metric.calculate()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_non_codebase_returns_zero(self):
        """Test that non-codebase assets return 0.0"""
        from parsing.url_base import Model
        model = Model("https://huggingface.co/bert-base-uncased")
        model_metric = CodeQualityMetric(model)
        score = model_metric.calculate()
        self.assertEqual(score, 0.0)

    def test_analyze_function_length_no_files(self):
        """Test function length analysis with no Python files"""
        # Mock _get_python_files to return empty list
        original_method = self.metric._get_python_files
        self.metric._get_python_files = lambda: []
        
        score = self.metric._analyze_function_length()
        self.assertEqual(score, 1.0)
        
        # Restore original method
        self.metric._get_python_files = original_method

    def test_analyze_coding_style_no_files(self):
        """Test coding style analysis with no Python files"""
        # Mock _get_python_files to return empty list
        original_method = self.metric._get_python_files
        self.metric._get_python_files = lambda: []
        
        score = self.metric._analyze_coding_style()
        self.assertEqual(score, 1.0)
        
        # Restore original method
        self.metric._get_python_files = original_method

    def test_analyze_function_length_with_sample_code(self):
        """Test function length analysis with sample Python code"""
        sample_code = '''
def short_function():
    return "hello"

def long_function():
    # This is a very long function
    line1 = "test"
    line2 = "test"
    line3 = "test"
    line4 = "test"
    line5 = "test"
    line6 = "test"
    line7 = "test"
    line8 = "test"
    line9 = "test"
    line10 = "test"
    line11 = "test"
    line12 = "test"
    line13 = "test"
    line14 = "test"
    line15 = "test"
    line16 = "test"
    line17 = "test"
    line18 = "test"
    line19 = "test"
    line20 = "test"
    line21 = "test"
    line22 = "test"
    line23 = "test"
    line24 = "test"
    line25 = "test"
    line26 = "test"
    line27 = "test"
    line28 = "test"
    line29 = "test"
    line30 = "test"
    line31 = "test"
    line32 = "test"
    line33 = "test"
    line34 = "test"
    line35 = "test"
    line36 = "test"
    line37 = "test"
    line38 = "test"
    line39 = "test"
    line40 = "test"
    line41 = "test"
    line42 = "test"
    line43 = "test"
    line44 = "test"
    line45 = "test"
    line46 = "test"
    line47 = "test"
    line48 = "test"
    line49 = "test"
    line50 = "test"
    line51 = "test"
    return "very long"
'''
        
        # Mock _get_python_files to return sample code
        original_method = self.metric._get_python_files
        self.metric._get_python_files = lambda: [sample_code]
        
        score = self.metric._analyze_function_length()
        # Should be 0.5 (1 good function out of 2 total)
        self.assertEqual(score, 0.5)
        
        # Restore original method
        self.metric._get_python_files = original_method

    def test_analyze_coding_style_with_violations(self):
        """Test coding style analysis with style violations"""
        bad_style_code = '''
def bad_function():
    x=1+2;y=3+4
    z = 5 + 6   
    return x,y,z
'''
        
        # Mock _get_python_files to return bad style code
        original_method = self.metric._get_python_files
        self.metric._get_python_files = lambda: [bad_style_code]
        
        score = self.metric._analyze_coding_style()
        # Should be less than 1.0 due to style violations
        self.assertLess(score, 1.0)
        
        # Restore original method
        self.metric._get_python_files = original_method


if __name__ == '__main__':
    unittest.main()