import csv
import re
from bs4 import BeautifulSoup
import os


def normalize(string):
    string = string.strip()
    string = string.replace('\t', '')
    string = string.replace('\n', '')
    string = re.sub(r'\s+', ' ', string)
    return string


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


def write_dict_to_tsv(input_dict, output_file):
    # Check if the file exists (to determine if it's the first time)
    try:
        with open(output_file, 'r', encoding='utf-8') as existing_file:
            # If the file already exists, read the existing header
            existing_header = existing_file.readline().strip().split('\t')
            write_header = False
    except FileNotFoundError:
        # If the file doesn't exist, set write_header to True
        write_header = True

    # Open the file in append mode with newline='' to ensure consistent line endings
    with open(output_file, 'a', encoding='utf-8', newline='') as file:
        # Create a CSV writer with tab as the delimiter
        writer = csv.writer(file, delimiter='\t')

        # If it's the first time, or if the header is not present in the existing file, write the header
        if write_header or not existing_header:
            writer.writerow(input_dict.keys())

        # Write a single row based on dictionary values
        writer.writerow(input_dict.values())


def tsv_from_xml(parsed_xml, xml_path):
    tsv_dict = {}

    # PID
    PID = parsed_xml.find('idno', {'type': 'PID'}).text.strip()
    tsv_dict['PID'] = PID

    # Main title
    tsv_dict['title'] = normalize(parsed_xml.find('title', {'type': 'main'}).text)

    # Fixed values
    tsv_dict['communities'] = 'critical-editions'
    tsv_dict['Resource type'] = 'Dataset'

    # Creators
    creator_string = ""
    for num, name_tag in enumerate(parsed_xml.find_all('respStmt')):
        if name_tag.persName:
            orc_id = ""
            if name_tag.find('idno', {'type': 'ORCID'}):
                orc_id = '|Name_identifiers:ORCID:' + name_tag.find('idno', {'type': 'ORCID'}).text
            creator_string += ('Person|' +
                               'Family_name:' + name_tag.surname.text.strip() + '|' +
                               'Given_name:' + name_tag.forename.text.strip() +
                               orc_id + '|' +
                               'Role:Editor' + '\n')
        tsv_dict['Creators'] = creator_string

    # Licences
    tsv_dict['Licenses'] = 'Creative Commons Attribution Non Commercial No Derivatives 4.0 International'

    # Contributors
    contributor_string = ""
    for num, name_tag in enumerate(parsed_xml.titleStmt.find_all('author')):
        if name_tag.persName:
            orc_id = ""
            if name_tag.find('idno', {'type': 'ORCID'}):
                orc_id = '|Name_identifiers:ORCID:' + name_tag.find('idno', {'type': 'ORCID'}).text
            contributor_string += ('Person|' +
                                   'Family_name:' + name_tag.surname.text.strip() + '|' +
                                   'Given_name:' + name_tag.forename.text.strip() +
                                   orc_id + '|' +
                                   'Role:Editor') + '\n'
            tsv_dict['Contributors'] = contributor_string

    # Subjects
    tsv_dict['Subjects'] = ("Languages and literature" + "|" +
                            "Digital Scholarly Edition" + "|" +
                            "Hungarian poetry" + "|" +
                            "XVII. Century")

    # Languages
    tsv_dict['Languages'] = ("Hungarian" + "|" + "Latin")

    # Dates
    tsv_dict['Dates'] = ("Date:1971" + "|" + "Type:Issued" + "|" + "Description:Publication of the print version")

    # Version
    tsv_dict['Version'] = "1.0"

    # Publisher
    tsv_dict['Publisher'] = "DigiPhil"

    # Alternate identifiers
    tsv_dict['Alternate Identifiers'] = ("Identifer:" + "20.500.14368/" + PID + "|" + "Scheme:" + "Handle")

    # Related works
    related_lines = ""
    github_file_link = parsed_xml.publicationStmt.find('ref', {'target': True})['target']
    DOI = parsed_xml.find('idno', {'type': 'DOI'}).text.strip()
    idno_itidata = parsed_xml.find('sourceDisc').find('bibl').find('idno', {'type': 'ITIdata'}).text.strip()
    related_works = (["Is part of", DOI, "DOI", "Dataset"],
                     ["Has version", github_file_link, "URL", "Dataset"],
                     ["Is described by", "https://digiphil.hu/gallery/regi-magyar-koltok-tara-17-szazad/", "URL",
                      "Publication / Other"],
                     ["Is described by", idno_itidata, "URL", "Dataset"]
                     )
    for related_work in related_works:
        related_lines += ("Relation:" + related_work[0] + "|" +
                          "Identifier:" + related_work[1] + "|" +
                          "Scheme:" + related_work[2] + "|" +
                          "Resource type:" + related_work[3] + "\n")
    tsv_dict['Related works'] = related_lines

    return tsv_dict


path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/modified-rmkt-17-6"]
invenio_tsv = "invenio_tsv.tsv"

for parsed, path in get_filenames(path_list):
    tsv_dict = tsv_from_xml(parsed, path)
    write_dict_to_tsv(tsv_dict, invenio_tsv)
