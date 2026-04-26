#!/bin/zsh
set -e
cd $HOME/github.com/loicbourgois
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m pip install spacy
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m spacy download fr_dep_news_trf
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m spacy --help
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m spacy validate
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m em.main_v2
# $HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m em.main_v3
$HOME/github.com/loicbourgois/em/.venv310/bin/python3 -m em.main_v4
# BOT_MANIFEST="$HOME/gitlab.com/loicbourgois/bot/Cargo.toml"
# cargo run --release --manifest-path $BOT_MANIFEST -- td $HOME/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/0.md &
# cargo run --release --manifest-path $BOT_MANIFEST -- td $HOME/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/1.md &
# cargo run --release --manifest-path $BOT_MANIFEST -- td $HOME/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/2.md &
# cargo run --release --manifest-path $BOT_MANIFEST -- td $HOME/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/3.md &
# cargo run --release --manifest-path $BOT_MANIFEST -- td $HOME/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/4.md &
# wait
