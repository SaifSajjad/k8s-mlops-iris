# Assignment Checklist — K8s Cluster Deployment (Project 03)

Source of truth: `Project_03_6th_K8s_Deployment.pdf`
Status keys: `[ ]` todo · `[~]` in progress · `[x]` done

## 0. Scaffold & docs
- [x] Repo structure created
- [x] `docs/ASSIGNMENT_CHECKLIST.md`
- [x] `docs/PROJECT_CONTEXT.md`
- [x] `.gitignore`, `.env.example`, README skeleton

## 1. Terraform setup (PDF 1.1–2.4)
- [x] `infra/main.tf`
- [x] `infra/variables.tf`
- [x] `infra/providers.tf` (Kubernetes provider — local-first)
- [x] `terraform init` runs clean
- [x] `terraform plan` runs clean
- [x] `terraform apply` provisions namespace + cluster resources

## 2. Kubernetes / Minikube (PDF 3.1–3.4)
- [x] Minikube install + start documented (scripts + terraform)
- [x] `manifests/` with Kustomize base + local overlay
- [x] `kubectl apply -k manifests/overlays/local`
- [x] All pods Running (`kubectl get pods`)
- [x] Exposure via port-forward and Nginx/Ingress

## 3. ML pipeline (PDF 4.1–4.7)
- [x] Iris dataset preprocessing component
- [x] Train component (scikit-learn) → model artifact
- [x] Evaluate component → metrics
- [x] Package component
- [x] Kubeflow Pipelines SDK → compiled `iris_pipeline.yaml` (generated)
- [x] Output metrics + model artifacts captured (train.py + KFP)

## 4. Model registry (PDF 5.1–5.2)
- [x] Register model in MLflow Model Registry (train.py)
- [x] Stage transition: Staging → Production (promote.py)

## 5. Deployment (PDF 6.1–7.9)
- [x] MLflow serving (serving/Dockerfile)
- [x] K8s Deployment manifest
- [x] 3 replicas (overlay; scale to 5 supported)
- [x] Pod distribution check (scripts/verify-pods.sh)
- [x] Nginx Ingress load balancing

## 6. Automation & delivery (PDF page 1 + 7)
- [x] Jenkins pipeline (`jenkins/Jenkinsfile`)
- [x] GitHub-ready repo (.gitignore, .env.example)
- [x] Final README with run instructions
- [x] Screen-recording demo checklist (docs/DEMO_CHECKLIST.md)
- [x] GitHub repository pushed: https://github.com/SaifSajjad/k8s-mlops-iris
- [ ] Screen-recording video provided (your step)

## Notes / open questions
- Final environment recorded: Windows PowerShell; Docker Desktop 29.5.2; Minikube v1.38.1 with 3000 MB; kubectl v1.34.1; Terraform v1.15.5; Python 3.11.9 venv; MLflow 2.16.2; scikit-learn 1.5.2; kfp 2.9.0.
- Deployment scope: three `iris-serving` replicas run on one local Minikube node; do not describe this as multi-node distribution.
- Model metrics: `iris-classifier v1 Production`, `accuracy=0.9667`, `f1=0.9666`.
- Local endpoints: MLflow UI `http://127.0.0.1:5002`; serving `http://127.0.0.1:5001`; `/ping` HTTP 200; `/invocations` returns `{"predictions": [0, 2]}`.
- Ingress: host `iris.local`, Minikube IP `192.168.49.2`, required Windows hosts entry `192.168.49.2 iris.local`; direct Minikube IP timed out from Windows, so `/predict` and `/mlflow` were verified via ingress-controller port-forward `http://127.0.0.1:8080`.
- Kubeflow: `pipeline/iris_pipeline.yaml` compiled YAML verified, 10,212 bytes; heavy local Kubeflow UI installation intentionally skipped for local-first submission scope.
- Jenkins: `jenkins/Jenkinsfile` exists; Jenkins executable/service was not installed locally; Jenkinsfile reviewed with no obvious blocking issue for a Unix/Linux-style Jenkins agent.
- Runtime reverified on 2026-06-04: existing Minikube profile restored with `--memory=3000`; node Ready, MLflow `1/1`, iris-serving `3/3`, ingress present.
- Kubeflow compiled YAML reverified on 2026-06-04: `pipeline/iris_pipeline.yaml` present.
- MLflow and serving reverified on 2026-06-04: `iris-classifier v1 Production`, `/ping` HTTP 200, prediction `{"predictions": [0, 2]}`.
- Ingress reverified on 2026-06-04: `/predict` fixed to rewrite to `/invocations`; Nginx route returned `{"predictions": [0, 2]}` via ingress-controller port-forward. Windows hosts entry still needed for `iris.local`.
- Git safety reverified on 2026-06-04: duplicate nested project directory unstaged and ignored; exact safety regex only flags `.env.example`, which contains placeholders.
- PDF 2.3 mentions Kind module as an alternative; instructions say **Minikube** → using Minikube, Terraform manages in-cluster resources via the Kubernetes/Helm providers.
- Cloud (AWS/VPC/S3) is optional in PDF → skipped for local-first unless you say otherwise.
