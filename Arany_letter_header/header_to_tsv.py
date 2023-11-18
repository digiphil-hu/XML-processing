# This python code reads data from the TEI header of the Arany correcpondence files
# and formats them to be uploaded to a wikibase instance

import os
from bs4 import BeautifulSoup
import lxml
import re


def revert_persname(name):
    # normalize whitespaces
    name = normalize_whitespaces(name)

    # Split the input name into words
    name_parts = name.split()

    # Check if there are at least two words (GivenName and FamilyName)
    if len(name_parts) >= 2:
        # Revert the order of the words
        english_name = f"{name_parts[-1]} {' '.join(name_parts[:-1])}"
        return english_name
    else:
        # Return the original name if it doesn't follow the expected format
        return name


def normalize_allcaps(input_str):
    """
    Function to normalize ALLCAPS input string as per the specified rules.
    """
    # Convert to ALLCAPS and then capitalize only the first character of person names
    words = input_str.upper().split()
    normalized_words = [word.capitalize() if word.isalpha() else word for word in words]
    normalized_str = ' '.join(normalized_words).replace("– ", "")
    return normalized_str


def normalize_whitespaces(input_str):
    """
    Function to normalize the input string by removing whitespaces.
    """
    input_str = re.sub(r"[\n\t]+", "", input_str)
    input_str = re.sub(r"\s+", " ", input_str)
    return input_str


def iterate_xml_files(f_path):
    """
    Iterates through each XML file in the given folder path.
    Calls parse_xml function for each file.

    Parameters:
    - folder_path (str): Path of the folder containing XML files.
    """
    for filename in os.listdir(f_path):
        if filename.endswith(".xml"):
            xml_path = os.path.join(f_path, filename)
            parse_xml(xml_path)


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
    create_dictionary(soup)


def create_dictionary(soup):
    """
    Creates a dictionary with keys 'Lhu' and 'Len' based on the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): BeautifulSoup object representing the parsed XML.
    """
    data_dict = {}

    # Extract data for 'Lhu'
    head = soup.body.div.find('head')
    title = head.find('title').text
    title = normalize_allcaps(title)
    elveszett = " [Elveszett]," if (soup.find('term', string='Elveszett.')
                                    or soup.find('supplied', string="Elveszett")) else ","
    place_name = get_text_with_supplied(head, 'placeName')
    if place_name != "":
        place_name += ", "
    date = get_text_with_supplied(head, 'date')

    lhu_value = f"{title}{elveszett} {place_name}{date}"

    # Sender and receiver namespace identity
    sender_id = soup.correspDesc.find("correspAction", attrs={"type": "sent"}).persName.idno.text
    recipient_id = soup.correspDesc.find("correspAction", attrs={"type": "recieved"}).persName.idno.text

    # Extract data for 'Dhu', 'Den'
    hu_desciption = []
    en_description = []
    sender_tag = soup.correspDesc.find("correspAction", attrs={"type": "sent"})
    if sender_tag:
        sender_tag.persName.idno.decompose()
        sender = normalize_whitespaces(sender_tag.persName.text)
    else:
        sender = "Unknown sender"
    if "ajom17" in soup.find("publicationStmt").text:
        edition = "Arany János levelezése. (1857–1861), 2004"
        id_edition = "Q338268"
        publication_date = "2004"
    elif "ajom18" in soup.find("publicationStmt").text:
        edition = "Arany János levelezése. (1862–1865), 2014"
        id_edition = "Q338270"
        publication_date = "2014"
    elif "ajom19" in soup.find("publicationStmt").text:
        edition = "Arany János levelezése. (1866–1882), 2015"
        id_edition = "Q338271"
        publication_date = "2015"
    else:
        edition = "Unknown edition"
        print(soup.publicationStmt.text)
    hu_desciption.append(sender)
    hu_desciption.append("levél")
    hu_desciption.append(edition)
    en_description.append(revert_persname(sender))
    en_description.append("letter")
    en_description.append(edition)

    # Number of letter
    pid = soup.publicationStmt.find("idno", {"type": "PID"}).text
    series_ordinal = pid.split(".")[-1]

    # Populate dictionary
    data_dict['qid'] = ""
    data_dict['Lhu'] = '"' + normalize_whitespaces(lhu_value) + '"'
    data_dict['Len'] = '"' + normalize_whitespaces(lhu_value) + '"'
    data_dict['Dhu'] = '"' + ", ".join(hu_desciption) + '"'
    data_dict['Den'] = '"' + ", ".join(en_description) + '"'
    data_dict['P1'] = "Q26"
    data_dict['P7'] = sender_id
    data_dict['P80'] = recipient_id
    data_dict['P41'] = "Q26"
    data_dict['P44'] = id_edition
    data_dict['P49'] = '""""' + "0." + '"'
    data_dict['P106'] = '""""' + series_ordinal + '"'
    data_dict['P18'] = '""""' + "Kritikai jegyzetek: 0. oldal. (magyar)" + '"'
    data_dict['P57'] = "+" + publication_date + '-01-01T00:00:00Z/9'
    write_to_csv(data_dict)


def get_text_with_supplied(soup, tag_name):
    """
    Gets the text value for the given tag, and adds '[' and ']' if it is under the 'supplied' tag.

    Parameters:
    - soup (BeautifulSoup): BeautifulSoup object representing the parsed XML.
    - tag_name (str): Name of the XML tag to extract.

    Returns:
    - str: Text value with optional '[' and ']' based on 'supplied' tag.
    """
    tag = soup.find(tag_name)
    if tag:
        if tag.parent.name == 'supplied':
            return f"[{tag.text.strip()}]"
        else:
            return tag.text.strip()
    return ""


def write_to_csv(data_dict):
    """
    Writes the values of the dictionary into a single line of the CSV.

    Parameters:
    - data_dict (dict): Dictionary containing values.
    """
    # with open('output.tsv', 'a', encoding='utf-8') as tsv_file:
    #     tsv_file.write(f"{data_dict['Lhu']}\t{data_dict['Len']}\t{data_dict['Dhu']}\t{data_dict['Den']}\n")
    with open('output.tsv', 'a', encoding='utf-8') as tsv_file:
        tsv_file.write(','.join([str(value) for value in data_dict.values()]) + '\n')


# Example usage:
folder_path = '/home/eltedh/PycharmProjects/DATA/Arany XML/a_tei xml_final'
with open('output.tsv', "w", encoding="utf8") as f:
    iterate_xml_files(folder_path)
