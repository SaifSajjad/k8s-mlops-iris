"""Transition the latest Staging model version to Production."""
import os
from mlflow.tracking import MlflowClient

MODEL_NAME = os.getenv("MODEL_NAME", "iris-classifier")
os.environ.setdefault("MLFLOW_TRACKING_URI", "http://localhost:5000")
client = MlflowClient()

staging = [v for v in client.search_model_versions(f"name='{MODEL_NAME}'")
           if v.current_stage == "Staging"]
if not staging:
    raise SystemExit("No model version in Staging. Run train.py first.")
v = max(staging, key=lambda x: int(x.version))
client.transition_model_version_stage(MODEL_NAME, v.version, stage="Production",
                                      archive_existing_versions=True)
print(f"Promoted {MODEL_NAME} v{v.version}: Staging -> Production")
