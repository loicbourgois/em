#!/bin/sh
set -e
secrets="$HOME/github.com/loicbourgois/em/gemma4/secrets_2.json"
MODEL_NAME=$(jq -r '.model_name' "$secrets")
SERVICE_NAME=$(jq -r '.service_name' "$secrets")
PROJECT=$(jq -r '.project' "$secrets")
REGION=$(jq -r '.region' "$secrets")
echo "MODEL_NAME:   $MODEL_NAME"
echo "SERVICE_NAME: $SERVICE_NAME"
echo "PROJECT:      $PROJECT"
echo "REGION:       $REGION"
# exit 1
CONTAINER_ARGS=(
    "serve"
    "$MODEL_NAME"
    "--enable-chunked-prefill"
    "--enable-prefix-caching"
    "--generation-config=auto"
    "--enable-auto-tool-choice"
    "--tool-call-parser=gemma4"
    "--reasoning-parser=gemma4"
    "--dtype=bfloat16"
    "--max-num-seqs=64"
    "--gpu-memory-utilization=0.95"
    "--tensor-parallel-size=1"
    "--port=8080"
    "--host=0.0.0.0"
)
gcloud beta run deploy $SERVICE_NAME \
    --image "us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:gemma4" \
    --project $PROJECT \
    --region $REGION \
    --execution-environment gen2 \
    --no-allow-unauthenticated \
    --cpu 20 \
    --memory 80Gi \
    --gpu 1 \
    --gpu-type nvidia-rtx-pro-6000 \
    --no-gpu-zonal-redundancy \
    --no-cpu-throttling \
    --max-instances 3 \
    --concurrency 64 \
    --timeout 600 \
    --startup-probe tcpSocket.port=8080,initialDelaySeconds=240,failureThreshold=5,timeoutSeconds=240,periodSeconds=240 \
    --command "vllm" \
    --args=$(IFS=','; echo "${CONTAINER_ARGS[*]}")
