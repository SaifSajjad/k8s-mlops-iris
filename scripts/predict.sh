#!/usr/bin/env bash
# Send a sample prediction (needs port-forward on 5001 OR ingress host iris.local)
curl -s -X POST http://localhost:5001/invocations \
  -H "Content-Type: application/json" \
  -d @pipeline/sample_request.json
echo
