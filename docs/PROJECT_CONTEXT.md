# Project Context

Living memory for this project. Update after each completed phase.

## What this is
MLOps assignment: deploy an Iris ML model on a local Kubernetes (Minikube)
cluster, provisioned with Terraform, trained via a Kubeflow pipeline, tracked
and registered in MLflow, served with 3–5 replicas behind Nginx, automated by
Jenkins. Must be GitHub-hosted with a screen recording.

## Decisions (the "why")
- **Local-first.** No cloud account assumed. Minikube cluster on the dev machine.
- **Terraform scope.** Manages in-cluster resources (namespace, MLflow via Helm,
  nginx-ingress) on top of a Minikube cluster, using the `kubernetes` + `helm`
  providers. Minikube itself is started by a script / `null_resource`, since
  Terraform has no first-class Minikube provider.
- **Kustomize** for manifests: `base/` + `overlays/local/`.
- **Model:** Iris + scikit-learn LogisticRegression (small, fast, reproducible).
- **Serving:** MLflow model server packaged in a container, run as a K8s
  Deployment (simpler than KServe for a local demo; KServe noted as alt).
- **Load balancing:** Nginx Ingress in front of the serving Service.

## Repo layout
```
infra/        Terraform (.tf files, .env.example)
manifests/    Kustomize base + overlays/local
pipeline/     Kubeflow components + compile script + data
mlflow/       MLflow server manifests / helm values
serving/      Model server Dockerfile + deployment
jenkins/      Jenkinsfile + setup notes
scripts/      helper scripts (minikube up, register model, etc.)
docs/         checklist + this context + demo script
```

## Environment notes
- GitHub repository: https://github.com/SaifSajjad/k8s-mlops-iris
- Runtime used for final verification: Windows PowerShell, Docker Desktop 29.5.2, Minikube v1.38.1 with 3000 MB memory, kubectl v1.34.1, Terraform v1.15.5.
- Python venv: Python 3.11.9, MLflow 2.16.2, scikit-learn 1.5.2, kfp 2.9.0.
- Kubernetes status: node Ready, MLflow pod `1/1 Running`, `iris-serving` deployment `3/3 Running`.
- Serving scope: three replicas on one local Minikube node; do not describe this as multi-node distribution.
- Model: `iris-classifier v1 Production`, `accuracy=0.9667`, `f1=0.9666`.
- Endpoints: MLflow UI `http://127.0.0.1:5002`; serving `http://127.0.0.1:5001`; `/ping` HTTP 200; `/invocations` returns `{"predictions": [0, 2]}`.
- Ingress: host `iris.local`, Minikube IP `192.168.49.2`, required Windows hosts entry `192.168.49.2 iris.local`. Direct Minikube IP access timed out from Windows; Nginx ingress routing was validated through `http://127.0.0.1:8080` with `/predict` and `/mlflow` returning HTTP 200.
- Kubeflow: `pipeline/iris_pipeline.yaml` exists, compiled YAML verified, size 10,212 bytes. Heavy local Kubeflow UI installation intentionally skipped because the compiled artifact satisfies the local-first submission scope.
- Jenkins: `jenkins/Jenkinsfile` exists. Jenkins executable/service was not installed locally; Jenkinsfile reviewed with no obvious blocking issue for a Unix/Linux-style Jenkins agent. Live Jenkins runtime execution remains a documented local limitation.
- Git: initial GitHub push completed successfully, branch `main`, remote `https://github.com/SaifSajjad/k8s-mlops-iris.git`.

## Windows run notes (2026-06-03)
- **Docker Desktop memory:** capped at 3613 MB → use `--memory=3000` for minikube; `infra/variables.tf` default updated to `"3000"`.
- **MLflow port-forward:** Docker Desktop owns `0.0.0.0:5000` (`com.docker.backend`). Forward MLflow to **5002**: `kubectl -n mlops port-forward svc/mlflow 5002:5000`. Always use `127.0.0.1:5002`, not `localhost:5000`.
- **Serving port-forward:** `kubectl -n mlops port-forward svc/iris-serving 5001:5001` → test at `http://127.0.0.1:5001/ping`.
- **Python venv:** Python 3.14 (default) cannot install kfp/mlflow wheels. Use `py -3.11 -m venv .venv`. Activated with `.\.venv\Scripts\Activate.ps1`.
- **Model:** `iris-classifier v1` registered and promoted to **Production**. `accuracy=0.9667, f1=0.9666`.
- **Ingress:** `mlops-ingress` nginx, host `iris.local`, address `192.168.49.2`. Add to hosts file for ingress testing.

## Phase log
- **Phase 0 (done):** scaffold, checklist, context, gitignore, env example, README skeleton.
- **Phase 1 (done):** `terraform init/validate/plan/apply` — minikube v1.38.1 + ingress addon, `kubernetes_config_map.project_metadata` created.
- **Phase 2 (done):** `kubectl apply -k manifests/overlays/local` — all resources created; mlflow `1/1 Running`.
- **Phase 3 (done):** `iris-serving:latest` built inside minikube daemon (838 MB). `train.py` → `iris-classifier v1 Staging`. `promote.py` → Production. All 3 iris-serving pods `1/1 Running`.
- **Phase 4 (done):** `/ping` HTTP 200, `/invocations` returns `{"predictions": [0, 2]}`. Ingress assigned `192.168.49.2`.

- **Handoff Phase 1 verification (2026-06-04):** Docker 29.5.2 OK. Fixed stale Minikube kubeconfig with `minikube update-context`, then started existing Minikube profile with `--memory=3000`. Node Ready, MLflow `1/1 Running`, iris-serving recovered to `3/3 Running`, ingress present at `192.168.49.2`.

- **Handoff Phase 2 verification (2026-06-04):** `pipeline/iris_pipeline.yaml` present, 10,212 bytes, last written 2026-06-03 01:25:51.

- **Handoff Phase 3 verification (2026-06-04):** Started MLflow port-forward on `127.0.0.1:5002` and serving port-forward on `127.0.0.1:5001`. Registry shows `iris-classifier v1 Production`; `/ping` HTTP 200; `/invocations` returns `{"predictions": [0, 2]}`.

- **Handoff Phase 4 verification (2026-06-04):** No Windows hosts entry for `iris.local`; add `192.168.49.2 iris.local` from Administrator PowerShell if direct host testing is needed. Direct Minikube IP HTTP timed out from Windows, so Nginx ingress was validated through `127.0.0.1:8080` port-forward to `ingress-nginx-controller` with `Host: iris.local`. Split ingress rewrites so `/predict` maps to `/invocations`; `/predict` and `/mlflow` both returned HTTP 200.

- **Handoff Phase 5 verification (2026-06-04):** Git initialized and staged for review. `.gitignore` now includes `**/secrets*` and ignores the nested duplicate `k8s-mlops-project/` directory without deleting it. Exact safety regex flags `.env.example`; inspected file contains placeholders only and refined check excluding `.env.example` passes.
- **GitHub delivery (2026-06-04):** Local commit `2e60c37` pushed successfully to `origin/main` at `https://github.com/SaifSajjad/k8s-mlops-iris.git`.

## Next
- Record screen demo following `docs/DEMO_CHECKLIST.md`.
