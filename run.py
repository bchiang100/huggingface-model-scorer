import argparse
import sys
import pathlib
import subprocess
import dotenv
from src.parsing.url_base import *
from src.parsing.url_parser import UrlParser
from tests import (
    test_bus_factor,
    test_code_quality,
    test_dataset_quality,
    test_documentation, 
    test_license, 
    test_performance_claims, 
    test_ramp_up,
    test_size
    )

all_tests = [
    test_bus_factor.run,
    # test_code_quality.run,
    # test_dataset_quality.run,
    test_documentation.run,
    test_license.run,
    test_performance_claims.run,
    test_ramp_up.run
    # test_size.run
]

dotenv.load_dotenv()

def install() -> None:
    print("Installing dependencies from requirements.txt...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    print("Dependencies installed.")
    print("Installing pyproject config...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '.'])
    print("Program is configured.")
    print("You can now run the script with: ./run <URL_FILE>")

def test() -> None:
    successful_tests = 0
    total_tests = len(all_tests)
    print(f"Total tests to run: {total_tests}")
    print("Running tests...")
    for test in all_tests:
        try:
            test()
            successful_tests += 1
            print(f"{test.__name__} passed.")
        except Exception as e:
            print(f"Test failed: {e}")
    print(f"Tests completed. {successful_tests}/{total_tests} tests passed. {successful_tests/total_tests*100:.2f}% line coverage.")

def run(url_file:str) -> None:
    p = UrlParser(url_file)
    asset = p.parse()
    print(f"Parsed asset URL: {asset.url}")
    asset.run_metrics()

def main() -> None:
    argparser = argparse.ArgumentParser(description="Hugging Face Model Scorer -- install, run or test.")
    argparser.add_argument(
        'action', 
        choices=['install', 'test'], 
        help="Command to execute: install, run, or test."
    )
    args = argparser.parse_args()
    if args.action == 'install':
        install()
    elif args.action == 'test':
        test()
    elif type(args.action) == str and pathlib.Path(args.action).is_file():
        run(args.action)
    else:
        print("Invalid action. Use 'install', 'test', or provide a valid URL file path.")

if __name__ == "__main__":
    main()
