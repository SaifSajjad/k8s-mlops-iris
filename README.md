# K8s MLOps Deployment — Iris Classifier

Local-first MLOps project: **Terraform + Minikube + Kubeflow Pipelines + MLflow
(registry) + MLflow model serving (3 replicas) + Nginx Ingress + Jenkins**.

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
kubectl -n mlops port-forward svc/mlflow 5000:5000 &
pip install -r pipeline/requirements.txt
python pipeline/train.py     # preprocess→train→eval→log→register (Staging)
python pipeline/promote.py   # Staging → Production
```
MLflow UI: http://localhost:5000

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
