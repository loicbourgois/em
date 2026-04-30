# Goal


## Group mentions
Group mentions together into entities


## Analyze relationships
Map the relationships between the different entities


## Update base
Add back the entities in the base text.


# Rules
- Only work on the "focus" part of the text.
  The rest of the text is here to give you context.
- Only work on living things. 
- We don't care about the décor.
- If two groups are refering to the same person, they should be merged together.
- You can only replace `____` parts
  If `____`is not present, do not do anything.
- You need to replace all `____`
- You can not create new `____`
- Use simple text for id: 'a-z' + '_' only
- a character can be in multiple entities
  {{{{John}} et {{moi}}}}, {{nous}} regardons la télé
    john_uniquement: John
    narateur_uniquement: moi
    les_2_personnages: nous
    les_2_personnages: John et moi
- if 2 entities are together, they create a new entity
- entities ID can not have spaces " "
- if you're not sure, prefer tagging the metion with 'unsure_...' + different tag
  a follow up process will work on unsure mentions
  do not create new mentions
  only existing `___` are ok to replace
- do not add any `{{`
- do not add any `}}`
- strictly rewrite the input sentences
- the entities labels should map to the full text, not just the focused part
- do not create any new mentions
  if ther is no "___" in `focus`, do nothing


# Example


## Input
```json
{{
    "text": [
        "Une histoire de chat",
        "Édition de référence :",
        "Chatou, Paris, 2076.",
        "{{LE_CHAT_NARRATEUR Je}} suis un chat. Les chats miaulent. {{LE_CHAT_NARRATEUR Je}} miaule aussi.",
        "{{LE_CHAT_NARRATEUR Je}} me balade dans le jardin, et mange des souris.",
        "{{LE_CHAT_NARRATEUR Mes}} moustaches flottent au vent comme des petits cerf-volant.",
        "{{____ J'}}ai les oreilles pointus, pointées vers {{____ les oiseaux}}.",
        "{{____ Je}} mangerai bien {{____ le plus gros de {{____ ces moineaux}}}}.",
    ],
    "focus": "{{____ J'}}ai les oreilles pointus, pointées vers {{____ les oiseaux}}."
}}
```


## Output
```json
{{
    "initial_mapping": {{
        "J'": "le narateur",
        "les oiseaux": "un groupe d'oiseu",
    }},
    "entities_reasoning": [
        ...
    ],
    "relationships_reasoning": [
        ...
    ],
    # Use this section to make sure all rules are respected
    "rules_validation": [
        ...
    ],
    "final_reasoning": [
        ...
    ],
    "relationships": [
        {{
            "entity_1": "LE_CHAT_NARRATEUR",
            "entity_2": "LES_OISEAUX",
            "relationship": "LE_CHAT_NARRATEUR observe LES_OISEAUX",
        }}
    ],
    # Note how each entity is unique
    # Note how we give them a description, to facilitate grouping
    "entities": {{
        "LE_CHAT_NARRATEUR": {{
            "description": "un chat spécifique, qui raconte l'histoire",
            "mentions": ["Je", "Je", "Je", "Mes", "J'", "Je"],
        }},
        "LES_OISEAUX": {{
            "description": "les oiseux que je chat guette",
            "mentions": ["les oiseaux", "ces moineaux"],
        }},
        "LE_GROS_MOINEAUX": {{
            "description": "le moineau specific que le chat veut",
            "mentions": ["le plus gros de ces moineaux"],
        }},
    }},
    "focus_formatted": "{{LE_CHAT_NARRATEUR J'}}ai les oreilles pointus, pointées vers {{LES_OISEAUX les oiseaux}}.",
    # Use this section to make sure all rules are respected
    "final_rules_validation": [
        ...
    ],
}}
```


# Input
```json
{input}
```


# Output
<TODO>
