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


def iterate_xml_files(folder_path):
    """
    Iterates through each XML file in the given folder path.
    Calls parse_xml function for each file.

    Parameters:
    - folder_path (str): Path of the folder containing XML files.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            xml_path = os.path.join(folder_path, filename)
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

    # Extract data for 'Dhu', 'Den'
    hu_desciption = []
    en_description = []
    sender_tag = soup.correspDesc.find("correspAction", attrs={"type": "sent"})
    if sender_tag:
        sender_tag.persName.idno.decompose()
        sender = sender_tag.persName.text
        print(sender)
    else:
        sender = "Unknown sender"
    if "ajom17" in soup.find("publicationStmt").text:
        edition = "Arany János levelezése. (1857–1861), 2004"
    elif "ajom18" in soup.find("publicationStmt").text:
        edition = "Arany János levelezése. (1862–1865), 2014"
    elif "ajom19" in soup.find("publicationStmt").text:
        edition = "Arany János levelezése. (1866–1882), 2015"
    else:
        edition = "Unknown edition"
        print(soup.publicationStmt.text)
    hu_desciption.append(sender)
    hu_desciption.append(edition)
    en_description.append(revert_persname(sender))
    en_description.append(edition)

    # Populate dictionary
    data_dict['Lhu'] = normalize_whitespaces(lhu_value)
    data_dict['Len'] = normalize_whitespaces(lhu_value)
    data_dict['Dhu'] = ", ".join(hu_desciption)
    data_dict['Den'] = ", ".join(en_description)

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
    - data_dict (dict): Dictionary containing values for 'Lhu' and 'Len'.
    """
    with open('output.tsv', 'a', encoding='utf-8') as tsv_file:
        tsv_file.write(f"{data_dict['Lhu']}\t{data_dict['Len']}\t{data_dict['Dhu']}\t{data_dict['Den']}\n")


# Example usage:
folder_path = '/home/eltedh/PycharmProjects/DATA/Arany XML/a_tei xml_final'
iterate_xml_files(folder_path)

'''
import os
import csv
import lxml
from bs4 import BeautifulSoup


def iterate_xml_files(folder_path):
    """
    Function to iterate through each XML file in the given folder.
    """
    xml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')]

    for xml_file in xml_files:
        xml_path = os.path.join(folder_path, xml_file)
        parse_xml_header(xml_path)


def parse_xml_header(xml_path):
    """
    Function to parse the TEI XML header and extract relevant information.
    """
    with open(xml_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, 'xml')

    # Extract information from the TEI header
    header_dict = create_header_dict(soup)

    # Write the values to CSV
    write_to_csv(header_dict)


def create_header_dict(soup):
    """
    Function to create a dictionary with 'Lhu' and 'Len' as keys and their respective values.
    """
    header_dict = {}

    # Extract 'Lhu' and 'Len' values from the TEI header
    title = soup.find('titleStmt').find('title').get_text(strip=True, separator=' ')

    # Normalize 'Lhu' and 'Len' values
    header_dict['Lhu'] = normalize_string(title)
    header_dict['Len'] = normalize_string(title)

    return header_dict


def normalize_string(input_str):
    """
    Function to normalize the input string as per the specified rules.
    """
    # Convert to ALLCAPS and then capitalize only the first character of person names
    words = input_str.upper().split()
    normalized_words = [word.capitalize() if word.isalpha() else word for word in words]
    normalized_str = ' '.join(normalized_words)
    return normalized_str


def write_to_csv(header_dict):
    """
    Function to write values from the dictionary to a CSV file.
    """
    csv_file_path = 'output.csv'

    # Check if the CSV file already exists, if not, create a new one with header
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=['Lhu', 'Len'])
            csv_writer.writeheader()

    # Append values to the CSV file
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=['Lhu', 'Len'])
        csv_writer.writerow(header_dict)


# Example usage
folder_path = '/home/eltedh/PycharmProjects/DATA/Arany XML/a_tei xml_final'
iterate_xml_files(folder_path)
'''
