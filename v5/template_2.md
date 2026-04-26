# Goal


## Group mentions
Group back multiple enities under the same group LABEL.


## Rules
Make sure all references make it back.


# Example


## Input
...


## Output
```json
{{
    "reasoning": [
        "...",
        "...",
        "...",
    ],
    "rules_validation": [
        "...",
        "...",
        "...",
    ],
    "references": {{
        "1_le_narateur": "CHRISTIAN_LE_NARATEUR",
        "1_mamam": "LA_MERE",
        "1_maman_et_l_enfant": "CHRISTIAN_ET_SA_MERE",
        "2_christian": "CHRISTIAN_LE_NARATEUR",
        "3_christian_et_sa_mere": "CHRISTIAN_ET_SA_MERE",
    }},
    "groups": {{
        "CHRISTIAN_LE_NARATEUR": {{
            "definition": "narateur, christian, un petit garcon",
            "references:" ["1_le_narateur", "2_christian"]
        }},
        "LA_MERE": {{
            "definition": "la mère de christian",
            "references:" ["1_mamam"],
        }},
        "CHRISTIAN_ET_SA_MERE": {{
            "definition": "le narateur, christian et sa mère",
            "references:" ["1_maman_et_l_enfant", "3_christian_et_sa_mere"],
        }}
    }},
}}
```


# Input
```json
{input}
```


# Output
<TODO>
