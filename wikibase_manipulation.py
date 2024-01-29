
import requests


def get_csrf_token(wikibase_api_url, username, password):
    # Log in to obtain a CSRF token
    login_url = f"{wikibase_api_url}"
    login_data = {
        'action': 'login',
        'lgname': username,
        'lgpassword': password,
        'format': 'json'
    }
    try:
        # Perform login request
        login_response = requests.post(login_url, data=login_data)
        login_response.raise_for_status()
        print(login_response.json())

        # Extract login token from response
        login_token = login_response.json()['login']['token']
        print(f'Login token: {login_token}')

        # Send login request with token
        login_data = {
            'action': 'login',
            'lgtoken': login_token,
            'format': 'json'}
        login_response = requests.post(login_url, data=login_data)
        login_response.raise_for_status()
        print (f'Login response: {login_response.json()}')

        # Get CSRF token from the API
        token_url = f"{wikibase_api_url}"
        token_data = {'action': 'query',
                      'meta': 'tokens',
                      'type': 'csrf',
                      'format': 'json'}
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        print(token_response.json())

        # Extract CSRF token from response
        csrf_token = token_response.json().get('tokens', {}).get('csrf')

        if csrf_token:
            print("CSRF token:", csrf_token)
        else:
            print("CSRF token not found in the response.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Example usage:
wikibase_api_url = "https://itidata.abtk.hu/w/api.php"  # Example API URL
item_id = "Q42"  # Example item ID
property_id = "P31"  # Example property ID
claim_id = "Q42$E821BF63-7F94-4A5E-8B9A-643C99B8C612"  # Example claim ID
username = "Palkó.Gábor"  # Your Wikibase username
password = "mFUFCZR7vf3eU9xD"  # Your Wikibase password
get_csrf_token(wikibase_api_url, username, password)
# delete_property_value(item_id, property_id, claim_id, wikibase_api_url, username, password)
