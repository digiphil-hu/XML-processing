
import ipywidgets as widgets
from IPython.display import display, clear_output
import wikitextparser as wtp
import requests


def check_wikidata_item(item_id):
    result_output.clear_output()

    # Get Wikidata content for the given item ID
    wikidata_api_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=claims|labels|descriptions&ids={item_id}"
    response = requests.get(wikidata_api_url)
    wikidata_data = response.json()

    try:
        # Extract relevant information from the response
        entity = wikidata_data['entities'][item_id]
        claims = entity.get('claims', {})
        labels = entity.get('labels', {})

        # Check if the item is an instance of human
        instance_of_claim = claims.get('P31', [])
        is_human = any(claim['mainsnak']['datavalue']['value']['id'] == 'Q5' for claim in instance_of_claim)

        # Check if required fields are present
        birth_name = labels.get('en', {}).get('value', '')
        given_name = claims.get('P735', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('text',
                                                                                                               '')
        date_of_birth = claims.get('P569', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get(
            'time', '')
        date_of_death = claims.get('P570', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get(
            'time', '')
        birth_place = claims.get('P19', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
        death_place = claims.get('P20', [{}])[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')

        # Check if death date is later than birth date
        death_date_valid = not (date_of_birth and date_of_death and date_of_birth > date_of_death)

        # Check if birth place and death place are human settlements
        birth_place_is_settlement = is_human_settlement(birth_place)
        death_place_is_settlement = is_human_settlement(death_place)

        # Check if birth place and death place have coordinates
        birth_place_has_coordinates = has_coordinates(birth_place)
        death_place_has_coordinates = has_coordinates(death_place)

        # Display the results
        with result_output:
            print(f"Item ID: {item_id}")
            print(f"Is Human: {is_human}")
            print(f"Birth Name: {birth_name}")
            print(f"Given Name: {given_name}")
            print(f"Date of Birth: {date_of_birth}")
            print(f"Date of Death: {date_of_death}")
            print(f"Birth Place: {birth_place}")
            print(f"Death Place: {death_place}")
            print(f"Death Date Valid: {death_date_valid}")
            print(f"Birth Place is Settlement: {birth_place_is_settlement}")
            print(f"Death Place is Settlement: {death_place_is_settlement}")
            print(f"Birth Place Has Coordinates: {birth_place_has_coordinates}")
            print(f"Death Place Has Coordinates: {death_place_has_coordinates}")

    except KeyError:
        with result_output:
            print(f"Error: Invalid Wikidata item ID")


def is_human_settlement(item_id):
    if not item_id:
        return False

    wikidata_api_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=claims&ids={item_id}"
    response = requests.get(wikidata_api_url)
    wikidata_data = response.json()

    try:
        claims = wikidata_data['entities'][item_id].get('claims', {})
        instance_of_claim = claims.get('P31', [])
        return any(claim['mainsnak']['datavalue']['value']['id'] == 'Q486972' for claim in instance_of_claim)
    except KeyError:
        return False


def has_coordinates(item_id):
    if not item_id:
        return False

    wikidata_api_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=claims&ids={item_id}"
    response = requests.get(wikidata_api_url)
    wikidata_data = response.json()

    try:
        claims = wikidata_data['entities'][item_id].get('claims', {})
        coordinates_claim = claims.get('P625', [])
        return len(coordinates_claim) > 0
    except KeyError:
        return False


# Create widgets
wikidata_item_id_input = widgets.Text(description='Wikidata Item ID:')
check_button = widgets.Button(description='Check')
result_output = widgets.Output()


# Define event handler for the button click
def on_check_button_click(b):
    check_wikidata_item(wikidata_item_id_input.value)


# Attach event handler to the button
check_button.on_click(on_check_button_click)

# Display widgets
display(wikidata_item_id_input, check_button, result_output)
