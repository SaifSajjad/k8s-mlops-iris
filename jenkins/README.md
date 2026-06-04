# Jenkins setup (local)

1. Run Jenkins (Docker): `docker run -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts`
2. Install plugins: Git, Pipeline, Docker Pipeline, Kubernetes CLI.
3. The Jenkins agent must have on PATH: terraform, kubectl, minikube, docker, python3.
4. New Item -> Pipeline -> "Pipeline script from SCM" -> point to this repo -> Script path `jenkins/Jenkinsfile`.
5. Build. Stages: Terraform -> Build image -> Train+Register -> Deploy+Verify.
