output "cluster_context" { value = var.kube_context }
output "namespace"       { value = var.namespace }
output "next_step"       { value = "Run: kubectl apply -k ../manifests/overlays/local" }
