# This python code reads data from the TEI header of the Arany correcpondence files
# and formats them to be uploaded to a wikibase instance
import csv

from xml_methods import get_filenames, revert_persname, normalize_allcaps, normalize_whitespaces, write_to_csv

with open("/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_itidata/itidata_query_manuscript_collection.csv",
          "r", encoding="utf-8") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter="\t")
    insitution_name_dict = {}
    for row in csv_reader:
        insitution_name_dict[row[1]] = (row[0], row[2])
for key, value in insitution_name_dict.items():
    print(key, value)


def create_dictionary(soup, path):
    """
    Creates a dictionary with keys 'Lhu' and 'Len' based on the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): BeautifulSoup object representing the parsed XML.
    """
    data_dict_letter = {}
    data_dict_manuscript = {}

    # Extract data for 'Lhu'
    head = soup.body.div.find('head')
    for tag in head.find_all('note'): # Leave out placeName or date tags from note type critic
        tag.decompose()
    title = head.find('title').text
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
    # print(lhu_value, path)

    # Sender and receiver namespace identity
    sender_id_tag = soup.correspDesc.find("correspAction", attrs={"type": "sent"}).persName
    if sender_id_tag and sender_id_tag.idno:
        sender_id = sender_id_tag.idno.text
    else:
        sender_id = None

    recipient_id_tag = soup.correspDesc.find("correspAction", attrs={"type": "recieved"}).persName
    if recipient_id_tag and recipient_id_tag.idno:
        recipient_id = recipient_id_tag.idno.text
    else:
        recipient_id = None

    # Extract data for 'Dhu', 'Den'
    hu_desciption = []
    en_description = []
    sender_tag = soup.correspDesc.find("correspAction", attrs={"type": "sent"})
    if sender_tag and sender_id_tag and sender_id_tag.idno:
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

    # Populate dictionary for letters
    data_dict_letter['qid'] = ""
    data_dict_letter['Lhu'] = lhu_value
    data_dict_letter['Len'] = lhu_value
    data_dict_letter['Dhu'] = ", ".join(hu_desciption)
    data_dict_letter['Den'] = ", ".join(en_description)
    data_dict_letter['P1'] = "Q26"
    data_dict_letter['P7'] = sender_id
    data_dict_letter['P80'] = recipient_id
    data_dict_letter['P41'] = "Q26"
    data_dict_letter['P44'] = id_edition
    data_dict_letter['P49'] = "0."
    data_dict_letter['P106'] = series_ordinal
    data_dict_letter['P18'] = "Kritikai jegyzetek: 0. oldal. (magyar)"
    data_dict_letter['P57'] = "+" + publication_date + '-00-00T00:00:00Z/9'

    write_to_csv(data_dict_letter, 'xml_header_tsv_letter.tsv')

    # Manuscript description
    if soup.msDesc.msIdentifier.find('institution') is None:
        institution_abr = "elveszett"
    else:
        institution = soup.msDesc.msIdentifier.find('institution').text.strip()
        if institution in insitution_name_dict:
            institution_abr = insitution_name_dict[institution][1]
        else:
            # print("Unknown insitution name: ", institution)
            institution_abr = "Unknown"
    manuscript_description_hu = sender + ", kézirat, " + institution_abr


    # Populate dictionary for manuscripts
    data_dict_manuscript['qid'] = ""
    data_dict_manuscript['P1'] = "Q15"
    data_dict_manuscript['Lhu'] = lhu_value
    data_dict_manuscript['Len'] = lhu_value
    data_dict_manuscript['Dhu'] = manuscript_description_hu
    data_dict_manuscript['Den'] = manuscript_description_hu.replace("elveszett", "lost").replace("kézirat", "manuscript")

    write_to_csv(data_dict_manuscript, 'xml_header_tsv_manuscript.tsv')


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


# Example usage:
folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]
with open('xml_header_tsv_letter.tsv', "w", encoding="utf8") as f1:
    with open('xml_header_tsv_manuscript.tsv', "w", encoding="utf8") as f2:
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


