import requests


def get_person_info_from_wikidata(item_id):
    # Wikidata API endpoint
    endpoint = "https://itidata.abtk.hu/w/api.php"

    # Wikidata API parameters
    params = {
        'action': 'wbgetentities',
        'ids': item_id,
        'format': 'json',
    }

    try:
        # Send a request to the Wikidata API
        response = requests.get(endpoint, params=params)
        data = response.json()

        # Extract relevant information from the response
        entity = data['entities'][item_id]
        labels = entity.get('labels', {})
        claims = entity.get('claims', {})

        # # Extract given name and family name from labels
        # given_name = labels.get('en', {}).get('value', 'N/A')
        # family_name = labels.get('en', {}).get('value', 'N/A')

        # Extract date of birth and date of death from claims
        birth_claim = claims.get('P5', [{}])[0]
        death_claim = claims.get('P6', [{}])[0]
        family_name_claim = claims.get('P104', [{}])[0]
        given_name_claim = claims.get('P105', [{}])[0]

        date_of_birth = birth_claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time', '')[1:5]
        date_of_death = death_claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time', '')[1:5]
        family_name = family_name_claim.get('mainsnak', {}).get('datavalue', {}).get('value', {})
        given_name = given_name_claim.get('mainsnak', {}).get('datavalue', {}).get('value', {})

        # Format the result string
        result_string = f"{family_name} {given_name} ({date_of_birth}-{date_of_death})"
        return result_string

    except Exception as e:
        print(f"Error: {e}")
        return None

#
# # Example usage
# item_id = "Q140423"  # Replace with the Wikidata item ID you are interested in
# result = get_person_info_from_wikidata(item_id)
#
# if result:
#     print(result)
# else:
#     print("Failed to retrieve information from Wikidata.")
