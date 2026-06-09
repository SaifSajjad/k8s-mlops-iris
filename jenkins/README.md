# Jenkins Setup — Windows PowerShell Agent

## Prerequisites (Windows agent machine)

The Windows Jenkins agent must have these tools on `PATH`:

| Tool        | Tested version | Notes |
|-------------|---------------|-------|
| `docker`    | 29.5.2        | Docker Desktop |
| `minikube`  | v1.38.1       | |
| `kubectl`   | v1.34.1       | |
| `terraform` | v1.15.5       | |
| `py`        | Python launcher | Installed with Python for Windows |
| Python 3.11 | 3.11.x         | Accessible via `py -3.11` |

The Python 3.11 venv (`.venv\`) is **created automatically** in the workspace
during stage 7 if it does not exist. `.venv` is gitignored, so a fresh Jenkins
SCM checkout has no venv — this is expected and handled.

Docker Desktop occupies host port **5000** on this machine. MLflow is always
port-forwarded to **5002**. Do not change this.

---

## RECOMMENDED — Native Windows Jenkins

Run Jenkins directly on the Windows host where Docker Desktop and Minikube
are installed. The built-in node (or a local agent) then has full, direct
access to all required host tools without any bridging.

### Download and start Jenkins

```powershell
# Download jenkins.war from https://www.jenkins.io/download/
java -jar jenkins.war --httpPort=8090
```

Port **8090** avoids colliding with the ingress port-forward on 8080.

### Label the built-in node `windows`

The Jenkinsfile uses `agent { label 'windows' }`, so the built-in node (or any
local agent) must carry that label:

1. Jenkins UI → **Manage Jenkins** → **Nodes** → **Built-In Node** → **Configure**
2. Labels: add `windows`
3. Save

Ensure `docker`, `minikube`, `kubectl`, `terraform`, `git`, and `py` (Python
3.11 launcher) are on the `PATH` for the Windows account running Jenkins.

### Create the pipeline job

1. New Item → **Pipeline**
2. Pipeline Definition → **Pipeline script from SCM**
3. SCM: Git — `https://github.com/SaifSajjad/k8s-mlops-iris`
4. Branch: `main`
5. Script Path: `jenkins/Jenkinsfile`
6. Save → **Build Now**

---

## OPTIONAL (advanced) — Docker controller + separate Windows agent

A Jenkins Docker controller (`jenkins/jenkins:lts`, Linux image) **alone cannot
run this Windows Jenkinsfile**. The Linux container cannot:

- execute `powershell` steps
- reach the host Docker Desktop daemon
- access Minikube's kubeconfig or the Minikube Docker socket
- use the workspace-local Windows Python venv

If you want a Docker-based controller, you must connect a **separate, fully
configured Windows machine as a Jenkins agent** labelled `windows` via JNLP:

```powershell
# On the Windows agent machine:
java -jar agent.jar -url http://<controller-host>:8090 `
  -secret <agent-secret> -name windows-agent -workDir C:\jenkins
```

The Docker controller manages the UI and scheduling only; the Windows agent
performs all pipeline execution.

---

## Pipeline stages (15 stages)

| # | Stage | Key command |
|---|-------|-------------|
| 1 | Checkout | `checkout scm` + `Test-Path` validation |
| 2 | Tool Preflight | `Get-Command docker/minikube/kubectl/terraform/py` + `py -3.11 --version` |
| 3 | Terraform Infrastructure | `minikube start` (idempotent) + `update-context` + `addons enable ingress` + `terraform init/validate/apply` |
| 4 | Build Serving Image | `minikube docker-env --shell powershell` → `docker build -t iris-serving:latest serving/` |
| 5 | Deploy Kubernetes Manifests | `kubectl apply -k manifests/overlays/local` + MLflow rollout wait |
| 6 | MLflow Port-Forward | `kubectl port-forward svc/mlflow 5002:5000` + HTTP readiness loop requiring MLflow UI HTTP 200 (12 × 5 s) |
| 7 | Prepare Python Environment | `py -3.11 -m venv .venv` (if missing) + `pip install -r requirements.txt` |
| 8 | Train and Register Model | `.venv\Scripts\python.exe pipeline/train.py` → iris-classifier vN → Staging |
| 9 | Promote to Production | `.venv\Scripts\python.exe pipeline/promote.py` → Production |
| 10 | Deploy Production Model | `kubectl -n mlops rollout restart deploy/iris-serving` + rollout wait |
| 11 | Verify Kubernetes Runtime | `kubectl -n mlops get pods -o wide` + `get deploy` |
| 12 | Serving Smoke Test | `/ping` HTTP 200 + POST `/invocations` → `{"predictions":[0,2]}` |
| 13 | Nginx Ingress Verification | port-forward 8080 → POST `/predict` `Host: iris.local` → `{"predictions":[0,2]}` |
| 14 | Kubeflow Artifact Verification | `Test-Path pipeline\iris_pipeline.yaml` + size check |
| 15 | Success Summary | endpoint summary + `archiveArtifacts pipeline/iris_pipeline.yaml` |

## Windows-specific notes

- All steps use `powershell '''...'''`; no `sh` / `bash` / `eval` anywhere.
- Minikube Docker env: `& minikube -p minikube docker-env --shell powershell | Invoke-Expression`
- Sleep: `Start-Sleep -Seconds N`
- Port-forward check: `Get-NetTCPConnection -LocalPort N -State Listen`
- Background port-forwards: `Start-Process -WindowStyle Hidden -FilePath 'kubectl' -ArgumentList ...`
- `post.always` uses `powershell(returnStatus: true, ...)` — a transient kubectl failure
  in cleanup does not hide the true pipeline result.

## Unix/Linux agent

See `jenkins/Jenkinsfile.unix.example` for the original 4-stage Unix reference.
