variable "kube_context" {
  description = "kubeconfig context to use"
  type        = string
  default     = "minikube"
}

variable "namespace" {
  description = "Kubernetes namespace for the project"
  type        = string
  default     = "mlops"
}

variable "minikube_cpus" {
  type    = number
  default = 2
}

variable "minikube_memory" {
  type    = string
  default = "3000"
}

variable "apply_manifests" {
  description = "If true, terraform also runs 'kubectl apply -k' on the manifests"
  type        = bool
  default     = false
}
