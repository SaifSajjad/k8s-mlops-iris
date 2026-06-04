# Screen-recording demo checklist

Use this final recording order; narrate each step briefly.

Before recording, keep these non-blocking port-forward windows open:

- `kubectl -n mlops port-forward svc/mlflow 5002:5000`
- `kubectl -n mlops port-forward svc/iris-serving 5001:5001`
- `kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80`

1. Show GitHub repository structure: https://github.com/SaifSajjad/k8s-mlops-iris
2. Show Terraform files:
   - `infra/main.tf`
   - `infra/providers.tf`
   - `infra/variables.tf`
3. Run:
   ```powershell
   terraform output
   ```
4. Run:
   ```powershell
   kubectl get nodes
   ```
5. Run:
   ```powershell
   kubectl -n mlops get pods -o wide
   ```
6. Run:
   ```powershell
   kubectl -n mlops get deploy
   ```
7. Open MLflow UI:
   ```text
   http://127.0.0.1:5002
   ```
8. Show:
   ```text
   iris-classifier v1 Production
   ```
9. Run prediction:
   ```powershell
   $body = Get-Content pipeline/sample_request.json -Raw
   Invoke-WebRequest http://127.0.0.1:5001/invocations `
     -Method POST `
     -ContentType "application/json" `
     -Body $body `
     -UseBasicParsing
   ```
10. Show prediction:
    ```json
    {"predictions": [0, 2]}
    ```
11. Run:
    ```powershell
    kubectl -n mlops get ingress
    ```
12. Show ingress request through controller port-forward:
    ```text
    http://127.0.0.1:8080/predict
    ```
13. Show:
    ```text
    pipeline/iris_pipeline.yaml
    ```
14. Show:
    ```text
    jenkins/Jenkinsfile
    ```
15. Show:
    ```powershell
    git log --oneline -n 3
    ```
16. Show:
    ```powershell
    git remote -v
    ```
