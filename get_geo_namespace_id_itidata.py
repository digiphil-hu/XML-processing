import requests

# Define the Wikidata API endpoint
api_endpoint = "https://itidata.abtk.hu/w/api.php"

# Define the Wikidata Query Service endpoint
wdqs_endpoint = "https://query.itidata.abtk.hu/proxy/wdqs/bigdata/namespace/wdq/sparql"

# Set the request headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Accept": "application/json"
}


def get_itidata_item_info(item_ids):

    # Initialize result dictionary
    result_dict = {}

    # Set the request parameters
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": "|".join(item_ids),
        "languages": "en|hu",
    }

    try:
        # Send the HTTP request to the Wikidata API
        response = requests.get(api_endpoint, params=params)
        data = response.json()

        # Iterate over item IDs and extract information
        for item_id in item_ids:
            entity_data = data["entities"].get(item_id, {})

            # Extract item labels
            labels = entity_data.get("labels", {})
            english_label = labels.get("en", {}).get("value", "")
            hungarian_label = labels.get("hu", {}).get("value", "")
            item_labels = [english_label, hungarian_label]

            # Extract values for P2 (wikidata id)
            wikidata_claims = entity_data.get("claims", {}).get("P2", [])
            wikidata_id_values = [claim["mainsnak"]["datavalue"]["value"] for claim in wikidata_claims]

            # Extract values for P1 (instance of)
            instance_of_claims = entity_data.get("claims", {}).get("P1", [])
            instance_of_values = [claim["mainsnak"]["datavalue"]["value"]["id"] for claim in instance_of_claims]
            #
            # Extract values for P20 (country)
            country_claims = entity_data.get("claims", {}).get("P20", [])
            country_values = [claim["mainsnak"]["datavalue"]["value"]["id"] for claim in country_claims]

            # Extract values for P19 (coordinate location)
            coordinate_claims = entity_data.get("claims", {}).get("P625", [])
            coordinate_values = [(claim["mainsnak"]["datavalue"]["value"]["latitude"],
                                  claim["mainsnak"]["datavalue"]["value"]["longitude"]) for claim in coordinate_claims]

            # Populate the result dictionary with item ID as key and lists as values
            result_dict[item_id] = {
                "item_labels": item_labels,
                "wikidata_id": wikidata_id_values,
                "instance_of": instance_of_values,
                "country": country_values,
                # "coordinates": coordinate_values
            }

    except Exception as e:
        print(f"Error: {e}")

    # Return the result dictionary
    return result_dict


def get_itidata_subclasses_of_human_settlement():
    """
    Retrieves subclasses of "human settlement" in Wikidata.

    Returns:
    - list: List of tuples containing subclass item id and label.
    """
    # Define the SPARQL query to retrieve subclasses of "human settlement"
    sparql_query = """
    SELECT ?subclass ?subclassLabel WHERE {
        ?subclass wdt:P14/wdt:P14* wd:Q51;  # Subclass or sub-subclass of human settlement
                 rdfs:label ?subclassLabel.
        FILTER(LANG(?subclassLabel) = "en").
    }
    """

    # Set the request parameters
    params = {
        "query": sparql_query,
        "format": "json"
    }

    try:
        # Send the HTTP request to the Wikidata Query Service
        response = requests.get(wdqs_endpoint, headers=headers, params=params)
        data = response.json()

        # Extract relevant information from the response
        results = data.get("results", {}).get("bindings", [])

        # Create a list of tuples containing subclass item id and label
        subclasses = [(result["subclass"]["value"].split("/")[-1], result["subclassLabel"]["value"])
                      for result in results]
        subclasses.append(('Q51', 'human settlement'))

        return subclasses

    except Exception as e:
        print(f"Error: {e}")

    # Return an empty list if an error occurred
    return []


def get_itidata_item_id(label):
    # Set the request parameters
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "hu",
        "search": label,
        "type": "item",
    }

    try:
        # Send the HTTP request to the itidata API
        response = requests.get(api_endpoint, params=params)
        data = response.json()

        # Check if any entities were found
        if data.get("search"):
            # Get a list of itidata item IDs from the search results
            itidata_item_ids = [result["id"] for result in data["search"]]

            return itidata_item_ids

    except Exception as e:
        print(f"Error: {e}")

    # Return an empty string if an error occurred or no match found
    return ""


def get_item_labels_from_itidata(item_id):

    # Set the request parameters
    params = {
        "action": "wbgetentities",
        "ids": item_id,
        "languages": "hu|en",  # Specify languages for labels (Hungarian and English)
        "format": "json"
    }

    try:
        # Send the HTTP request to the Wikidata API
        response = requests.get(api_endpoint, params=params)
        data = response.json()

        # Extract relevant information from the response
        entity = data.get("entities", {}).get(item_id, {})
        labels = entity.get("labels", {})
        label_hu = labels.get("hu", {}).get("value", "")
        label_en = labels.get("en", {}).get("value", "")

        if label_hu is None or label_hu == "":
            return label_en + f"({item_id})"
        else:
            return label_hu + f"({item_id})"

    except Exception as e:
        print(f"Error: {e}")

    # Return empty strings if an error occurred
    return "Unknown"

def get_eng_hun_item_labels_from_itidata(item_id, what_do_yo_need):

    # Set the request parameters
    params = {
        "action": "wbgetentities",
        "ids": item_id,
        "languages": "hu|en",  # Specify languages for labels (Hungarian and English)
        "format": "json"
    }

    try:
        # Send the HTTP request to the Wikidata API
        response = requests.get(api_endpoint, params=params)
        data = response.json()

        # Extract relevant information from the response
        entity = data.get("entities", {}).get(item_id, {})
        labels = entity.get("labels", {})
        label_hu = labels.get("hu", {}).get("value", "")
        label_en = labels.get("en", {}).get("value", "")

        if what_do_yo_need == "json":
            return data
        else:
            return (label_hu, label_en)

    except Exception as e:
        print(f"Error: {e}")

    # Return empty strings if an error occurred
    return "Unknown"

#
# print(get_itidata_subclasses_of_human_settlement())
# print(get_item_labels_from_itidata("Q2727"))
# bud_ids = get_itidata_item_id("Budapest")
# print(bud_ids)
# bud_dict = get_itidata_item_info(bud_ids)
# for key, value in bud_dict.items():
#     print(f"{key}: {value}")
#
