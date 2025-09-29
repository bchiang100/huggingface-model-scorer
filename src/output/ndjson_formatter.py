import json
from typing import Dict, Any, List

def output_results(results: List[Dict[str, Any]]) -> None:
    """

    Output model results to stdout in NDJSON format as required by the project spec.

    """
    for result in results:
        ndjson_line = format_model_ndjson(result)
        print(ndjson_line)
        
def format_model_ndjson(model_result: Dict[str, Any]) -> str:
    """
    Format a single model result as NDJSON according to project specifications.

    """
    required_fields = {
        "name": model_result.get("name", ""),
        "category": model_result.get("category", "MODEL"),
        "net_score": model_result.get("net_score", 0.0),
        "net_score_latency": model_result.get("net_score_latency", 0),
        "ramp_up_time": model_result.get("ramp_up_time", 0.0),
        "ramp_up_time_latency": model_result.get("ramp_up_time_latency", 0),
        "bus_factor": model_result.get("bus_factor", 0.0),
        "bus_factor_latency": model_result.get("bus_factor_latency", 0),
        "performance_claims": model_result.get("performance_claims", 0.0),
        "performance_claims_latency": model_result.get("performance_claims_latency", 0),
        "license": model_result.get("license", 0.0),
        "license_latency": model_result.get("license_latency", 0),
        "size_score": model_result.get("size_score", {
            "raspberry_pi": 0.0,
            "jetson_nano": 0.0,
            "desktop_pc": 0.0,
            "aws_server": 0.0
        }),
        "size_score_latency": model_result.get("size_score_latency", 0),
        "dataset_and_code_score": model_result.get("dataset_and_code_score", 0.0),
        "dataset_and_code_score_latency": model_result.get("dataset_and_code_score_latency", 0),
        "dataset_quality": model_result.get("dataset_quality", 0.0),
        "dataset_quality_latency": model_result.get("dataset_quality_latency", 0),
        "code_quality": model_result.get("code_quality", 0.0),
        "code_quality_latency": model_result.get("code_quality_latency", 0)
    }

    return json.dumps(required_fields)

