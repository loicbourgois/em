#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/em
# python3.10 -m venv .venv310
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 \
#     -m pip install --upgrade pip
# # $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m pip install spacy
# # $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m spacy download fr_dep_news_trf
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 \
#     -m pip install -r \
#     $HOME/github.com/loicbourgois/em/requirements.txt
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 \
#     -m pip install git+ssh://git@github.com/lattice-8094/propp.git

# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 \
#     -m pip install $HOME/Downloads/fr_dep_news_trf-3.8.0-py3-none-any.whl

$HOME/github.com/loicbourgois/em/.venv310/bin/python3 \
    -m pip install pyyaml
    