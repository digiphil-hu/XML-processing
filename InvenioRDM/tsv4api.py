import csv
import datetime
import re
from bs4 import BeautifulSoup
import os
from dict_to_json import create_json_data


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

        # Write a single row based on dictionary values.
        # Linebreaks stripped from cell endings.
        for key, value in input_dict.items():
            if isinstance(value, str):
                input_dict[key] = value.strip()
            elif isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], str):
                    input_dict[key] = ';'.join(value)
                elif isinstance(value[0], list):
                    input_dict[key] = "\n".join(";".join(inner_list) for inner_list in value)
        writer.writerow(input_dict.values())


def tsv_from_xml(parsed_xml, xml_path):
    tsv_dict = {}

    # PID
    PID = parsed_xml.find('idno', {'type': 'PID'}).text.strip()
    tsv_dict['filename'] = PID + ".xml"

    # Main title
    main_title = normalize(parsed_xml.titleStmt.find('title', {'type': 'main'}).text)
    tsv_dict['title'] = main_title

    # Description
    series_title = []
    for title in parsed_xml.sourceDesc.bibl.find_all('title'):
        series_title.append(normalize(title.text.strip()))
    desciption = ("<p>"
                  + "<br>".join(series_title) + "<br>"
                  + main_title + "</p")
    tsv_dict['description'] = desciption

    # Fixed values
    tsv_dict['communities'] = 'critical-editions'
    tsv_dict['Resource type'] = 'Dataset'

    # Creators
    creators_list = []
    for num, name_tag in enumerate(parsed_xml.find_all('respStmt')):
        if name_tag.persName:
            creator_list = [name_tag.surname.text.strip(), name_tag.forename.text.strip(), "Editor"]
            orc_id, isni_id = ("", "")
            if name_tag.find('idno', {'type': 'ORCID'}):
                orc_id = "ORCID:" + name_tag.find('idno', {'type': 'ORCID'}).text
            # TODO: ISNI id-s to XML!
            if name_tag.find('idno', {'type': 'ISNI'}):
                isni_id = ("ISNI:" + name_tag.find('idno', {'type': 'ISNI'}).text)
            if orc_id != "":
                creator_list.append(orc_id)
            if isni_id != "":
                creator_list.append(isni_id)
            creators_list.append(creator_list)
    tsv_dict['Creators'] = creators_list

    # Licences
    tsv_dict['Licenses'] = 'cc-by-nc-nd-4.0'

    # Contributors
    contributors_list = []
    for num, name_tag in enumerate(parsed_xml.titleStmt.find_all('author')):
        if name_tag.persName:
            if name_tag.surname:
                contributor_list = [name_tag.surname.text.strip(), name_tag.forename.text.strip(), "Other"]
            else:
                contributor_list = [name_tag.persName.text.strip(), "", "Other"]
            orc_id, isni_id = ("", "")
            if name_tag.find('idno', {'type': 'ORCID'}):
                orc_id = "ORCID:" + name_tag.find('idno', {'type': 'ORCID'}).text
            # TODO: ISNI id-s to XML!
            if name_tag.find('idno', {'type': 'ISNI'}):
                isni_id = ("ISNI:" + name_tag.find('idno', {'type': 'ISNI'}).text)
            if orc_id != "":
                contributor_list.append(orc_id)
            if isni_id != "":
                contributor_list.append(isni_id)
            contributors_list.append(contributor_list)
        tsv_dict['Contributors'] = contributors_list

    # Subjects
    tsv_dict['Subjects'] = ["Languages and literature",
                            "Digital Scholarly Edition",
                            "Hungarian poetry",
                            "XVII. Century"]

    # Languages
    language_list = get_languages(parsed_xml)
    tsv_dict['Languages'] = language_list

    # Dates
    print_edition_date = parsed_xml.sourceDesc.bibl.find('date')['when']
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")
    tsv_dict['publication_date'] = formatted_date
    tsv_dict['Dates'] = [print_edition_date, "Issued", "Publication of the print version"]

    # Version
    tsv_dict['Version'] = "1.0"

    # Publisher
    tsv_dict['Publisher'] = "DigiPhil"

    # Alternate identifiers
    tsv_dict['Alternate Identifiers'] = [("20.500.14368/" + PID), "Handle"]

    # Related works
    github_file_link = parsed_xml.publicationStmt.find('ref', {'target': True})['target']
    DOI = parsed_xml.find('idno', {'type': 'DOI'}).text.strip()
    idno = parsed_xml.sourceDesc.bibl.find('idno', {'type': 'ITIdata'}, recursive=False)
    idno_itidata = ("https://itidata.abtk.hu/wiki/item:" + idno.text)
    related_works = [["Is part of", DOI, "DOI", "Dataset"],
                     ["Has version", github_file_link, "URL", "Dataset"],
                     ["Is described by", "https://digiphil.hu/gallery/regi-magyar-koltok-tara-17-szazad/", "URL",
                      "Publication"],
                     ["Is described by", idno_itidata, "URL", "Dataset"]
                     ]
    tsv_dict['Related works'] = related_works

    return tsv_dict


def get_languages(parsed_xml):
    language_codes_set = set()
    language_list = []
    european_languages = {
        "hu": "Hungarian", "en": "English", "la": "Latin", "fr": "French", "de": "German",
        "es": "Spanish", "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "sv": "Swedish",
        "fi": "Finnish", "da": "Danish", "no": "Norwegian", "is": "Icelandic", "ga": "Irish",
        "sq": "Albanian", "el": "Greek", "ro": "Romanian", "bg": "Bulgarian", "hr": "Croatian",
        "sl": "Slovenian", "cs": "Czech", "sk": "Slovak", "pl": "Polish", "hu": "Hungarian",
        "et": "Estonian", "lv": "Latvian", "lt": "Lithuanian", "mt": "Maltese", "cy": "Welsh",
        "gd": "Scottish Gaelic",
    }
    for tag in parsed_xml.find_all(lambda t: t.has_attr('xml:lang')):
        lang_code = tag['xml:lang']
        language_codes_set.add(lang_code)
    for tag in parsed_xml.find_all('language', {'ident': True}):
        lang_code = tag['ident']
        language_codes_set.add(lang_code)
    if len(language_codes_set) == 0:
        language_codes_set.add("hu")
    language_list = [european_languages[lan] for lan in language_codes_set]
    return language_list


path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/modified-rmkt-17-6"]
invenio_tsv = "invenio_tsv.tsv"

for parsed, path in get_filenames(path_list):
    tsv_dict = tsv_from_xml(parsed, path)
    # write_dict_to_tsv(tsv_dict, invenio_tsv)
    json_folder = "/home/eltedh/PycharmProjects/XML-processing/InvenioRDM/JSON"
    create_json_data(tsv_dict, json_folder)

