# Entity Mapping - Gemma 4


## Resources
- https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run


## 
```sh
$HOME/github.com/loicbourgois/em/gemma4/deploy.sh
$HOME/github.com/loicbourgois/em/gemma4/proxy.sh
$HOME/github.com/loicbourgois/em/gemma4/proxy_2.sh
```

## 
```sh
pyenv install 3.14
cd models
pyenv local 3.14
python --version
# Python 3.14.0
python -m venv .venv314
source .venv314/bin/activate
python --version

pip install --upgrade huggingface_hub
hf login
hf download google/gemma-4-31B-it --local-dir ./gemma-4-31B-it --repo-type model
gsutil -m cp -r ./gemma-4-31B-it gs://$MODEL_BUCKET/
```
