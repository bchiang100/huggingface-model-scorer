import argparse
import sys
import pathlib
import subprocess
import dotenv
import time
from src.output.ndjson_formatter import output_results
from src.metrics import (
    busfactor,
    code_quality,
    dataset_quality,
    documentation,
    license,
    performance_claims,
    ramp_up,
    size
)
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
    test_code_quality.run,
    test_dataset_quality.run,
    test_documentation.run,
    test_license.run,
    test_performance_claims.run,
    test_ramp_up.run,
    test_size.run
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
    for x in p.model_asset_groups:
        start = time.perf_counter()
        netscore = 0.0 
        cqc = 0.0
        bfc = 0.0
        dqd = 0.0
        lsm = 0.0
        szm = 0.0
        psm = 0.0 
        bfm = 0.0
        rum = 0.0

        if c := x.codebase:
            cqc = code_quality.CodeQuality(c)
            bfc = busfactor.BusFactorMetric(c)
            cqc.calculate()
            bfc.calculate()
            
        if d := x.dataset:
            dqd = dataset_quality.DatasetQualityMetric(d)
            dqd.calculate()

        if m := x.model:
            lsm = license.License(m)
            szm = size.SizeScore(m)
            psm = performance_claims.PerformanceClaimsScore(m)
            bfm = busfactor.BusFactorMetric(m)
            rum = ramp_up.RampUpScore(m)
            lsm.calculate()
            szm.calculate()
            psm.calculate()
            bfm.calculate()
            rum.calculate()

        end = time.perf_counter()
        netscore = 0.25 * dqd.score + 0.1 * cqc.score + 0.2 * lsm.score + 0.2 * rum.score + 0.1 * szm.score + 0.1 * psm.score + 0.05 * (bfc.score + bfm.score )/2
        netscore_lat = end - start

        code_and_data = 1 if cqc.score and dqd.score else (0.5 if bool(cqc.score) ^ bool(dqd.score) else 0)

        results = {
            "name": f"{x.model.owner},{x.model.asset_id}", 
            "category": type(ModelAssets),
            "net_score": netscore,
            "net_score_latency": netscore_lat,
            "ramp_up_time": rum.score,
            "ramp_up_time_latency": rum.latency,
            "bus_factor": (bfc.score + bfm.score) /2,
            "bus_factor_latency": (bfc.latency + bfm.latency)/2,
            "performance_claims": psm.score,
            "performance_claims_latency": psm.latency ,
            "license": lsm.score,
            "license_latency": lsm.latency,
            "size_score": (szm.score , {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 0.0,
                "aws_server": 0.0
            }),
            "size_score_latency": szm.latency,
            "dataset_and_code_score": code_and_data ,
            "dataset_and_code_score_latency": 0,
            "dataset_quality": dqd.score,
            "dataset_quality_latency": dqd.latency,
            "code_quality": cqc.score,
            "code_quality_latency": cqc.latency
        }

        output_results(list(results))


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
