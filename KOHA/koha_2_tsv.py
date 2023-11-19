# This code reads KOHA id-s to a TSV

import os
from bs4 import BeautifulSoup
import lxml
import re
from collections import defaultdict


def iterate_xml_files(f_path):
    """
    Iterates through each XML file in the given folder path.
    Calls parse_xml function for each file.

    Parameters:
    - folder_path (str): Path of the folder containing XML files.
    """
    # for filename in os.listdir(f_path):
    #     if filename.endswith(".xml"):
    #         xml_path = os.path.join(f_path, filename)
    #         parse_xml(xml_path)

    for root, dirs, files in os.walk(f_path):
        for filename in files:
            if filename.endswith(".xml"):
                xml_path = os.path.join(root, filename)
                print(xml_path)
                parse_xml(xml_path)


def parse_xml(xml_path):
    """
    Parses the given XML file using BeautifulSoup.

    Parameters:
    - xml_path (str): Path of the XML file.
    """
    with open(xml_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    print(xml_path)
    soup = BeautifulSoup(xml_content, 'xml')
    return soup


def create_dictionary(f_path):
    """
    This function creates a dictionary. Keys are the KOHA id's, values are the names given in the corresp attribute.
    :param f_path:
    :return:
    """

    koha_id_dict = defaultdict(set)
    names_without_koha_id = set()
    viaf_id_dict = defaultdict(set)
    names_without_viaf_id = set()

    for root, dirs, files in os.walk(f_path):
        for filename in files:
            if filename.endswith(".xml"):
                xml_path = os.path.join(root, filename)
                parsed_xml = parse_xml(xml_path)

                # Extracting KOHA authorities
                for idno_tag in parsed_xml.find_all('idno', {'type': 'KOHA_AUTH'}):
                    if idno_tag.text != "":
                        koha_id = (idno_tag.text.replace("KOHA_AUTH:", "")
                                   .replace("KOHA:", "").strip())
                        corresp_name = idno_tag.get('corresp')
                        if corresp_name:
                            koha_id_dict[koha_id].add(corresp_name.strip())
                        else:
                            koha_id_dict[koha_id].add("")
                    else:
                        corresp_name = idno_tag.get('corresp')
                        if corresp_name:
                            names_without_koha_id.add(corresp_name.strip())

                # Extracting VIAF authorities
                for idno_tag in parsed_xml.find_all('idno', {'type': 'VIAF_AUTH'}):
                    if idno_tag.text != "":
                        viaf_id = (idno_tag.text.replace("VIAF_AUTH:", "")
                                   .replace("VIAF:", "").strip())
                        corresp_name = idno_tag.get('corresp').strip()
                        if corresp_name:
                            viaf_id_dict[viaf_id].add(corresp_name.strip())
                        else:
                            viaf_id_dict[koha_id].add("")
                    else:
                        corresp_name = idno_tag.get('corresp')
                        if corresp_name:
                            names_without_viaf_id.add(corresp_name.strip())

            write_to_tsv(koha_id_dict, names_without_koha_id, viaf_id_dict, names_without_viaf_id)


def write_to_tsv(koha_dict, koha_names_set, viaf_dict, viaf_names_set):
    """
    Writes the values of the dictionary into a single line of the TSV.

    Parameters:
    - data_dict (dict): Dictionary containing values.
    """
    with open('koha_id_list.tsv', 'w', encoding='utf-8') as tsv_file:
        for key in koha_dict.keys():
            value = koha_dict[key]
            value.discard("")
            tsv_file.write(key + '\t' + "; ".join(value) + '\n')

    with open('names_without_Koha_id', 'w', encoding='utf-8') as tsv_file:
        for i in sorted(koha_names_set):
            tsv_file.write(i + '\n')

    with open('viaf_id_list.tsv', 'w', encoding='utf-8') as tsv_file:
        for key in viaf_dict.keys():
            value = viaf_dict[key]
            value.discard("")
            tsv_file.write(key + '\t' + "; ".join(value) + '\n')

    with open('names_without_viaf_id', 'w', encoding='utf-8') as tsv_file:
        for i in sorted(viaf_names_set):
            tsv_file.write(i + '\n')


folder_path = '/home/eltedh/PycharmProjects/DATA/migration/'
create_dictionary(folder_path)



