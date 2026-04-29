#!/bin/sh
set -e


secrets="$HOME/github.com/loicbourgois/em/gemma4/secrets_2.json"


MODEL_NAME=$(jq -r '.model_name' "$secrets")
SERVICE_NAME=$(jq -r '.service_name' "$secrets")
PROJECT=$(jq -r '.project' "$secrets")
REGION=$(jq -r '.region' "$secrets")
MODEL_PATH=$(jq -r '.model_path' "$secrets")
MODEL_BUCKET=$(jq -r '.model_bucket' "$secrets")


# model will be stored at gs://$MODEL_BUCKET/$MODEL_NAME
# in the container it will be mounted to $MODEL_PATH
echo "MODEL_NAME:           $MODEL_NAME"
echo "SERVICE_NAME:         $SERVICE_NAME"
echo "PROJECT:              $PROJECT"
echo "REGION:               $REGION"
echo "MODEL_PATH:           $MODEL_PATH"
echo "MODEL_BUCKET:         $MODEL_BUCKET"
echo "config:               https://console.cloud.google.com/storage/browser/$MODEL_BUCKET/$MODEL_NAME/config.json"


CONTAINER_ARGS=(
    "serve"
    "$MODEL_PATH"
    "--served-model-name=$MODEL_NAME"
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


gcloud beta run deploy "$SERVICE_NAME" \
    --image "us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:gemma4" \
    --project "$PROJECT" \
    --region "$REGION" \
    --execution-environment gen2 \
    --no-allow-unauthenticated \
    --cpu 20 \
    --memory 80Gi \
    --gpu 1 \
    --gpu-type nvidia-rtx-pro-6000 \
    --no-gpu-zonal-redundancy \
    --no-cpu-throttling \
    --max-instances 1 \
    --concurrency 64 \
    --timeout 600 \
    --startup-probe tcpSocket.port=8080,initialDelaySeconds=240,failureThreshold=5,timeoutSeconds=240,periodSeconds=240 \
    --add-volume name=model-cache,type=in-memory,size-limit=20Gi \
    --add-volume name=model-bucket,type=cloud-storage,bucket="$MODEL_BUCKET",readonly=true,mount-options="only-dir=$MODEL_NAME;implicit-dirs=false;cache-dir=cr-volume:model-cache" \
    --add-volume-mount volume=model-bucket,mount-path=$MODEL_PATH \
    --add-volume-mount volume=model-cache,mount-path=/mnt/model-cache \
    --command "vllm" \
    --args="$(IFS=','; echo "${CONTAINER_ARGS[*]}")"
