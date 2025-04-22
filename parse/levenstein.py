from difflib import ndiff

def levenshtein_distance(str1:str, str2:str):
    counter = {"+": 0, "-": 0}
    distance = 0
    for edit_code, *_ in ndiff(str1, str2):
        if edit_code == " ":
            distance += max(counter.values())
            counter = {"+": 0, "-": 0}
        else:
            counter[edit_code] += 1
    distance += max(counter.values())
    lens = float((len(str1) - distance) / len(str1) * 100)
    if lens < 0.0: lens = 0.0
    return distance, lens