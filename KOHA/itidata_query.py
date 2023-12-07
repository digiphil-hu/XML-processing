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

    # Input, output TSV file path
    tsv_file_path_in = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/koha_pim_biblio.tsv"
    tsv_file_path_out = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/itidata_koha_pim_biblio.tsv"

    # Open input and create output TSV files:
    with (open(tsv_file_path_in, 'r', newline='', encoding='utf-8') as tsvfile_in,
          open(tsv_file_path_out, 'w', newline='', encoding='utf-8') as tsvfile_out):

        tsvreader = csv.reader(tsvfile_in, delimiter='\t')
        tsvwriter = csv.writer(tsvfile_out, delimiter='\t')

        for row in tsvreader:
            if row and row[3].isdigit():  # Check if the row is not empty and if the 4th cell contains numbers only.

                # Get the value from the 4th column
                pim_id_tsv_value = "PIM" + row[3]
                print(pim_id_tsv_value)

                # Get SPARQL query
                sparql_query = get_sparql_query(pim_id_tsv_value)

                # Send the SPARQL query to the endpoint
                response = send_sparql_query(sparql_endpoint, sparql_query)

                # Process the results and add to the list
                result = process_results(response)

                # Print result
                # print(result)

    # Create a new TSV file with Q IDs
    create_and_write_tsv(results_list, "output_file.tsv")


if __name__ == "__main__":
    main()
