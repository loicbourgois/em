# Goal


## Flag entities
Flag all entities

All pronouns should be referenced
"vous me faites signe" -> vous + me -> "<vous> <me> faites signe"

We can have multiple levels
"la belle soeur du mari de ma mère" -> "<la belle soeur <du mari de <<ma> mere>>>"

Be as wide as possible.


## Extract entities
Extract all entities


## Group entities
Group entities


## Map entities
Map entities to their group



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
  "je me regarde dans la glace" -> "<je> me regarde dans la glace"
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
    "Je suis un chat. Les chats miaulent. Je miaule aussi.",
    "Je me balade dans le jardin, et mange des souris.",
    "Mes moustaches flottent au vent comme des petits cerf-volant.",
    "J'ai les oreilles pointus, pointées vers les oiseaux.",
    "Je mangerai bien un petit moineau."
]
```



## Output
```json
{{
    "flagging_reasoning": "...",
    # Note how all sentences are present
    "flagging": [
        "Une histoire de chat",
        "Édition de référence :",
        "Chatou, Paris, 2076.",
        "<Je> suis un chat. Les chats miaulent. <Je> miaule aussi.",
        "<Je> me balade dans le jardin, et mange des souris.",
        "<Mes> moustaches flottent au vent comme des petits cerf-volant.",
        "<J>'ai les oreilles pointus, pointées vers les oiseaux.",
        "<Je> mangerai bien un petit moineau.",
    ],
    "entities_reasoning": "...",
    "entities": [
        "je",
        "je",
        "je",
        "Mes",
        "J",
        "Je",
    ],
    "groups_reasoning": "...",
    # Note how each group is unique
    # Note how we give them a description, to facilitate agregation, grouping and mapping
    "groups": {{
        "narrator": "le narateur, un chat spécifique",
    }},
    "mapping_reasoning": "...",
    "mapping": [
        ["je", "narrator"],
        ["je", "narrator"],
        ["je", "narrator"],
        ["Mes", "narrator"],
        ["J", "narrator"],
        ["Je", "narrator"],
    ],
    "sacr": [
        "Une histoire de chat",
        "Édition de référence :",
        "Chatou, Paris, 2076.",
        "{{narrator:EN=__PER__ Je}} suis un chat. Les chats miaulent. {{narrator:EN=__PER__ je}} miaule aussi.",
        "{{narrator:EN=__PER__ Je}} me balade dans le jardin, et mange des souris.",
        "{{narrator:EN=__PER__ Mes}} moustaches flottent au vent comme des petits cerf-volant.",
        "{{narrator:EN=__PER__ J}}'ai les oreilles pointus, pointées vers les oiseaux.",
        "{{narrator:EN=__PER__ Je}} mangerai bien un petit moineau.",
    ]
}}
```


# Input
```json
{input}
```


# Output
<TODO>
