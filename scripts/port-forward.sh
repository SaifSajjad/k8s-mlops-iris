#!/usr/bin/env bash
# MLflow UI on :5000, model API on :5001
kubectl -n mlops port-forward svc/mlflow 5000:5000 &
kubectl -n mlops port-forward svc/iris-serving 5001:5001 &
echo "MLflow http://localhost:5000  |  Model http://localhost:5001"
wait
