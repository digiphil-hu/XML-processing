import os
import re

from bs4 import BeautifulSoup


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
    string = re.sub(r'[^\w\s]', '', string)
    string = string.replace('\t', '').replace('\n', '')
    string = re.sub(r'\s+', ' ', string)
    return string