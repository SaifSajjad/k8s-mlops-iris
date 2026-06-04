# 1) Bring up the local Kubernetes cluster (Minikube)
resource "null_resource" "minikube" {
  provisioner "local-exec" {
    command = "minikube start --cpus=${var.minikube_cpus} --memory=${var.minikube_memory} --driver=docker"
  }
}

# 2) Enable the Nginx ingress addon (load balancing)
resource "null_resource" "ingress_addon" {
  depends_on = [null_resource.minikube]
  provisioner "local-exec" {
    command = "minikube addons enable ingress"
  }
}

# 3) Demonstrate the Kubernetes Terraform provider creating a real resource
resource "kubernetes_config_map" "project_metadata" {
  depends_on = [null_resource.minikube]
  metadata {
    name      = "project-metadata"
    namespace = "default"
  }
  data = {
    project = "k8s-mlops-iris"
    managed = "terraform"
  }
}

# 4) Optional: let terraform deploy the app manifests too
resource "null_resource" "apply_manifests" {
  count      = var.apply_manifests ? 1 : 0
  depends_on = [null_resource.ingress_addon]
  provisioner "local-exec" {
    command = "kubectl apply -k ../manifests/overlays/local"
  }
}
