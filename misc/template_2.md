# Goal
Merge back groups together.


# Rules
Make sure to not merge back too much.
If a group refers to 2 people, this group should stay like that.
A given reference can only be in 1 group.


# Example 


## Input
```yaml
[
    {{
        "entities": {{
            "le narateur": "narateur, dont on ne connais pas le nom pour l'instant",
            "maman et l'enfant": "le narateur et sa mère"
        }},
        "relationships": {{
            ...
        }}
    }},
    {{
        "entities": {{
            "christian": "petit garcon qui compte l'histoire",
            "mamam": "la mère de christian",
            "christian et sa mère": "christian et sa mère"
        }},
        "relationships": {{
            ...
        }}
    }}
]
```


## Output
```json
{{
    "reasoning": [
        "...",
        "...",
        "...",
    ],
    "groups": {{
        "CHRISTIAN_LE_NARATEUR": {{
            "definition": "narateur, christian, un petit garcon",
            "references:" ["le narateur", "christian"]
        }},
        "LA_MERE": {{
            "definition": "la mère de christian",
            "references:" ["mamam"],
        }},
        "CHRISTIAN_ET_SA_MERE": {{
            "definition": "le narateur, christian et sa mère",
            "references:" ["maman et l'enfant", "christian et sa mère"],
        }}
    }},
    # Note that on the left, we have simple references, from the input
    # All references are listed
    # on the right, we have a new meta reference
    "reference to group": {{
        "le narateur": "CHRISTIAN_LE_NARATEUR",
        "maman et l'enfant": "CHRISTIAN_ET_SA_MERE",
        "christian": "CHRISTIAN_LE_NARATEUR",
        "mamam": "LA_MERE",
        "christian et sa mère": "CHRISTIAN_ET_SA_MERE"
    }},
}}
```


# Input
```yaml
{input}
```


# Output
<TODO>
