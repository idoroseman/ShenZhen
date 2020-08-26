import json
with open("data/Connectors.json") as fin:
     parts = json.load(fin)
search = "6p 2.54"

for item in parts:
    found = all([x in item['desc'].upper() for x in search.upper().split(' ')])
    if found:
        print(item)