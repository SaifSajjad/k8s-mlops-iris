# Screen-recording demo checklist

Record these in order; narrate each step briefly.

1. **Repo tour** — show folder structure + README.
2. **Terraform**
   - `cd infra && terraform init`
   - `terraform plan`
   - `terraform apply -auto-approve` → minikube starts, ingress enabled.
   - `kubectl get nodes`
3. **Build image** — `bash scripts/build-image.sh`
4. **Deploy** — `kubectl apply -k manifests/overlays/local`
   - `kubectl -n mlops get pods` → show all Running.
5. **MLflow + pipeline**
   - port-forward MLflow, open http://localhost:5000
   - `python pipeline/train.py` → show run + metrics in UI
   - show model in **Models** tab at **Staging**
   - `python pipeline/promote.py` → refresh UI → **Production**
   - `python pipeline/pipeline.py` → show generated `iris_pipeline.yaml`
6. **Serving + load balancing**
   - `bash scripts/verify-pods.sh` → 3 iris-serving pods + distribution
   - `bash scripts/predict.sh` → JSON predictions returned
   - hit it via Nginx ingress host `iris.local`
7. **Jenkins** — open Jenkins, trigger build, show green stages.
8. **Wrap** — state repo link; confirm everything live on GitHub.
