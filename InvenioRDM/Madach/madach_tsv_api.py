import csv
import datetime
from bs4 import BeautifulSoup
from InvenioRDM.dict_to_json import create_json_data
from xml_methods import prettify_soup, get_filenames, normalize


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
    tsv_dict['Filename'] = PID + ".xml"

    # Main title
    # main_title = normalize(parsed_xml.titleStmt.find('title', {'type': 'main'}).text)
    main_title = normalize(parsed_xml.find('title').text)
    tsv_dict['Title'] = main_title

    # Description
    description = normalize(parsed_xml.publicationStmt.text)
    # desciption = ("<p> "
    #               + "<br> ".join(series_title) + "<br> "
    #               + main_title + "</p")
    tsv_dict['Description'] = description

    # Fixed values
    tsv_dict['Communities'] = 'critical-editions'
    tsv_dict['Resource type'] = 'Dataset'

    # Creators
    creators_list = []
    editor_list = ["editor", "editor in chief", "TEI-specification", "editor of the digital edition"]
    for num, contrib in enumerate(parsed_xml.editionStmt.find_all('respStmt')):
        for creator in contrib.find_all('persName'):
            if creator.previous_sibling.string in editor_list:
                creator_list = [creator.surname.text.strip(),
                                " ".join([creator_forename.text.strip() for creator_forename in creator.find_all("forename")]),
                                "Editor"]
                orc_id, isni_id = ("", "")
                if creator.find('idno', {'type': 'ORCID'}):
                    orc_id = "ORCID:" + creator.find('idno', {'type': 'ORCID'}).text
                # TODO: ISNI id-s to XML!
                if creator.find('idno', {'type': 'ISNI'}):
                    isni_id = ("ISNI:" + creator.find('idno', {'type': 'ISNI'}).text)
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
    for num, author in enumerate(parsed_xml.titleStmt.find_all('author')):
        for contrib in author.find_all('persName'):
            if contrib.surname:
                contributor_list = [contrib.surname.text.strip(), contrib.forename.text.strip(), "Other"]
            else:
                contributor_list = [contrib.persName.text.strip(), "", "Other"]
            orc_id, isni_id = ("", "")
            if contrib.find('idno', {'type': 'ORCID'}):
                orc_id = "ORCID:" + contrib.find('idno', {'type': 'ORCID'}).text
            # TODO: ISNI id-s to XML!
            if contrib.find('idno', {'type': 'ISNI'}):
                isni_id = ("ISNI:" + contrib.find('idno', {'type': 'ISNI'}).text)
            if orc_id != "":
                contributor_list.append(orc_id)
            if isni_id != "":
                contributor_list.append(isni_id)
            contributors_list.append(contributor_list)
        tsv_dict['Contributors'] = contributors_list
    if len(contributors_list) < 1:
        tsv_dict['Contributors'] = []

    # Subjects
    tsv_dict['Subjects'] = ["Languages and literature",
                            "Digital Scholarly Edition",
                            "Hungarian drama",
                            "XIX. Century"]

    # Languages
    language_list = get_languages(parsed_xml)
    tsv_dict['Languages'] = language_list

    # Dates
    print_edition_date = parsed_xml.sourceDesc.bibl.find('date')['when']
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")
    tsv_dict['publication_date'] = formatted_date
    tsv_dict['Dates'] = [[print_edition_date, "Issued", "Publication of the print version"]]

    # Version
    tsv_dict['Version'] = "1.0"

    # Publisher
    tsv_dict['Publisher'] = "DigiPhil"

    # Alternate identifiers
    tsv_dict['Alternate Identifiers'] = [[("20.500.14368/" + PID), "Handle"]]

    # Related works #TODO GitHub repo name from XML
    github_file_link = parsed_xml.publicationStmt.find('ref', {'target': True})['target']
    DOI = parsed_xml.find('idno', {'type': 'DOI'}).text.strip()
    # idno = parsed_xml.publicationStmt.find('idno', {'type': 'ITIdata'}, recursive=False)
    # idno_itidata = ("https://itidata.abtk.hu/wiki/item:" + idno.text)
    related_works = [["Is part of", DOI, "DOI", "Dataset"],
                     ["Has version", github_file_link, "URL", "Dataset"],
                     ["Is described by", "https://digiphil.hu/gallery/az-ember-tragediaja-2/", "URL",
                      "Publication"]
                    # ,["Is described by", idno_itidata, "URL", "Dataset"]
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
    language_list = [(lan + ":" + european_languages[lan]) for lan in language_codes_set]
    return language_list

# OLAHUS saját path
path_list = ["/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Genetikus-szöveg"]
invenio_tsv = "madach_invenio_tsv.tsv"

# TODO: tsv and Json creation do not run in parallel
for parsed, path in get_filenames(path_list):
    parsed = prettify_soup(parsed)
    new_soup = BeautifulSoup(parsed, 'xml')
    tsv_dict = tsv_from_xml(new_soup, path)
    write_dict_to_tsv(tsv_dict, invenio_tsv)
    json_folder = "/Madach_json"
    # create_json_data(tsv_dict, json_folder)
