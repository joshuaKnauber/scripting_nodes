from ...utils.libraries.fuzzywuzzy import fuzz
from . import scraper


SEARCH_RESULTS = []


def update_search_results(query: str):
    global SEARCH_RESULTS

    # assign a score to each key
    scores = {}
    for key, operator in scraper.BLENDER_OPERATORS.items():
        id_score = fuzz.partial_ratio(query, key)
        name_score = fuzz.partial_ratio(operator["name"], query)
        desc_score = fuzz.partial_ratio(operator["description"], query)
        score = max([id_score, name_score, desc_score])
        scores[key] = score

    # order by score
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # create search results
    SEARCH_RESULTS = [item[0] for item in ordered]
