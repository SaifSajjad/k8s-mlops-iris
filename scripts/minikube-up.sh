#!/usr/bin/env bash
set -e
minikube start --cpus=2 --memory=4096 --driver=docker
minikube addons enable ingress
kubectl get nodes
