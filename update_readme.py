import os
import pandas
from .io import read, write_force
HOME = os.environ['HOME']


models = [
    "gpt-5.5-high",
    "gpt-5.5-medium",
    "gpt-5.5-low",
    "google/gemma-4-31B-it",
    "gpt-5-chat-latest",
    "google/gemma-4-E4B-it",
]
mode = "pretagged"
sizes = [
    "full",
    "half",
    "quarter",
    "eighth",
    "sixteenth",
    "10",
    "5",
]
books = {
    # "Manon Lescaut - Antoine François Prévost, 1731": "1731_Prévost-Antoine-François_Manon-Lescaut",
    "Ourika - Claire de Duras, 1823": "1823_Duras-Claire-de_Ourika",
    "Sarrasine - Honoré de Balzac, 1830": "1830_Balzac-Honoré-de_Sarrasine",
    "Indiana - George Sand, 1832": "1832_Sand-George_Indiana_PER-ONLY",
}


content = read(f"{HOME}/github.com/loicbourgois/em/templates/README.md")


results = ""
for book_k, book in books.items():
    data_df = pandas.DataFrame(index=list(models), columns=list(sizes), dtype=str)
    for model in models:
        for size in sizes:
            path = f"{HOME}/github.com/loicbourgois/em/v5/{book}/{mode}-{size}-{model}/00_result.tsv"
            try:
                df = pandas.read_csv(path, sep='\t')
                df = df.set_index('Unnamed: 0')
                score = df.loc['CONLL', 'f1_score']
                data_df.at[model, size] = score
            except:
                data_df.at[model, size] = ""
    results += f"\n\n### {book_k}\n"
    results += str(data_df.to_markdown(floatfmt=".3f"))
    results += "\n"


write_force(
    f"{HOME}/github.com/loicbourgois/em/README.md",
    content.format(
        results=results,
    )
)
