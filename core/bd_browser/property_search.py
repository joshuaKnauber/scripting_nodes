import re
from ...utils.libraries.fuzzywuzzy import fuzz
from . import scraper


SEARCH_RESULTS = {}  # group: { key, score }[]


def update_search_results(query: str, types: [str], groupby: str, data_type: str):
    global SEARCH_RESULTS

    # filter data by type
    filtered_data = {}
    for key, value in scraper.BLENDER_DATA.items():
        has_bpydata = any(map(lambda p: p.startswith("bpy.data"), value["paths"]))
        has_bpycontext = any(map(lambda p: p.startswith("bpy.context"), value["paths"]))
        if (not types or value["type"] in types) or (
            data_type == "ALL"
            or (data_type == "DATA" and has_bpydata)
            or (data_type == "CONTEXT" and has_bpycontext)
        ):
            filtered_data[key] = value

    # assign a score to each key
    scores = {}
    for key, value in filtered_data.items():
        clean_path = (
            re.sub(r"\[.*\]", "", list(value["paths"])[0]).replace(".", " ").lower()
        )
        path_score = fuzz.partial_ratio(query, clean_path)
        name_score = fuzz.partial_ratio(value["name"], query)
        desc_score = fuzz.partial_ratio(value["description"], query)
        score = max([path_score, name_score, desc_score])
        scores[key] = score

    # order by score
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # create search results
    SEARCH_RESULTS = {}
    for item in ordered:
        key, score = item
        if groupby == "NAME":
            group = scraper.BLENDER_DATA[key]["name"]
        else:
            group = scraper.BLENDER_DATA[key]["last_value"]
        if not group in SEARCH_RESULTS:
            SEARCH_RESULTS[group] = []
        SEARCH_RESULTS[group].append(
            {
                "key": key,
                "score": score,
            }
        )
