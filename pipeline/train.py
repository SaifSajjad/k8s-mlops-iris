"""Real preprocess -> train -> evaluate -> log -> register (Staging) on MLflow.
Run with the MLflow server reachable (port-forward 5000). See README."""
import os
import mlflow, mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

TRACKING = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris-classifier")

mlflow.set_tracking_uri(TRACKING)
mlflow.set_experiment("iris-classification")

X, y = load_iris(return_X_y=True, as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

with mlflow.start_run() as run:
    clf = LogisticRegression(max_iter=200).fit(Xtr, ytr)
    pred = clf.predict(Xte)
    acc = accuracy_score(yte, pred)
    f1 = f1_score(yte, pred, average="macro")
    mlflow.log_param("max_iter", 200)
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("f1_macro", f1)
    mlflow.sklearn.log_model(clf, artifact_path="model",
                             registered_model_name=MODEL_NAME,
                             input_example=Xte.iloc[:2])
    print(f"accuracy={acc:.4f} f1={f1:.4f} run_id={run.info.run_id}")

# Move the just-registered version to Staging
client = MlflowClient()
latest = max(int(v.version) for v in client.search_model_versions(f"name='{MODEL_NAME}'"))
client.transition_model_version_stage(MODEL_NAME, latest, stage="Staging",
                                      archive_existing_versions=False)
print(f"Registered {MODEL_NAME} v{latest} -> Staging")
