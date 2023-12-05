# This code reads KOHA id-s to a TSV

import os
from bs4 import BeautifulSoup
import lxml
import re
from collections import defaultdict


def parse_xml(xml_path):
    """
    Parses the given XML file using BeautifulSoup.

    Parameters:
    - xml_path (str): Path of the XML file.
    """
    with open(xml_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    # print(xml_path)
    soup = BeautifulSoup(xml_content, 'xml')
    return soup


def create_koha_id_tsv(f_path_list, out_path):
    """
    This function creates a dictionary. Keys are the KOHA id's, values are the names given in the corresp attribute.
    :param out_path: Output will be written here.
    :param f_path_list: A list of folders containing XML files to iterate on.
    :return:
    """

    koha_id_dict = defaultdict(set)
    names_without_koha_id = set()
    viaf_id_dict = defaultdict(set)
    names_without_viaf_id = set()

    for f_path in f_path_list:
        for root, dirs, files in os.walk(f_path):
            for filename in files:
                if filename.endswith(".xml"):
                    xml_path = os.path.join(root, filename)
                    parsed_xml = parse_xml(xml_path)

                    # Extracting KOHA authorities
                    for idno_tag in parsed_xml.find_all('idno', {'type': 'KOHA_AUTH'}):
                        if idno_tag.string:
                            corresp_name = idno_tag.get('corresp')
                            koha_id = idno_tag.string
                            koha_id = re.sub(r'[^0-9]', '', koha_id)

                            # koha_id = idno_tag.string.replace("\n", "").replace("\t", "")
                            # koha_id = koha_id.replace("KOHA_AUTH:", "").replace("KOHA:", "")
                            # if not re.fullmatch(r'\d*', koha_id):
                            #     print(filename, "'", koha_id, "'", idno_tag)

                            if corresp_name and koha_id == "":
                                corresp_name = corresp_name.replace("\n", "").replace("\t", "").strip()
                                names_without_koha_id.add(corresp_name)
                            if corresp_name and koha_id != "":
                                corresp_name = corresp_name.replace("\n", "").replace("\t", "").strip()
                                koha_id_dict[koha_id].add(corresp_name)
                            else:
                                koha_id_dict[koha_id].add("")
                        else:
                            corresp_name = idno_tag.get('corresp')
                            if corresp_name:
                                corresp_name = corresp_name.replace("\n", "").replace("\t", "").strip()
                                names_without_koha_id.add(corresp_name)

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

                write_to_tsv(out_path, koha_id_dict, names_without_koha_id, viaf_id_dict, names_without_viaf_id)
    if koha_id != "":
        names_without_koha_id.add(corresp_name)
    else:
        koha_id_dict[koha_id].add(corresp_name)


def write_to_tsv(out_path, koha_dict, koha_names_set, viaf_dict, viaf_names_set):
    """
    Writes the values of the dictionary into a single line of the TSV.

    Parameters:
    - data_dict (dict): Dictionary containing values.
    """
    with open(out_path + 'koha_id_list.tsv', 'w', encoding='utf-8') as tsv_file:
        sorted_dict = sort_dict(koha_dict)
        for key in sorted_dict.keys():
            value = koha_dict[key]
            value.discard("")
            tsv_file.write(key + '\t' + "; ".join(value) + '\n')

    with open(out_path + 'names_without_Koha_id.tsv', 'w', encoding='utf-8') as tsv_file:
        for i in sorted(koha_names_set):
            tsv_file.write(i + '\n')

    with open(out_path + 'viaf_id_list.tsv', 'w', encoding='utf-8') as tsv_file:
        for key in viaf_dict.keys():
            value = viaf_dict[key]
            value.discard("")
            tsv_file.write(key + '\t' + "; ".join(value) + '\n')

    with open(out_path + 'names_without_viaf_id.tsv', 'w', encoding='utf-8') as tsv_file:
        for i in sorted(viaf_names_set):
            tsv_file.write(i + '\n')


def sort_dict(input_dict):
    out_dict = dict(sorted(input_dict.items(), key=lambda x: x[1]))
    return out_dict
