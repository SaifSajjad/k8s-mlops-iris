# K8s MLOps Deployment — Iris Classifier

Local-first MLOps project: **Terraform + Minikube + Kubeflow Pipelines + MLflow
(registry) + MLflow model serving (3 replicas) + Nginx Ingress + Jenkins**.

GitHub repository: https://github.com/SaifSajjad/k8s-mlops-iris

## Verified submission state
- Runtime: Windows PowerShell, Docker Desktop 29.5.2, Minikube v1.38.1 with 3000 MB memory, kubectl v1.34.1, Terraform v1.15.5.
- Python venv: Python 3.11.9 with MLflow 2.16.2, scikit-learn 1.5.2, kfp 2.9.0.
- Kubernetes: node Ready; MLflow pod `1/1 Running`; `iris-serving` deployment `3/3 Running`.
- Serving replicas: three replicas on one local Minikube node; this is not a multi-node cluster.
- Model registry: `iris-classifier v1` in Production; `accuracy=0.9667`, `f1=0.9666`.
- Local endpoints: MLflow UI `http://127.0.0.1:5002`; serving `http://127.0.0.1:5001`; `/ping` HTTP 200; `/invocations` returns `{"predictions": [0, 2]}`.
- Ingress: host `iris.local`, Minikube IP `192.168.49.2`, Windows hosts entry `192.168.49.2 iris.local`. Direct Minikube IP access timed out from Windows, so Nginx routing was validated through `http://127.0.0.1:8080`; `/predict` and `/mlflow` returned HTTP 200.
- Kubeflow: `pipeline/iris_pipeline.yaml` verified, 10,212 bytes. Heavy local Kubeflow UI installation was skipped intentionally because the compiled artifact satisfies the local-first submission scope.
- Jenkins: `jenkins/Jenkinsfile` exists. Jenkins executable/service was not installed locally; Jenkinsfile was reviewed with no obvious blocking issue for a Unix/Linux-style Jenkins agent. Live Jenkins runtime execution remains a documented local limitation.
- Git: initial GitHub push completed successfully on branch `main`; remote `https://github.com/SaifSajjad/k8s-mlops-iris.git`.

## Prerequisites
docker · minikube · kubectl · terraform · helm (optional) · python 3.10+

## End-to-end run

### 1. Infrastructure (Terraform → Minikube)
```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply -auto-approve     # starts minikube + ingress addon
cd ..
```

### 2. Build the serving image inside minikube
```bash
bash scripts/build-image.sh
```

### 3. Deploy to Kubernetes (Kustomize)
```bash
kubectl apply -k manifests/overlays/local
kubectl -n mlops get pods            # wait until all Running
kubectl -n mlops rollout status deploy/mlflow
```

### 4. ML pipeline + MLflow registry
```bash
# expose MLflow locally
kubectl -n mlops port-forward svc/mlflow 5002:5000 &
pip install -r pipeline/requirements.txt
python pipeline/train.py     # preprocess→train→eval→log→register (Staging)
python pipeline/promote.py   # Staging → Production
```
MLflow UI: http://127.0.0.1:5002

Kubeflow pipeline artifact (upload to a KFP instance → new experiment → run):
```bash
python pipeline/pipeline.py  # produces pipeline/iris_pipeline.yaml
```

### 5. Serve + verify load balancing
```bash
kubectl -n mlops rollout restart deploy/iris-serving
bash scripts/verify-pods.sh          # 3 pods, distribution (assignment 7.8)
kubectl -n mlops port-forward svc/iris-serving 5001:5001 &
bash scripts/predict.sh              # sample prediction
```
Ingress (Nginx LB): add `iris.local` → `minikube ip` in /etc/hosts, then
`curl -H "Host: iris.local" http://$(minikube ip)/predict -d @pipeline/sample_request.json`

On this Windows Docker-driver setup, direct Minikube IP HTTP timed out from the host. For recording, validate ingress through:
```powershell
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```
Then send requests to `http://127.0.0.1:8080/predict` with `Host: iris.local`.

### 6. Automation (Jenkins)
See `jenkins/README.md`. Pipeline script: `jenkins/Jenkinsfile`.

## Structure
| Dir | Purpose |
|-----|---------|
| `infra/` | Terraform (providers, main, variables) |
| `manifests/` | Kustomize base + `overlays/local` |
| `pipeline/` | Kubeflow pipeline + local train/promote scripts |
| `serving/` | MLflow model-server Dockerfile |
| `jenkins/` | Jenkinsfile + setup |
| `scripts/` | helper shell scripts |
| `docs/` | checklist, context, demo script |

## Notes
- Local-first; no cloud needed. Cloud (AWS/VPC/S3) intentionally skipped.
- MLflow stages (`Staging`/`Production`) per the assignment; newer MLflow prefers
  aliases — kept stages because the spec names them explicitly.
