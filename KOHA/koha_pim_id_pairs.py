import csv


def make_dict(input_file_path, output_file_path):
    # Dict to store KOHA and PIM id's
    data_dict = dict()

    # Open the TSV file and iterate line-by-line
    with open(input_file_path, 'r', newline='', encoding='utf-8') as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')

        # Read the header
        header = next(tsvreader)

        for row in tsvreader:
            if row:
                # Extract values from the first and second columns
                first_column_value = row[0]
                second_column_value = row[1] if len(row) > 1 else None

                # Add id-s to dict
                data_dict[first_column_value] = second_column_value

        # with open(output_tsv_file, 'w', encoding='utf8') as f:
        #     for key, value in data_dict.items():
        #         f.write(f'{key}\t{value}\n')

        return data_dict


def process_tsv(tsv_filename_in, tsv_filename_out, id_dict):
    # Open the input TSV file and create the output TSV file
    with open(tsv_filename_in, 'r', newline='', encoding='utf-8') as infile, \
         open(tsv_filename_out, 'w', newline='', encoding='utf-8') as outfile:

        tsvreader = csv.reader(infile, delimiter='\t')
        tsvwriter = csv.writer(outfile, delimiter='\t')

        # Process header
        # header = next(tsvreader)
        # new_header = ['ID'] + header  # Add 'ID' as the first column in the header
        # tsvwriter.writerow(new_header)

        # Process each line in the input TSV file
        for row in tsvreader:
            if row:
                # Get the value from the first cell of the current row
                key = row[0]

                # Look up the key in the id_dict and get the corresponding value
                id_value = id_dict.get(key, "Missing")

                # Write a new line to the output TSV file
                tsvwriter.writerow([id_value] + row)



# Example usage:
input_tsv_file_koha_dump = "koha_pim.tsv"  # Replace with the path to your input TSV file
input_tsv_file_koha_from_xml = "koha_id_list.tsv"
output_tsv_file = "koha_pim_id_pairs.tsv"  # Replace with the desired output TSV file path

dict_of_id_pairs = make_dict(input_tsv_file_koha_dump, output_tsv_file)
process_tsv(input_tsv_file_koha_from_xml, output_tsv_file, dict_of_id_pairs)