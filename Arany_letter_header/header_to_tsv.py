# This python code reads data from the TEI header of the Arany correcpondence files
# and formats them to be uploaded to a wikibase instance

import os
from bs4 import BeautifulSoup
import lxml
import re
from xml_methods import get_filenames


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
    # Capitalize only the first character of person names
    word_list = []
    input_str = input_str.replace("-", "").replace("–", "")
    input_str = normalize_whitespaces(input_str).strip()
    words = input_str.split()
    for word in words:
        if not "." in word: # Do not capitalize abbreviations
            if word.startswith("("): # Capitalize (words)
                word = "(" + word[1:].capitalize()
            else:
                word = word.capitalize()
        word_list.append(word)
    # normalized_words = [word.capitalize() if word.isalpha() else word for word in words]
    normalized_str = ' '.join(word_list)
    return normalized_str


def normalize_whitespaces(input_str):
    """
    Function to normalize the input string by removing whitespaces.
    """
    input_str = re.sub(r"[\n\t]+", "", input_str)
    input_str = re.sub(r"\s+", " ", input_str)
    return input_str


def create_dictionary(soup, path):
    """
    Creates a dictionary with keys 'Lhu' and 'Len' based on the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): BeautifulSoup object representing the parsed XML.
    """
    data_dict = {}

    # Extract data for 'Lhu'
    head = soup.body.div.find('head')
    for tag in head.find_all('note'): # Leave out placeName or date tags from note type critic
        tag.decompose()
    title = head.find('title').text
    print(title)
    title = normalize_allcaps(title)
    elveszett = " [Elveszett]," if (soup.find('term', string='Elveszett.')
                                    or soup.find('supplied', string="Elveszett")) else ","
    place_name = get_text_with_supplied(head, 'placeName')
    place_name = normalize_whitespaces(place_name)
    if place_name != "":
        place_name += ", "
    date = get_text_with_supplied(head, 'date')
    date = normalize_whitespaces(date)

    lhu_value = f"{title}{elveszett} {place_name}{date}"
    print(lhu_value)

    # Sender and receiver namespace identity

    sender_id_tag = soup.correspDesc.find("correspAction", attrs={"type": "sent"}).persName.idno
    if sender_id_tag:
        sender_id = sender_id_tag.text
    else:
        sender_id = None

    recipient_id_tag = soup.correspDesc.find("correspAction", attrs={"type": "recieved"}).persName.idno
    if recipient_id_tag:
        recipient_id = recipient_id_tag.text
    else:
        recipient_id = None

    # Extract data for 'Dhu', 'Den'
    hu_desciption = []
    en_description = []
    sender_tag = soup.correspDesc.find("correspAction", attrs={"type": "sent"})
    if sender_tag and sender_id_tag:
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
    data_dict['Lhu'] = lhu_value
    data_dict['Len'] = lhu_value
    data_dict['Dhu'] = ", ".join(hu_desciption)
    data_dict['Den'] = ", ".join(en_description)
    data_dict['P1'] = "Q26"
    data_dict['P7'] = sender_id
    data_dict['P80'] = recipient_id
    data_dict['P41'] = "Q26"
    data_dict['P44'] = id_edition
    data_dict['P49'] = "0."
    data_dict['P106'] = series_ordinal
    data_dict['P18'] = "Kritikai jegyzetek: 0. oldal. (magyar)"
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
    with open('output.tsv', 'a', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join([str(value) for value in data_dict.values()]) + '\n')


# Example usage:
folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]
with open('output.tsv', "w", encoding="utf8") as f:
    # write header:
    header_list = ["qid",
                   "Lhu",
                   "Len",
                   "Dhu",
                   "Den",
                   "P1",
                   "P7",
                   "P80",
                   "P41",
                   "P44",
                   "P49",
                   "P106",
                   "P18",
                   "P57"]
    # f.write("\t".join(header_list) + "\n" + "\n")
for parsed, path in get_filenames(folder_list):
    create_dictionary(parsed, path)


