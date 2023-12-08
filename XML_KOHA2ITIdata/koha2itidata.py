import os
from bs4 import BeautifulSoup
import csv


def parse_xml(xml_path):
    with open(xml_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    # print(xml_path)
    soup = BeautifulSoup(xml_content, 'xml')
    return soup


def get_filenames(f_path_list):
    for f_path in f_path_list:
        for root, dirs, files in os.walk(f_path):
            for filename in files:
                if filename.endswith(".xml"):
                    xml_path = os.path.join(root, filename)
                    parsed_xml = parse_xml(xml_path)
                    # print(xml_path)
                    yield parsed_xml, xml_path


def tsv_to_dict(tsv_path):
    koha_itidata_dict = dict()
    with open(tsv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            koha_itidata_dict[row[3]] = row[1]
    return koha_itidata_dict


tsv_path = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data_RMKT/itidata_koha_pim_biblio.tsv"
path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-6"]
koha_dict = tsv_to_dict(tsv_path)


for parsed, path in get_filenames(path_list):
    for idno_tag in parsed.find_all('idno', {'type': 'KOHA_AUTH'}):
        # print(idno_tag.parent.name, idno_tag.string, idno_tag.get('corresp'))
        if idno_tag.parent.name == 'persName':
            koha_key = idno_tag.string.replace('KOHA_AUTH:', '').strip()
            # print(idno_tag.string, path)
            idno_tag['type'] = 'ITIdata'
            idno_tag.string = koha_dict[koha_key]
            print(idno_tag)


