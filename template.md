# Goal
- Flag all entities
- Extract all entities
- Group entities
- Map entities to their group


# Rules
- Only work on living things and their attibuts. 
- We don't care about the décor. 
- If two groups are refering to the same person, they should be merged together.
- The `flagging` section should have the full input text
  Do not forget any sentence, even if there is no mention of any personnage.


# Example


## Input
Une histoire de chat

Édition de référence :

Chatou, Paris, 2076.

Je suis un chat. Les chats miaulent. Je miaule aussi.

Je me balade dans le jardin, et mange des souris.

Mes moustaches flottent au vent comme des petits cerf-volant.


## Output
```yaml
{{
    "flagging_reasoning": "...",
    # Note how all sentences are present
    "flagging": [
        "Une histoire de chat",
        "Édition de référence :",
        "Chatou, Paris, 2076.",
        "<Je> suis <un chat>. <Les chats> miaulent. <Je> miaule aussi.",
        "<Je> me balade dans le jardin, et mange <des souris>.",
        "<Mes> moustaches flottent au vent comme des petits cerf-volant."
    ],
    "entities_reasoning": "...",
    "entities": [
        "je",
        "un chat",
        "les chats",
        "je",
        "je",
        "des souris",
        "Mes",
    ],
    "groups_reasoning": "...",
    "groups": [
        "narrator",
        "les chats",
        "souris"
    ],
    "mapping_reasoning": "...",
    "mapping": [
        ["je", "narrator"],
        ["un chat", "narrator"],
        ["les chats", "les chats"],
        ["je", "narrator"],
        ["je", "narrator"],
        ["des souris", "souris"],
        ["Mes", "narrator"],
    ]
}}
```


# Input
{input}


# Output
<TODO>
