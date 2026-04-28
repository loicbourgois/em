#!/bin/zsh
set -e
cd $HOME/github.com/loicbourgois
$HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m em.update_readme
