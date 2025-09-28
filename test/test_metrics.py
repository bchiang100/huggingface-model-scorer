# Run: python3 -m test.test_metrics

from src.parsing.url_parser import UrlParser
import os

if __name__ == "__main__":
    parser = UrlParser(os.path.join(os.path.dirname(__file__), 'example.txt'))
    # print([x.model.url for x in parser.model_asset_groups])
    # print([x.dataset.url for x in parser.model_asset_groups])
    # print([x.codebase.url for x in parser.model_asset_groups])
    # print()

    for i, x in enumerate(parser.model_asset_groups):
        has_dataset, has_codebase = False, False

        print(f"Model #{i+1}: {x.model.url}")
        # retrieve all available metrics first
        print("====================\nModel Metrics\n====================")
        model_metrics = x.model.run_metrics()
        if x.dataset.url:
            print("====================\nDataset Metrics\n====================")
            has_dataset = True
            dataset_metrics = x.dataset.run_metrics()
        if x.codebase.url:
            print("====================\nCodebase Metrics\n====================")
            has_codebase = True
            codebase_metrics = x.codebase.run_metrics()
        print()

        # do any calculations for other metrics (i.e. dataset_and_code_score)
        dataset_and_code_score = 0.00
        if has_dataset or has_codebase:
            dcq_sum, weights_sum = 0.00, 0.0
            # 70% dataset, 30% code
            # 85% quality, 15% documentation
            if has_dataset:
                dcq_sum += 0.7*(0.85*dataset_metrics["dataset_quality"] + 0.15*dataset_metrics["dataset_documentation"])
                weights_sum += 0.7
            if has_codebase:
                dcq_sum += 0.3*(0.85*codebase_metrics["code_quality"] + 0.15*codebase_metrics["code_documentation"])
                weights_sum += 0.3
            dataset_and_code_score = dcq_sum/(weights_sum)

        # assemble metrics to expected output format
        output = {
            # "license": model_metrics["license"],
            # "license_latency": model_metrics["license_latency"],
            "dataset_and_code_score": dataset_and_code_score,
            "dataset_and_code_score_latency": 0.0,
            "dataset_quality": dataset_metrics["dataset_quality"],
            "dataset_quality_latency": dataset_metrics["dataset_quality_latency"],
            "code_quality": codebase_metrics["code_quality"],
            "code_quality_latency": codebase_metrics["code_quality_latency"],
        }
        print(output)
        
        print("\n\n\n")