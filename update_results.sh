#!/bin/sh
set -e
$HOME/github.com/loicbourgois/em/v5/update_readme.sh
$HOME/github.com/loicbourgois/em/v6/update_readme.sh
cp $HOME/github.com/loicbourgois/em/v5/README.md \
    $HOME/github.com/loicbourgois/em/README.md
