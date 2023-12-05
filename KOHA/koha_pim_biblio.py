import csv


def read_tsv_to_dict(file_path):
    result_dict = {}
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            # Assuming the TSV file has at least two columns
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                result_dict[key] = value
    return result_dict


def process_tsv(input_tsv_path, input_dict, output_tsv_path):
    with open(input_tsv_path, 'r', encoding='utf-8', newline='') as input_file, \
         open(output_tsv_path, 'w', encoding='utf-8', newline='') as output_file:

        reader = csv.reader(input_file, delimiter='\t')
        writer = csv.writer(output_file, delimiter='\t')
        set_of_used_koha_entries = set()

        for row in reader:
            # Assuming the TSV file has at least one column
            if len(row) >= 1:
                key = row[0]

                # Check if the key is present in the input dictionary
                if key in input_dict:
                    value = input_dict[key]
                    set_of_used_koha_entries.add(key)

                    # Write a line in the output TSV
                    output_row = [f'{key}', f'{value}'] + row
                    writer.writerow(output_row)

    all_koha_from_editions = set(input_dict.keys())
    print(all_koha_from_editions.difference(set_of_used_koha_entries))


def koha_pim_biblio(id_list_tsv, koha_pim_tsv, koha_pim_biblio_tsv):
    id_dict = read_tsv_to_dict(id_list_tsv)
    process_tsv(koha_pim_tsv, id_dict, koha_pim_biblio_tsv)

