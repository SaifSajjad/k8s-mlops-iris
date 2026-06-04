#!/usr/bin/env bash
# Shows pod distribution across nodes (assignment 7.8)
kubectl -n mlops get pods -o wide
echo "---"
kubectl -n mlops get deploy,svc,ingress
