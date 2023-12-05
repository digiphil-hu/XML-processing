import os
import requests
from bs4 import BeautifulSoup

def convert_xml_to_docx(xml_path, log_file):
    # Read the XML file
    with open(xml_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # API endpoint for conversion with specified properties
    api_url = "https://teigarage2.tei-c.org/ege-webservice/Conversions/TEI%3Atext%3Axml/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/conversion?properties=<conversions><conversion index=\"0\"><property id=\"oxgarage.getImages\">true</property><property id=\"oxgarage.getOnlineImages\">true</property><property id=\"oxgarage.lang\">en</property><property id=\"oxgarage.textOnly\">false</property><property id=\"pl.psnc.dl.ege.tei.profileNames\">default</property></conversion></conversions>"

    # Send a POST request to the API
    response = requests.post(api_url, data=xml_content, headers={'Content-Type': 'application/xml'})

    # Check if the conversion is successful (status code 200)
    if response.status_code == 200:
        # Parse the response to check the conversion status
        soup = BeautifulSoup(response.content, 'html.parser')
        status = soup.find('status').text.strip()

        # Write to the log file
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"File: {xml_path}, Conversion Status: {status}\n")
    else:
        # Write to the log file in case of an error
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"File: {xml_path}, Conversion Error - Status Code: {response.status_code}\n")

def convert_xml_files_in_directory(input_directory, log_file):
    # Iterate over every XML file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.xml'):
            xml_path = os.path.join(input_directory, filename)
            convert_xml_to_docx(xml_path, log_file)

# Example usage:
input_directory = '/home/eltedh/PycharmProjects/DATA/EP_TR_manu/manuscript'
log_file = 'file.log'

# Clear the log file before starting
with open(log_file, 'w', encoding='utf-8'):
    pass

convert_xml_files_in_directory(input_directory, log_file)

