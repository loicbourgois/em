#!/bin/sh
set -e
MODEL_NAME=$(jq -r '.model_name' "$HOME/github.com/loicbourgois/em/gemma4/secrets.json")
curl http://localhost:9090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "model": "${MODEL_NAME}",
  "messages": [{"role": "user", "content": "Hello"}],
  "chat_template_kwargs": {
      "enable_thinking": true
  },
  "skip_special_tokens": false
}
EOF
