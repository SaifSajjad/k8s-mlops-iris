# Jenkins Pipeline Verification — K8s MLOps Iris

Verification date: 2026-06-09 (updated 2026-06-09)
Environment: Windows 11 Pro Education, PowerShell, Docker Desktop 29.5.2,
Minikube v1.38.1 (3000 MB), kubectl v1.34.1, Terraform v1.15.5,
Python 3.11.9 (via `py -3.11`; venv created automatically in pipeline)

**Jenkins agent:** `agent { label 'windows' }` — requires a native Windows
Jenkins agent. A Linux Docker controller alone cannot run this pipeline.

---

## 1. Jenkins Stage Table

| # | Stage | Purpose | Main Command | Expected Output |
|---|-------|---------|--------------|-----------------|
| 1 | Checkout | Clone repo + validate required files exist | `checkout scm` + `Test-Path` for each required file | "Workspace validation passed." |
| 2 | Tool Preflight | Confirm docker, minikube, kubectl, terraform, py launcher on PATH; Python 3.11 available via `py -3.11`; Docker daemon reachable. Does NOT check .venv (created in stage 7). | `Get-Command docker/minikube/kubectl/terraform/py` + `py -3.11 --version` | All tools found; Docker daemon version printed |
| 3 | Terraform Infrastructure | Idempotent Minikube start/update-context/ingress enable, then Terraform provisioning | `minikube start --driver=docker --cpus=2 --memory=3000` + `update-context` + `addons enable ingress` + `terraform init/validate/apply` (in `infra/`) | Minikube running; Apply complete |
| 4 | Build Serving Image | Build `iris-serving:latest` inside Minikube's Docker daemon (prevents ImagePullBackOff) | `& minikube -p minikube docker-env --shell powershell \| Invoke-Expression` then `docker build -t iris-serving:latest serving/` | Successfully built iris-serving:latest |
| 5 | Deploy Kubernetes Manifests | Apply Kustomize overlay; wait for MLflow rollout | `kubectl apply -k manifests/overlays/local` + `kubectl -n mlops rollout status deploy/mlflow --timeout=600s` | deployment "mlflow" successfully rolled out |
| 6 | MLflow Port-Forward | Expose MLflow registry on host port 5002 (port 5000 occupied by Docker Desktop); HTTP readiness loop polls MLflow UI for HTTP 200, up to 12 × 5 s | `Get-NetTCPConnection -LocalPort 5002` check → `Start-Process kubectl port-forward svc/mlflow 5002:5000` → `Invoke-WebRequest http://127.0.0.1:5002` loop (StatusCode 200 required) | MLflow HTTP 200; MLFLOW_TRACKING_URI=http://127.0.0.1:5002 |
| 7 | Prepare Python Env | Create Python 3.11 venv automatically if missing (fresh Jenkins SCM workspace has no .venv because it is gitignored); install pipeline dependencies | `py -3.11 -m venv .venv` (if missing) + `.venv\Scripts\python.exe -m pip install -r pipeline\requirements.txt` | "Python environment ready." |
| 8 | Train and Register Model | Train Iris LogisticRegression, log metrics to MLflow, register as iris-classifier → Staging | `.venv\Scripts\python.exe pipeline/train.py` | `accuracy=0.9667 f1=0.9666`; iris-classifier vN → Staging |
| 9 | Promote to Production | Promote latest Staging version to Production | `.venv\Scripts\python.exe pipeline/promote.py` | "Promoted iris-classifier vN: Staging -> Production" |
| 10 | Deploy Production Model | Restart serving pods so they load the new Production model | `kubectl -n mlops rollout restart deploy/iris-serving` + `rollout status --timeout=600s` | deployment "iris-serving" successfully rolled out |
| 11 | Verify Kubernetes Runtime | Confirm mlflow 1/1 and iris-serving 3/3 Running | `kubectl -n mlops get pods -o wide` + `get deploy` | mlflow 1/1 Running; iris-serving 3/3 Running |
| 12 | Serving Smoke Test | Verify /ping and /invocations on the serving service | `Invoke-WebRequest http://127.0.0.1:5001/ping` + POST to `/invocations` | HTTP 200; `{"predictions": [0, 2]}` |
| 13 | Nginx Ingress Verification | Verify Nginx ingress routes /predict → iris-serving /invocations via Host: iris.local | POST `http://127.0.0.1:8080/predict` with `Host: iris.local` header | `{"predictions": [0, 2]}` |
| 14 | Kubeflow Artifact Verification | Confirm compiled KFP pipeline YAML exists and is non-trivial | `Test-Path pipeline\iris_pipeline.yaml` + size check | "iris_pipeline.yaml — 10212 bytes" |
| 15 | Success Summary | Print endpoint summary; archive KFP artifact | `Write-Host` summary + `archiveArtifacts 'pipeline/iris_pipeline.yaml'` | Summary printed; artifact archived |

---

## 2. End-to-End Flow Confirmation

```
train.py
  -> MLflow experiment: iris-classification
  -> Log: accuracy, f1_macro
  -> Register: iris-classifier vN
  -> Transition: vN -> Staging

promote.py
  -> Find: latest iris-classifier in Staging
  -> Transition: vN -> Production
  -> Archive existing Staging versions

kubectl rollout restart deploy/iris-serving
  -> Pods restart and load: models:/iris-classifier/Production
  -> Readiness probe (/ping) must pass before traffic is served
  -> 3/3 Running confirmed

/ping HTTP 200 -> /invocations {"predictions": [0, 2]}
  -> Ingress /predict (Host: iris.local) -> /invocations {"predictions": [0, 2]}
```

---

## 3. Static Verification Results (2026-06-09)

### File existence checks

| File / Path | Present | Size |
|-------------|---------|------|
| `jenkins/Jenkinsfile` | YES | Windows 15-stage declarative pipeline |
| `jenkins/Jenkinsfile.unix.example` | YES | Original 4-stage Unix reference |
| `pipeline/iris_pipeline.yaml` | YES | 10,212 bytes |
| `pipeline/train.py` | YES | 1,700 bytes |
| `pipeline/promote.py` | YES | 742 bytes |
| `pipeline/requirements.txt` | YES | kfp==2.9.0, mlflow==2.16.2, scikit-learn==1.5.2 |
| `serving/Dockerfile` | YES | python:3.10-slim, mlflow 2.16.2, port 5001 |
| `manifests/overlays/local` | YES | Kustomize overlay (3 replicas) |
| `manifests/base/serving-deployment.yaml` | YES | `MODEL_URI=models:/iris-classifier/Production` |

### train.py analysis

| Requirement | Evidence |
|-------------|----------|
| Reads MLFLOW_TRACKING_URI from env | `TRACKING = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")` line 11 |
| Sets MLflow tracking URI | `mlflow.set_tracking_uri(TRACKING)` line 14 |
| Creates iris-classification experiment | `mlflow.set_experiment("iris-classification")` line 15 |
| Logs accuracy | `mlflow.log_metric("accuracy", acc)` line 26 |
| Logs f1 | `mlflow.log_metric("f1_macro", f1)` line 27 |
| Logs model | `mlflow.sklearn.log_model(...)` line 28 |
| Registers iris-classifier | `registered_model_name=MODEL_NAME` in log_model |
| Transitions to Staging | `client.transition_model_version_stage(MODEL_NAME, latest, stage="Staging")` line 36 |

### promote.py analysis

| Requirement | Evidence |
|-------------|----------|
| Reads MLFLOW_TRACKING_URI | `os.environ.setdefault("MLFLOW_TRACKING_URI", "http://localhost:5000")` — setdefault means env var set by Jenkins (5002) takes precedence |
| Finds Staging version | `[v for v in ... if v.current_stage == "Staging"]` line 9 |
| Promotes to Production | `client.transition_model_version_stage(... stage="Production", archive_existing_versions=True)` line 14 |

### serving-deployment.yaml analysis

| Requirement | Evidence |
|-------------|----------|
| Uses Production model | `MODEL_URI: models:/iris-classifier/Production` env var |
| Connects to in-cluster MLflow | `MLFLOW_TRACKING_URI: http://mlflow:5000` (Kubernetes service name) |
| Readiness probe | `httpGet: { path: /ping, port: 5001 }` |

---

## 4. Runtime Evidence (2026-06-09)

### Kubernetes pod status

```
NAME                           READY   STATUS    RESTARTS   AGE
iris-serving-7c64db95b-qn6fn   1/1     Running   5          6d10h
iris-serving-7c64db95b-z6vc9   1/1     Running   5          6d10h
iris-serving-7c64db95b-zrjdh   1/1     Running   15         6d11h
mlflow-5478fc59cb-s27r2        1/1     Running   4          6d11h

NAME           READY   UP-TO-DATE   AVAILABLE   AGE
iris-serving   3/3     3            3           6d11h
mlflow         1/1     1            1           6d11h
```

### MLflow model registry

```
iris-classifier v1 Production
```

### Serving endpoint tests

```
/ping          => HTTP 200
/invocations   => {"predictions": [0, 2]}
```

Input: `{"dataframe_split": {"columns": ["sepal length (cm)","sepal width (cm)","petal length (cm)","petal width (cm)"], "data": [[5.1,3.5,1.4,0.2],[6.7,3.0,5.2,2.3]]}}`

### Nginx ingress test

```
POST http://127.0.0.1:8080/predict  Host: iris.local
=> {"predictions": [0, 2]}
```

### Kubeflow artifact

```
pipeline/iris_pipeline.yaml   10212 bytes
```

---

## 5. Windows Compatibility Fixes Applied to Jenkinsfile

| Original (Unix / first draft) | Fixed (Windows PowerShell) |
|-------------------------------|---------------------------|
| `sh '...'` (all steps) | `powershell '''...'''` |
| `eval $(minikube docker-env)` | `& minikube -p minikube docker-env --shell powershell \| Invoke-Expression` |
| `sleep 8` | `Start-Sleep -Seconds 8` |
| `MLFLOW_TRACKING_URI = 'http://localhost:5000'` | `MLFLOW_TRACKING_URI = 'http://127.0.0.1:5002'` |
| `port-forward svc/mlflow 5000:5000 &` | `Start-Process -WindowStyle Hidden -FilePath 'kubectl' ...` |
| `source .venv/bin/activate` | `.venv\Scripts\python.exe` called directly |
| `agent any` | `agent { label 'windows' }` — prevents accidental run on Linux controller |
| Preflight checked `.venv` existence | Preflight checks `py` launcher + `py -3.11 --version` only; venv deferred to stage 7 |
| Stage 7 assumed venv existed | Stage 7 runs `py -3.11 -m venv .venv` if missing (handles fresh SCM checkout) |
| Stage 3 had no Minikube pre-check | Stage 3 runs `minikube start/update-context/addons enable ingress` (all idempotent) before Terraform |
| Stage 6 had no readiness wait | Stage 6 HTTP readiness loop (`Invoke-WebRequest http://127.0.0.1:5002`, StatusCode 200, 12 × 5 s) ensures MLflow UI is serving before training begins |
| `post` block used bare `powershell '...'` | `post.always` uses `powershell(returnStatus: true, ...)` so kubectl failures do not mask pipeline result |
| 4 stages | 15 stages |
| No port check before port-forward | `Get-NetTCPConnection -LocalPort N -State Listen` guards each port-forward |
| `curl` (Unix) | `Invoke-WebRequest` (PowerShell) |
| No smoke test | Stages 12 and 13 validate `/ping`, `/invocations`, ingress `/predict` |
| No Kubeflow check | Stage 14 verifies `iris_pipeline.yaml` presence and size |

---

## 6. Honest Limitations

- **Jenkins server not installed locally.** Jenkinsfile was reviewed line-by-line and static-validated. The pipeline has not been executed by a live Jenkins instance.
- **Native Windows Jenkins is the recommended path.** `java -jar jenkins.war --httpPort=8090` on the same Windows machine as Docker Desktop and Minikube. The built-in node (or a local agent) must carry the label `windows`.
- **A Linux Docker controller alone is insufficient.** `docker run ... jenkins/jenkins:lts` without a connected Windows agent cannot run `powershell` steps, access host Docker Desktop, Minikube kubeconfig, or the Windows Python launcher.
- **Fresh Jenkins SCM workspace has no `.venv`.** `.venv/` is gitignored. Stage 7 handles this automatically via `py -3.11 -m venv .venv`.
- **Live pipeline run will create a new MLflow model version** (iris-classifier v2) and promote it to Production. This should only be triggered after explicit user approval. The existing v1 Production deployment remains intact.
- **Terraform apply is idempotent** against the running Minikube cluster; re-running it will update in-cluster resources without destroying the cluster.
- **Port-forward processes** started by `Start-Process` in Jenkins run as children of the agent process and are cleaned up when the agent session ends.

---

## 7. How to Trigger the Live Pipeline

After installing and configuring Jenkins (see `jenkins/README.md`):

1. Open Jenkins UI (e.g. `http://localhost:8090`)
2. New Item → Pipeline → Script from SCM → Git: `https://github.com/SaifSajjad/k8s-mlops-iris` → Script Path: `jenkins/Jenkinsfile`
3. Save → **Build Now**

Or via Jenkins CLI:
```
java -jar jenkins-cli.jar -s http://localhost:8090 build <job-name> -s -v
```

**Do not trigger without explicit approval** — the live run will register iris-classifier v2 and promote it to Production.
