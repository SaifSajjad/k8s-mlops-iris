terraform {
  required_version = ">= 1.4.0"
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
    null       = { source = "hashicorp/null", version = "~> 3.2" }
  }
}

# Uses the local minikube kubeconfig context.
provider "kubernetes" {
  config_path    = pathexpand("~/.kube/config")
  config_context = var.kube_context
}
