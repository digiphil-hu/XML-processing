import logging

import requests
from wikidataintegrator import wdi_core, wdi_login

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define your Wikidata credentials
wikidata_user = "Palkó.Gábor"
wikidata_pass = "mFUFCZR7vf3eU9xD"

# Define the Wikidata API URL
wikidata_api_url = "https://itidata.abtk.hu/w/api.php"

# Set up a Wikidata login session
login_instance = wdi_login.WDLogin(wikidata_user, wikidata_pass, mediawiki_api_url=wikidata_api_url)
csrf_token = login_instance.get_edit_token()
print(f"csrf_token: {csrf_token}")


def modify_wikidata_item(item_id, property_id, value):
    # Create a statement object with the desired claim
    claim = [wdi_core.WDMonolingualText(value, prop_nr=property_id, language="hu")]

    # Define the Wikidata item to modify
    item = wdi_core.WDItemEngine(wd_item_id=item_id, mediawiki_api_url=wikidata_api_url)

    # Add the claim to the item
    item.update(claim)

    # Save the changes to Wikidata
    try:
        item.write(login_instance, bot_account=True)
        logging.info(f"Successfully modified {item_id}, Property {property_id} with value: {value}")
    except Exception as e:
        logging.error(f"Error modifying {item_id}, Property {property_id}: {e}")


def delete_wikidata_claim(item_id, property_id):
    try:
        # Define the Wikidata item to modify
        item = wdi_core.WDItemEngine(wd_item_id=item_id, mediawiki_api_url=wikidata_api_url)

        # Retrieve all claims for the specified property
        claims = item.get_wd_json_representation()["claims"].get(property_id, [])

        # Check if claims exist before attempting to delete
        if claims:
            # Loop through the claims and delete each one
            for claim in claims:
                claim_id = claim.get('id')
                print(claim_id)
                login_instance = wdi_login.WDLogin(wikidata_user, wikidata_pass, mediawiki_api_url=wikidata_api_url)
                csrf_token = login_instance.get_edit_token()
                print(csrf_token)
                try:
                    # Construct the URL for deleting the claim
                    delete_url = f"{wikidata_api_url}"

                    # Set the parameters for the POST request
                    post_data = {
                        "action": "wbremoveclaims",
                        "claim": claim_id,
                        "token": csrf_token
                    }

                    # Send a custom POST request
                    response = requests.post(delete_url, data=post_data)
                    print(response.text)

                except Exception as e:
                    logging.error(f"Error during claim deletion: {e}")

        else:
            logging.warning(f"No claims found for {item_id}, Property {property_id}")

    except Exception as e:
        logging.error(f"Error initializing WDItemEngine: {e}")


# Example usage:
item_id = "Q346075"  # Replace with the Wikidata item ID you want to modify
property_id = "P18"  # Replace with the Wikidata property ID you want to modify
new_value = "New value"  # Replace with the new value you want to set

# modify_wikidata_item(item_id, property_id, new_value)
delete_wikidata_claim(item_id, property_id)
