import os
import re
from bs4 import BeautifulSoup
from RMKT_17_6.koha2itidata import idno_koha2itidata, tsv_to_dict


def ends_with_numbers_or_f_j(filename):
    pattern1 = r'\d+\.xml$'
    pattern2 = r'[fj]-\d'
    return re.search(pattern1, filename) is not None or re.search(pattern2, filename) is not None


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


def change_header(parsed_xml, xml_path):
    new_header = parse_xml('/home/eltedh/PycharmProjects/XML-processing/RMKT_17_6/perfect-rmkt-17-6-header.xml')
    old_header = parsed_xml.teiHeader

    # Replace num title
    old_num = old_header.titleStmt.find('title', {'type': 'num'})
    new_num = new_header.titleStmt.find('title', {'type': 'num'})
    if old_num and new_num:
        new_num.string = old_num.string

    # Replace main title
    old_main = old_header.titleStmt.find('title', {'type': 'main'})
    new_main = new_header.titleStmt.find('title', {'type': 'main'})
    if old_main and new_main:
        new_main.string = old_main.string

    # Create PID
    if old_num:
        verse_num = old_num.string.replace('.', '')
        if verse_num.isnumeric() is not True:
            print('Verse number is not a number!')
    else:
        pattern = r'[fj]-\d'
        match = re.search(pattern, xml_path.split('/')[-1])
        verse_num = match.group(0)
        # print(xml_path, verse_num)
    PID = 'rmkt-17-6.tei.' + verse_num
    new_header.find('idno', {'type': 'PID'}).string = PID

    # Add GitHub link
    ref_github = new_header.find('ref', {'target': 'https://github.com/digiphil-hu/rmkt-17-6/blob/main/'})
    ref_github['target'] = 'https://github.com/digiphil-hu/rmkt-17-6/blob/main/' + PID + ".xml"

    # Add listWit
    if old_header.listWit:
        new_header.listWit.replace_with(old_header.listWit)
    else:
        new_header.listWit.extract()

    # Add notes statements
    if old_header.notesStmt:
        new_header.notesStmt.replace_with(old_header.notesStmt)
    else:
        new_header.notesStmt.extract()

    # Rewrite header
    parsed_xml.teiHeader.replace_with(new_header)
    return parsed_xml


tsv_path = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data_RMKT/itidata_koha_pim_biblio_auth_geo.csv"
path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-16"]
koha_dict = tsv_to_dict(tsv_path)


for parsed, path in get_filenames(path_list):
    # if ends_with_numbers_or_f_j(path):
    #     change_header(parsed, path)
    soup_new = idno_koha2itidata(parsed, path, koha_dict)

    # Save the modified XML back to a file
    new_filename = soup_new.find('idno', {'type': 'PID'}).string + '.xml'
    # print(path, new_filename)
    new_path = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/XML/"

    with open(new_path + new_filename, 'w', encoding='utf-8') as file:
        file.write(str(soup_new))
