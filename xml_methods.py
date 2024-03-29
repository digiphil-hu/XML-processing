import difflib
import os
import re
from collections import Counter
from datetime import datetime
from bs4 import BeautifulSoup
import lxml

import get_geo_namespace_id_itidata

month_names_hu = {
        "January": "január",
        "February": "február",
        "March": "március",
        "April": "április",
        "May": "május",
        "June": "június",
        "July": "július",
        "August": "augusztus",
        "September": "szeptember",
        "October": "október",
        "November": "november",
        "December": "december"
    }


def parse_xml(xml_path):
    with open(xml_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    # print(xml_path)
    soup = BeautifulSoup(xml_content, 'xml')
    return soup


def get_filenames(f_path_list):
    for f_path in f_path_list:
        for root, dirs, files in os.walk(f_path):
            for filename in sorted(files):
                if filename.endswith(".xml"):
                    xml_path = os.path.join(root, filename)
                    parsed_xml = parse_xml(xml_path)
                    # print(xml_path)
                    yield parsed_xml, xml_path


def normalize(string):
    string = string.strip()
    string = string.replace('\t', '')
    string = string.replace('\n', '')
    string = re.sub(r'\s+', ' ', string)
    return string


def prettify_soup(soup):
    # Prettify
    string = str(soup)
    string = string.replace('\t', '')
    string = string.replace('\n', '')
    string = re.sub(r'\s+', ' ', string)
    return string


def compare_text_normalize(string):
    string = string.strip()
    string = re.sub(r'[^\w\s]', '', string)
    string = string.replace('\t', '').replace('\n', '')
    string = re.sub(r'\s+', ' ', string)
    return string


def visualize_diff(string_one, string_two):
    differ = difflib.Differ()
    diff = list(differ.compare(string_one, string_two))
    highlighted_diff = []
    for item in diff:
        if item.startswith('- '):
            highlighted_diff.append(f'\033[91m{item[2:]}\033[0m')  # Red color for deletions
        elif item.startswith('+ '):
            highlighted_diff.append(f'\033[92m{item[2:]}\033[0m')  # Green color for additions
        else:
            highlighted_diff.append(item)
    # print(''.join(highlighted_diff))


def find_difference_strings(str1, str2):
    # Find the longest common substring
    matcher = difflib.SequenceMatcher(None, str1, str2)
    match = matcher.find_longest_match(0, len(str1), 0, len(str2))

    # If there is a common substring
    if match.size > 4:
        # Extract the common substring
        common_substring = str1[match.a : match.a + match.size]

        # Delete the common substring and repeat the process
        str1 = str1.replace(common_substring, "")
        str2 = str2.replace(common_substring, "")

        # Recursively find the remaining differences
        remaining_str1, remaining_str2 = find_difference_strings(str1, str2)

        return remaining_str1, remaining_str2

    # If there is no common substring, return the original strings
    return str1, str2


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
        if not "." in word:  # Do not capitalize abbreviations
            if word.startswith("("):  # Capitalize (words)
                word = "(" + word[1:].capitalize()
            else:
                word = word.capitalize()
        word = re.sub(r"[Dd][Rr]\.", "Dr.", word)
        word = re.sub(r"É[sS]", " és ", word)
        word = word.replace("Üzenetváltása", "üzenetváltása")
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


def write_to_csv(data_dict, output_file):
    """
    Writes the values of the dictionary into a single line of the CSV.

    Parameters:
    - data_dict (dict): Dictionary containing values.
    """
    with open(output_file, 'a', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join([str(value) for value in data_dict.values()]) + '\n')


def get_parent_tags(xml_segment):
    """
    Get a list of parent tag names for a given XML segment.

    Parameters:
    - xml_segment (BeautifulSoup): BeautifulSoup object representing the XML segment.

    Returns:
    - list: List of parent tag names.
    """
    parent_tags = []

    # Start from the immediate parent and go upwards
    parent_tag = xml_segment.parent
    while parent_tag:
        parent_tags.insert(0, parent_tag.name)
        parent_tag = parent_tag.parent

    return parent_tags


def format_date(input_date):
    date_parts = input_date.split('-')

    # If only year is provided
    if len(date_parts) == 1:
        return f"{date_parts[0]}-00-00"
    # If year and month are provided
    elif len(date_parts) == 2:
        return f"{date_parts[0]}-{date_parts[1]}-00"
    # If year, month, and day are provided
    elif len(date_parts) == 3:
        return f"{date_parts[0]}-{date_parts[1]}-{date_parts[2]}"
    # If the input format is not recognize
    else:
        return "Invalid date format"


def format_iso_date_to_itidata(date_str):
    """
    Format date from ISO format (yyyy-mm-dd, yyyy-mm, yyyy) to wikidata fromat with precision: /9-11
    :param date_str:
    :return: wikidata formatted date
    """
    # Remove zero mm or dd and split the date string into components
    parts = date_str.replace("-00", "").split('-')

    # Determine the level of detail provided in the date
    if len(parts) == 1 and parts[0]:  # Only year is provided
        return f"+{parts[0]}-00-00T00:00:00Z/9"
    elif len(parts) == 2 and all(parts):  # Year and month are provided
        return f"+{parts[0]}-{parts[1]}-00T00:00:00Z/10"
    elif len(parts) == 3 and all(parts):  # Year, month, and day are provided
        return f"+{parts[0]}-{parts[1]}-{parts[2]}T00:00:00Z/11"
    else:
        return "Invalid input"


def check_list_index(index_number, list_to_check):
    try:
        list_to_check[index_number]
    except IndexError:
        list_to_check.insert(index_number, "")
    return list_to_check


def duplicate_list(list_in):
    if len(list_in) > len(set(list_in)):
        counter = Counter(list_in)
        duplicates = [value for value, count in counter.items() if count > 1]
        return duplicates
    else:
        return None


def convert_date(date_str):
    try:
        if len(date_str) == 4:
            year = int(date_str)
            return f"{year}."
        elif len(date_str) == 7:
            date_obj = datetime.strptime(date_str, "%Y-%m")
            month_name_hu = month_names_hu[date_obj.strftime("%B")]
            year = date_obj.year
            return f"{year}. {month_name_hu}"
        elif len(date_str) == 10:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_name_hu = month_names_hu[date_obj.strftime("%B")]
            day = date_obj.day
            year = date_obj.year
            return f"{year}. {month_name_hu} {day}."
        else:
            return "Invalid date format"
    except ValueError:
        return "Invalid date format"


def process_dictionary(input_dict):
    """

    :param input_dict: ITIdata JSON dict
    :return: dictionary with propertys as keys, itidata item labels as values
    """

    # Initialize an empty dictionary to hold the result
    result = {}

    # Navigate through the dictionary structure to extract the relevant information
    if 'entities' in input_dict:
        for item_id, item_data in input_dict['entities'].items():
            if 'claims' in item_data:
                for prop, claims in item_data['claims'].items():
                    for claim in claims:
                        if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                            value = claim['mainsnak']['datavalue']['value']
                            # Check if the value is a dictionary
                            if isinstance(value, dict):
                                # If 'id' is a key, use it; otherwise, use the first value from the dictionary
                                if 'id' in value:
                                    result_value = value['id']
                                else:
                                    first_key = next(iter(value))
                                    result_value = value[first_key]
                            else:
                                result_value = value
                            result[prop] = result_value

    for key, value in result.items():
        if value.lstrip('Q').isnumeric():
            result[key] = get_geo_namespace_id_itidata.get_eng_hun_item_labels_from_itidata(result[key], "")
    return result
