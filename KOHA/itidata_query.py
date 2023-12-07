import csv
import time

import requests
from api_request import get_person_info_from_wikidata


def get_sparql_query(tsv_value):
    return f"""
    SELECT DISTINCT ?item WHERE {{
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }}
      {{
        SELECT DISTINCT ?item WHERE {{
          ?item p:P100 ?statement0.
          ?statement0 (ps:P100) "{tsv_value}".
        }}
        LIMIT 10
      }}
    }}
    """

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def send_sparql_query_with_retry(endpoint, query):
    session = requests.Session()
    retry_strategy = Retry(
        total=10,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.post(endpoint, data={'query': query, 'format': 'json'})
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return requests.Response()  # Return an empty response object

# def send_sparql_query(endpoint, query):
#     response = requests.post(endpoint, data={'query': query, 'format': 'json'})
#     return response


def process_results(response):
    if response.status_code == 200:
        result_json = response.json()
        if 'results' in result_json and 'bindings' in result_json['results'] and result_json['results']['bindings']:
            return result_json['results']['bindings'][0]['item']['value']
        else:
            return "Missing"
    else:
        return f"Error: {response.status_code}, {response.text}"


def itidata_query(tsv_file_path_in, tsv_file_path_out):
    # SPARQL endpoint URL
    sparql_endpoint = "https://query.itidata.abtk.hu/proxy/wdqs/bigdata/namespace/wdq/sparql"

    # Open input and create output TSV files:
    with (open(tsv_file_path_in, 'r', newline='', encoding='utf-8') as tsvfile_in,
          open(tsv_file_path_out, 'w', newline='', encoding='utf-8') as tsvfile_out):

        tsvreader = csv.reader(tsvfile_in, delimiter='\t')
        tsvwriter = csv.writer(tsvfile_out, delimiter='\t')
        result_list = []

        for row in tsvreader:
            time.sleep(1)
            if row and row[3].isdigit():  # Check if the row is not empty and if the 4th cell contains numbers only.

                # Get the value from the 4th column
                pim_id_tsv_value = "PIM" + row[3]
                print(pim_id_tsv_value)

                # Get SPARQL query
                sparql_query = get_sparql_query(pim_id_tsv_value)

                # Send the SPARQL query to the endpoint
                response = send_sparql_query_with_retry(sparql_endpoint, sparql_query)

                # Process the results and add to the list
                result = process_results(response).replace("https://itidata.abtk.hu/entity/", "")
                result_list.append((pim_id_tsv_value, result))

                # Get name and dates
                name_and_dates = get_person_info_from_wikidata(result)

                # Write new line to the output TSV
                new_row = [f"PIM{row[3]}", f"{result}", f"{name_and_dates}"] + row
                tsvwriter.writerow(new_row)

                # Print result
                print(result)

            else:
                new_row = [f"{row[3]}", f"Unknown"] + row
                tsvwriter.writerow(new_row)
