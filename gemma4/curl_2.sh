#!/bin/sh
curl http://localhost:9091/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-4-31B-it",
    "messages": [{"role": "user", "content": "Why is the sky blue?"}],
    "chat_template_kwargs": {
         "enable_thinking": true
     },
     "skip_special_tokens": false
  }'
