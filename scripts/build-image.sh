#!/usr/bin/env bash
set -e
eval $(minikube docker-env)
docker build -t iris-serving:latest serving/
echo "Built iris-serving:latest inside minikube"
