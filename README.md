# Entity Mapping


## Results
        pretagged-gpt-5.5-high  pretagged-gpt-5.5-medium
quart   0.99260                 0.9748
moitie  0.9680
full    0.9497                  

file://./v5/pretagged-quarter-gpt-5.5-medium/00_result.tsv
file://./v5/pretagged-full-gpt-5.5-medium/00_result.tsv
file://./v5/pretagged-quarter-gpt-5.5-high/00_result.tsv
file://./v5/pretagged-half-gpt-5.5-high/00_result.tsv
file://./v5/pretagged-full-gpt-5.5-high/00_result.tsv


## Manual Mapping
```sh
open https://boberle.com/projects/coreference-annotation-with-sacr/online/
# paste your text
# paste follow
    PROP:name=EN
    PER
# untick `Show property warnings`
# parse data
```


## Misc

```sh
b td $HOME/github.com/loicbourgois/em/wip.md
$HOME/github.com/loicbourgois/em/run.sh
```

https://github.com/lattice-8094/litbank/blob/main/litbank-fr/data/Manuel_Annotation_propp.md

que personnages

<la belle seour <du mari de <<ma> mere>>>
<la belle seour de <le mari de <<ma> mere>>>

entité, mentions d'entités 

la tete syntaxique 

https://boberle.com/projects/coreference-annotation-with-sacr/online/

https://lattice-8094.github.io/propp/sacr_dataset_annotation/#annotation-process

https://github.com/lattice-8094/litbank/tree/main/litbank-fr/data

désactivé Show property warnings: 

```sh
PROP:name=EN
PER
```

coreference_resolution_metric

extract_mentions_

generate_tokens_

```sh

$HOME/github.com/loicbourgois/em/.venv310/bin/scorch \
    /Users/loicbourgois/github.com/loicbourgois/em/corbeau_renard/gold/gold.json \
    /Users/loicbourgois/github.com/loicbourgois/em/corbeau_renard/silver/silver.json

diff \
    /Users/loicbourgois/github.com/loicbourgois/em/corbeau_renard/gold/corbeau_renard.sacr.entities \
    /Users/loicbourgois/github.com/loicbourgois/em/corbeau_renard/silver/0.md.gpt-5.5-low.sacr.entities

```

