import re
from RMKT_17_6.koha2itidata import idno_koha2itidata, tsv_to_dict
import xml.dom.minidom

from xml_methods import parse_xml, get_filenames


def change_header(parsed_xml, xml_path):
    new_header_tei = parse_xml('perfect-rmkt-17-16-tei-header.xml')
    new_header = new_header_tei.teiHeader
    old_header = parsed_xml.teiHeader
    new_title_stmt = new_header.titleStmt

    new_title_stmt.replace_with(old_header.titleStmt)

    num_title = new_header.titleStmt.find('title', {'type': 'num'})
    if num_title:
        if num_title.text.strip() == "":
            num_title.extract()

    # # Replace num title
    # old_num = old_header.titleStmt.find('title', {'type': 'num'})
    # new_num = new_header.titleStmt.find('title', {'type': 'num'})
    # if old_num:
    #     new_num.string = old_num.string
    #
    # # Replace main title
    # old_main = old_header.titleStmt.find('title', {'type': 'main'})
    # new_main = new_header.titleStmt.find('title', {'type': 'main'})
    # if old_main and new_main:
    #     new_main.string = old_main.string

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
        PID = 'rmkt-17-16.tei.' + old_file_info.split('-')[1].lower() + '-' + old_file_info.split('-')[0].lower()
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


def prettify_xml(xml_string):
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml(indent=' ')

tsv_path = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data_RMKT/itidata_koha_pim_biblio_auth_geo.csv"
path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-16/"]
koha_dict = tsv_to_dict(tsv_path)


for parsed, path in get_filenames(path_list):
    # Change the header to a new on
    change_header(parsed, path)

    # Exchange KOHA id-s to ITIdata items
    soup_new = idno_koha2itidata(parsed, path, koha_dict)

    # Get the PID to build filename
    new_filename = soup_new.find('idno', {'type': 'PID'}).string + '.xml'

    # Prettify
    string = str(soup_new)
    string = string.replace('\t', '')
    string = string.replace('\n', '')
    string = re.sub(r'\s+', ' ', string)

    # Save the modified XML back to a file
    # print(path, new_filename)
    new_path = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/XML/"

    with open(new_path + new_filename, 'w', encoding='utf-8') as file:
        file.write(string)
