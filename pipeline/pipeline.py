"""Kubeflow Pipelines (KFP v2) definition for the Iris workflow.
Compile:  python pipeline.py   ->  produces iris_pipeline.yaml
Upload the YAML to a Kubeflow Pipelines instance, create an experiment, run it.
"""
from kfp import dsl, compiler

BASE = "python:3.10-slim"
PKGS = ["scikit-learn==1.5.2", "pandas==2.2.2", "joblib==1.4.2"]


@dsl.component(base_image=BASE, packages_to_install=PKGS)
def preprocess(train_out: dsl.Output[dsl.Dataset], test_out: dsl.Output[dsl.Dataset]):
    import pandas as pd
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    X, y = load_iris(return_X_y=True, as_frame=True)
    df = X.copy(); df["target"] = y
    tr, te = train_test_split(df, test_size=0.2, random_state=42, stratify=df["target"])
    tr.to_csv(train_out.path, index=False)
    te.to_csv(test_out.path, index=False)


@dsl.component(base_image=BASE, packages_to_install=PKGS)
def train(train_in: dsl.Input[dsl.Dataset], model_out: dsl.Output[dsl.Model]):
    import pandas as pd, joblib
    from sklearn.linear_model import LogisticRegression
    df = pd.read_csv(train_in.path)
    X, y = df.drop(columns=["target"]), df["target"]
    clf = LogisticRegression(max_iter=200).fit(X, y)
    joblib.dump(clf, model_out.path)


@dsl.component(base_image=BASE, packages_to_install=PKGS)
def evaluate(model_in: dsl.Input[dsl.Model], test_in: dsl.Input[dsl.Dataset],
             metrics: dsl.Output[dsl.Metrics]):
    import pandas as pd, joblib
    from sklearn.metrics import accuracy_score, f1_score
    clf = joblib.load(model_in.path)
    df = pd.read_csv(test_in.path)
    X, y = df.drop(columns=["target"]), df["target"]
    pred = clf.predict(X)
    metrics.log_metric("accuracy", float(accuracy_score(y, pred)))
    metrics.log_metric("f1_macro", float(f1_score(y, pred, average="macro")))


@dsl.component(base_image=BASE, packages_to_install=PKGS)
def package(model_in: dsl.Input[dsl.Model], packaged: dsl.Output[dsl.Model]):
    import shutil
    shutil.copy(model_in.path, packaged.path)  # placeholder for real packaging/push


@dsl.pipeline(name="iris-mlops-pipeline",
              description="preprocess -> train -> evaluate -> package")
def iris_pipeline():
    p = preprocess()
    t = train(train_in=p.outputs["train_out"])
    evaluate(model_in=t.outputs["model_out"], test_in=p.outputs["test_out"])
    package(model_in=t.outputs["model_out"])


if __name__ == "__main__":
    compiler.Compiler().compile(iris_pipeline, "iris_pipeline.yaml")
    print("Compiled -> iris_pipeline.yaml")
