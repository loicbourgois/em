#!/bin/sh
set -e
cd $HOME/github.com/loicbourgois/em
python3.14 -m venv .venv
$HOME/github.com/loicbourgois/em/.venv/bin/python3 \
    -m pip install --upgrade pip
$HOME/github.com/loicbourgois/em/.venv/bin/python3 \
    -m pip install -r \
    $HOME/github.com/loicbourgois/em/requirements.txt
