import os
import re
from bs4 import BeautifulSoup
from RMKT_17_6.koha2itidata import idno_koha2itidata, tsv_to_dict


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
    new_header_tei = parse_xml('perfect-rmkt-17-16-tei-header.xml')
    new_header = new_header_tei.teiHeader
    old_header = parsed_xml.teiHeader

    # Replace num title
    old_num = old_header.titleStmt.find('title', {'type': 'num'})
    new_num = new_header.titleStmt.find('title', {'type': 'num'})
    if old_num:
        new_num.string = old_num.string

    # Replace main title
    old_main = old_header.titleStmt.find('title', {'type': 'main'})
    new_main = new_header.titleStmt.find('title', {'type': 'main'})
    if old_main and new_main:
        new_main.string = old_main.string

    # Create PID
    old_file_info = xml_path.split('/')[-1].split('.xml')[0].replace('RMKT-XVII-16-', '')
    if old_file_info == "-0-Előszó":
        PID = "rmkt-17-16.tei.eloszo"
    elif old_file_info == "-01-Bevezetés":
        PID = "rmkt-17-16.tei.bevezeto"
    elif old_file_info == "KIJegyzetek":
        PID = "rmkt-17-16.tei.ki-jegyzetek"
    elif old_file_info == "KPJegyzetek":
        PID = "rmkt-17-16.tei.kp-jegyzetek"
    elif old_file_info == "PKSZJegyzetek":
        PID = "rmkt-17-16.tei.pksz-jegyzetek"
    elif old_file_info == "RDJegyzetek":
        PID = "rmkt-17-16.tei.rdj-jegyzetek"
    else:
        PID = 'rmkt-17-16.tei.' + old_file_info.split('-')[1] + '-' + old_file_info.split('-')[0]
    new_header.find('idno', {'type': 'PID'}).string = PID

    # Add GitHub link
    ref_github = new_header.find('ref', {'target': True})
    ref_github['target'] = 'https://github.com/digiphil-hu/rmkt-17-16/blob/main/' + PID + ".xml"

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
path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/modified-rmkt-17-16"]
koha_dict = tsv_to_dict(tsv_path)


for parsed, path in get_filenames(path_list):

    change_header(parsed, path)
    soup_new = idno_koha2itidata(parsed, path, koha_dict)

    # Save the modified XML back to a file
    new_filename = soup_new.find('idno', {'type': 'PID'}).string + '.xml'
    # print(path, new_filename)
    new_path = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/XML/"

    with open(new_path + new_filename, 'w', encoding='utf-8') as file:
        file.write(str(soup_new))
