# Goal


## Group mentions
Group mentions together into entities


## Analyze relationships
Map the relationships between the different entities


## Update base
Add back the entities in the base text.


# Rules
- Only work on living things. 
- We don't care about the décor.
- If two groups are refering to the same person, they should be merged together.
- Only work on active personnage. No general entities.


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
    "entities_reasoning": "...",
    "relationships_reasoning": "...",
    # Note how each entity is unique
    # Note how we give them a description, to facilitate grouping
    "entities": {{
        "le_chat": {{
            "description": "un chat spécifique, qui raconte l'histoire",
            "mentions": ["Je", "Je", "Je", "Mes", "J'", "Je"],
        }},
        "les_moineaux": {{
            "description": "les oiseux que je chat guette",
            "mentions": ["les oiseaux", "ces moineaux"],
        }},
        "le_gros_moineau": {{
            "description": "le moineau specific que le chat veut",
            "mentions": ["le plus gros de ces moineaux"],
        }},
    }},
    "relationships": [
        {{
            "entity_1": "le_chat",
            "entity_2": "les_moineaux",
            "relationship": "le_chat observe les_moineaux",
        }}, {{
            "entity_1": "les_moineaux",
            "entity_2": "le_gros_moineau",
            "relationship": "le_gros_moineau est un individu du groupe les_moineaux",
        }}, {{
            "entity_1": "le_chat",
            "entity_2": "le_gros_moineau",
            "relationship": "le_chat veut manger le_gros_moineau",
        }}
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
