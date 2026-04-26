# Context


## Mention detection
This is already done for you.
eg: {{la petite fille}} se balade


# Goal


## Extract mentions
Extract all mentions.
They are already flagged, but we wnat to make sure to have them all in the same place.


## Group mentions
Group mentions together into entities


## Map entities
Map mentions to their entities


## sacr
Add back the entities types in the base text.
Export as proper sacr file.


# Rules
- Only work on living things. 
- We don't care about the décor.
- If two groups are refering to the same person, they should be merged together.
- The `flagging` section should have the full input text
  Do not forget any sentence, even if there is no mention of any personnage.
- Only work on active personnage. No general entities.
- Don't process pronons that are part of the verb
  "je me regarde dans la glace" -> "{{je}} me regarde dans la glace"
  "me" is not processed
- Don't process the title of the book
  We are only interested in the story


# Example


## Input
```json
[
    "Une histoire de chat",
    "Édition de référence :",
    "Chatou, Paris, 2076.",
    "{{Je}} suis un chat. Les chats miaulent. {{Je}} miaule aussi.",
    "{{Je}} me balade dans le jardin, et mange des souris.",
    "{{Mes}} moustaches flottent au vent comme des petits cerf-volant.",
    "{{J'}}ai les oreilles pointus, pointées vers {{les oiseaux}}.",
    "{{Je}} mangerai bien {{le plus gros de {{ces moineaux}}}}.",
]
```


## Output
```json
{{
    "mentions_reasoning": "...",
    "mentions": [
        "je",
        "je",
        "je",
        "Mes",
        "J'",
        "les oiseaux",
        "Je",
        "le plus gros de ces moineaux",
        "ces moineaux",
    ],
    "groups_reasoning": "...",
    # Note how each group is unique
    # Note how we give them a description, to facilitate agregation, grouping and mapping
    "groups": {{
        "le_chat": "un chat spécifique, qui raconte l'histoire",
        "les_moineaux": "les oiseux que je chat guette",
        "le_gros_moineau": "le moineau specific que le chat veut",
    }},
    "mapping_reasoning": "...",
    "mapping": [
        ["je", "le_chat"],
        ["je", "le_chat"],
        ["je", "le_chat"],
        ["Mes", "le_chat"],
        ["J'", "le_chat"],
        ["les oiseaux", "les_moineaux"],
        ["Je", "le_chat"],
        ["le plus gros de ces moineaux", "le_gros_moineau"],
        ["ces moineaux", "les_moineaux"],
    ],
    "sacr": [
        "Une histoire de chat",
        "Édition de référence :",
        "Chatou, Paris, 2076.",
        "{{le_chat:EN=__PER__ Je}} suis un chat. Les chats miaulent. {{le_chat:EN=__PER__ je}} miaule aussi.",
        "{{le_chat:EN=__PER__ Je}} me balade dans le jardin, et mange des souris.",
        "{{le_chat:EN=__PER__ Mes}} moustaches flottent au vent comme des petits cerf-volant.",
        "{{le_chat:EN=__PER__ J'}}ai les oreilles pointus, pointées vers {{les_moineaux:EN=__PER__ les oiseaux}}.",
        "{{le_chat:EN=__PER__ Je}} mangerai bien {{le_gros_moineau:EN=__PER__ le plus gros de {{les_moineaux:EN=__PER__ ces moineaux}}.",
    ]
}}
```


# Input
```json
{input}
```


# Output
<TODO>
