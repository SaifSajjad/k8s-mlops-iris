# Serving image

Build directly inside minikube's docker so the cluster can use it:

```bash
eval $(minikube docker-env)
docker build -t iris-serving:latest serving/
```

The container runs `mlflow models serve` and pulls the **Production** model
from the in-cluster MLflow registry. Endpoints: `/ping` (health), `/invocations` (predict).
