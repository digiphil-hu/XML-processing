from bs4 import BeautifulSoup
import re


def normalize(string):
    string = string.strip()
    string = string.replace('\t', '')
    string = string.replace('\n', '')
    string = re.sub(r'\s+', ' ', string)
    return string


def extract_field_value(soup, tag, subfield_code, tag_value):
    """
    Extract the value of a field (controlfield or datafield) from BeautifulSoup object.
    """
    field = "Unknown"
    if tag == "controlfield":
        field = soup.find(tag, {'tag': tag_value}).text
    else:
        if (soup.find(tag, {'tag': tag_value})
                          and soup.find(tag, {'tag': tag_value}).find('subfield', {'code': subfield_code})):
            field = soup.find(tag, {'tag': tag_value}).find('subfield', {'code': subfield_code}).text

    return normalize(field)


def parse_large_txt_file(input_file_path, output_tsv_path):
    # Define datafields to extract
    datafields = [
        {'tag': 'controlfield', 'subfield_code': '', 'tag_value': '001'},
        {'tag': 'datafield', 'subfield_code': 'a', 'tag_value': '151'},
        {'tag': 'datafield', 'subfield_code': 'a', 'tag_value': '451'},
        {'tag': 'datafield', 'subfield_code': 'a', 'tag_value': '550'},
        {'tag': 'datafield', 'subfield_code': 'a', 'tag_value': '551'}
        ]

    with (open(output_tsv_path, 'w', encoding='utf-8') as tsv_file):
        # Write header to the TSV file
        header = '\t'.join(
            [f"{field['tag']}_{field['tag_value']}{field['subfield_code']}" for field in datafields]) + '\n'
        tsv_file.write(header)

        with open(input_file_path, 'r', encoding='utf-8') as file:
            in_record_segment = False
            record_segment = ""

            for line in file:
                if '<record>' in line:
                    in_record_segment = True
                    record_segment = line
                elif '</record>' in line and in_record_segment:
                    in_record_segment = False
                    record_segment += line

                    if '<subfield code="a">GEOGR_NAME</subfield>' in record_segment:
                        soup = BeautifulSoup(record_segment, 'xml')

                        # Extract values of datafields
                        datafield_values = [
                            extract_field_value(soup, field['tag'], field.get('subfield_code'), field.get('tag_value'))
                            for field in datafields
                        ]

                        # Write values to the TSV file
                        tsv_file.write('\t'.join(datafield_values) + '\n')
                elif in_record_segment:
                    record_segment += line


# Example usage
input_file_path = '/home/eltedh/PycharmProjects/DATA/KOHA/auths.txt'
output_tsv_path = 'geonames_form_koha_dump.tsv'

parse_large_txt_file(input_file_path, output_tsv_path)
