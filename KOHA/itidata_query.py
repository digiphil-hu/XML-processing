import csv
import requests


def get_sparql_query(tsv_value):
    return f"""
    SELECT DISTINCT ?item WHERE {{
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }}
      {{
        SELECT DISTINCT ?item WHERE {{
          ?item p:P100 ?statement0.
          ?statement0 (ps:P100) "{tsv_value}".
        }}
        LIMIT 100
      }}
    }}
    """


def send_sparql_query(endpoint, query):
    response = requests.post(endpoint, data={'query': query, 'format': 'json'})
    return response


def process_results(response):
    if response.status_code == 200:
        result_json = response.json()
        if 'results' in result_json and 'bindings' in result_json['results'] and result_json['results']['bindings']:
            return result_json['results']['bindings'][0]['item']['value']
        else:
            return "Missing"
    else:
        return f"Error: {response.status_code}, {response.text}"


def create_and_write_tsv(q_ids, output_file_path):
    with open(output_file_path, 'w', newline='', encoding='utf-8') as tsvfile:
        tsvwriter = csv.writer(tsvfile, delimiter='\t')
        for q_id in q_ids:
            tsvwriter.writerow([q_id])


def main():
    # SPARQL endpoint URL
    sparql_endpoint = "https://query.itidata.abtk.hu/proxy/wdqs/bigdata/namespace/wdq/sparql"

    # TSV file path
    tsv_file_path = "koha_id_list.tsv"  # Replace with the path to your TSV file

    # List to store results
    results_list = []

    # Read values from the first column of the TSV file
    with open(tsv_file_path, 'r', newline='', encoding='utf-8') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        for row in tsvreader:
            if row:  # Check if the row is not empty
                # Get the value from the first column
                tsv_value = "PIM" + row[0]

                # Get SPARQL query
                sparql_query = get_sparql_query(tsv_value)

                # Send the SPARQL query to the endpoint
                response = send_sparql_query(sparql_endpoint, sparql_query)

                # Process the results and add to the list
                result = process_results(response)
                results_list.append(result)

                # Print result
                print(result)

    # Create a new TSV file with Q IDs
    create_and_write_tsv(results_list, "output_file.tsv")


if __name__ == "__main__":
    main()
