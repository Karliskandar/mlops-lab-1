import argparse
import math
import os

import mlflow
from mlflow import MlflowClient

MODEL_NAME = "food11"
TEST_SIZE = 1055

MLFLOW_TRACKING_URI = os.environ.get(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a Food-11 model candidate"
    )
    parser.add_argument(
        "--version",
        required=True,
        type=int,
        help="Candidate model version",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    candidate = client.get_model_version(
        MODEL_NAME,
        str(args.version),
    )

    champion = client.get_model_version_by_alias(
        MODEL_NAME,
        "champion",
    )

    candidate_run = client.get_run(candidate.run_id)
    champion_run = client.get_run(champion.run_id)

    candidate_accuracy = candidate_run.data.metrics["test_accuracy"]
    champion_accuracy = champion_run.data.metrics["test_accuracy"]

    standard_error = math.sqrt(
        champion_accuracy
        * (1 - champion_accuracy)
        / TEST_SIZE
    )

    threshold = champion_accuracy + 2 * standard_error

    print(f"Candidate version: {candidate.version}")
    print(f"Candidate accuracy: {candidate_accuracy:.6f}")
    print(f"Champion version: {champion.version}")
    print(f"Champion accuracy: {champion_accuracy:.6f}")
    print(f"Standard error: {standard_error:.6f}")
    print(f"Promotion threshold: {threshold:.6f}")

    if candidate_accuracy >= threshold:
        decision = "promoted"

        client.set_registered_model_alias(
            MODEL_NAME,
            "champion",
            candidate.version,
        )

        print("Decision: PROMOTED TO CHAMPION")
    else:
        decision = "challenger"

        client.set_registered_model_alias(
            MODEL_NAME,
            "challenger",
            candidate.version,
        )

        print("Decision: KEPT AS CHALLENGER")

    tags = {
        "promotion_decision": decision,
        "candidate_accuracy": str(candidate_accuracy),
        "champion_accuracy": str(champion_accuracy),
        "promotion_threshold": str(threshold),
        "standard_error": str(standard_error),
    }

    for key, value in tags.items():
        client.set_model_version_tag(
            MODEL_NAME,
            candidate.version,
            key,
            value,
        )


if __name__ == "__main__":
    main()