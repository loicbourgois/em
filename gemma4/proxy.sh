#!/bin/sh
set -e
SERVICE_NAME=$(jq -r '.service_name' "$HOME/github.com/loicbourgois/em/gemma4/secrets.json")
PROJECT=$(jq -r '.project' "$HOME/github.com/loicbourgois/em/gemma4/secrets.json")
REGION=$(jq -r '.region' "$HOME/github.com/loicbourgois/em/gemma4/secrets.json")
gcloud run services proxy $SERVICE_NAME \
  --project $PROJECT \
  --region $REGION \
  --port=9090
