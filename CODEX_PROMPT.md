# Codex Agent Prompt — K8s MLOps (Iris) Project

You are my coding agent inside VS Code. Help me RUN and FINISH this MLOps
project on my local machine. The full code is already written — your job is
execution, debugging, and delivery, not a rewrite.

## What this project is
A local-first MLOps pipeline that deploys an Iris classifier on Kubernetes:
**Terraform → Minikube → Kustomize manifests → Kubeflow pipeline → MLflow
(tracking + model registry) → MLflow model serving (3 replicas) → Nginx Ingress
→ Jenkins automation.** It must end up on GitHub with a screen-recording demo.

## Current status (DONE — do not recreate)
- `infra/` Terraform: providers.tf, main.tf, variables.tf, outputs.tf
- `manifests/` Kustomize: base + overlays/local (namespace, mlflow, serving 3 replicas, ingress)
- `pipeline/` KFP pipeline.py (compiled → iris_pipeline.yaml), train.py (register→Staging), promote.py (→Production)
- `serving/Dockerfile` MLflow model server
- `jenkins/Jenkinsfile` + setup notes
- `scripts/` helpers; `docs/` checklist, context, demo steps
Track progress in `docs/ASSIGNMENT_CHECKLIST.md` and `docs/PROJECT_CONTEXT.md`.

## My machine / assumptions
OS: <fill: Windows/Mac/Linux>. Installed: docker, minikube, kubectl, terraform,
python 3.10+. If any tool is missing, give me the exact install command first.

## What I need you to do
1. Walk me through running the project END TO END using `README.md`, one phase
   at a time. Wait for me to confirm each phase works before the next.
2. When a command errors, read the actual output, find the root cause, and give
   a precise fix (edit the file or give the corrected command). Don't guess.
3. Verify each acceptance check:
   - `terraform apply` brings up minikube + ingress addon
   - `kubectl -n mlops get pods` → all Running
   - MLflow UI shows a run with accuracy/f1, model in Staging then Production
   - 3 `iris-serving` pods, distribution visible (`scripts/verify-pods.sh`)
   - sample prediction returns JSON (`scripts/predict.sh`)
   - Jenkins pipeline goes green
4. Make the repo GitHub-ready: confirm `.gitignore` excludes secrets/state/
   artifacts, then give me the exact `git init / add / commit / push` commands.
5. Help me follow `docs/DEMO_CHECKLIST.md` for the screen recording.

## Working rules
- Be concise and execution-focused. Step-by-step. Ready-to-run commands.
- One phase per response. Stop and let me run it, then report back.
- Do NOT scan the whole repo repeatedly. Read only files relevant to the current step.
- Do NOT output full unchanged files — show only the changed lines / diff.
- Do NOT delete my existing work. Ask before any destructive command
  (`terraform destroy`, `minikube delete`, force pushes, removing files).
- Never print or commit secrets. Use `.env.example`; keep `.env` gitignored.
- If a version mismatch breaks things (kfp / mlflow / k8s API), tell me the
  exact version to pin and how to recompile (`python pipeline/pipeline.py`).
- After each working phase, update `docs/ASSIGNMENT_CHECKLIST.md`.

## Known watch-points
- Build the serving image INSIDE minikube: `eval $(minikube docker-env)` then
  `docker build -t iris-serving:latest serving/` (else ImagePullBackOff).
- MLflow server runs with `--serve-artifacts` so the serving pod can pull
  `models:/iris-classifier/Production`. Train against the same MLflow (port-forward 5000).
- Ingress host is `iris.local` → map it to `minikube ip` in /etc/hosts.

Start by asking which OS I'm on and confirming my installed tool versions, then
begin Phase 1 (Terraform).
