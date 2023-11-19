import requests

url = "https://www.wikidata.org/w/api.php"

params = {
    "action": "wbgetentities",
    "format": "json",
    "language": "en",
    "props": "claims",
    "claims": f"P214:{29557616}"
}

response = requests.get(url, params=params).json()
for key, value in response.items():
    print(key, '\t', value)

if response["entities"]:
    entity_id = list(response["entities"].keys())[0]
    if "P214" in response["entities"][entity_id]["claims"]:
        viaf_id = response["entities"][entity_id]["claims"]["P214"][0]["mainsnak"]["datavalue"]["value"]
        print(f"The VIAF ID for the given value is {viaf_id}.")
    else:
        print("No VIAF ID found for the given value.")
else:
    print("No entity found for the given value.")
