# This python code reads data from the TEI header of the Arany correcpondence files
# and formats them to be uploaded to a wikibase instance
import csv

from xml_methods import get_filenames, revert_persname, normalize_allcaps, normalize_whitespaces, write_to_csv

with open(
        "/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_itidata/itidata_query_manuscript_collection.csv",
        "r", encoding="utf-8") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter="\t")
    insitution_name_dict = {}
    for row in csv_reader:
        insitution_name_dict[row[1]] = (row[0], row[2])
# for key, value in insitution_name_dict.items():
#     print(key, value)


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
    for tag in head.find_all('note'):  # Leave out placeName or date tags from note type critic
        tag.decompose()
    title = head.find('title').text
    title = normalize_allcaps(title)
    elveszett = " [Elveszett]," if (soup.find('term', string='Elveszett.')
                                    or soup.find('supplied', string="Elveszett")) else ","
    place_name_letter = get_text_with_supplied(head, 'placeName')
    place_name_letter = normalize_whitespaces(place_name_letter)
    if place_name_letter != "":
        place_name_letter += ", "
    try:
        if head.date.next_sibling and head.date.next_sibling.name is None:
            pass
            print(head.date.next_sibling.name, "///", normalize_whitespaces(head.date.next_sibling.text), "///", path.split("/")[-1])
    except AttributeError:
        pass
        # print("No date in <head>", path)
    date = get_text_with_supplied(head, 'date')
    date = normalize_whitespaces(date)

    lhu_value = f"{title}{elveszett} {place_name_letter}{date}"
    # print(lhu_value, path)

    # Sender and receiver namespace identity
    sender_id_list = []
    sent_action = soup.profileDesc.find("correspAction", attrs={"type": "sent"})
    if sent_action:
        sender_name_list = sent_action.find_all('persName')
        if len(sender_name_list) > 1:
            # print("More sender in: ", path)
            pass
        for sender_name in sender_name_list:
            if sender_name.idno:
                sender_id_list.append(sender_name.idno.text)
                if sender_name.idno.string is None:
                    pass
                    # print("No sender idno value: ", path, sender_name.parent.name, sender_name)
            else:
                pass
                # print("No sender idno: ", path)
    sender_id = ";".join(sender_id_list)

    recipient_id_list = []
    recipient_action = soup.profileDesc.find("correspAction", attrs={"type": "recieved"})
    if recipient_action:
        recipient_name_list = recipient_action.find_all('persName')
        if len(recipient_name_list) > 1:
            # print("More recipient in: ", path)
            pass
        for recipient_name in recipient_name_list:
            if recipient_name.idno:
                recipient_id_list.append(recipient_name.idno.text)
                if recipient_name.idno.string is None:
                    pass
                    # print("No recipient idno string: ", path, recipient_name.parent.name, recipient_name)
            else:
                pass
                # print("No recipient idno: ", path)
    recipient_id = ";".join(recipient_id_list)

    # Extract data for 'Dhu', 'Den'
    hu_desciption = []
    en_description = []
    senders = []
    senders_en = []
    if sent_action:
        for sender_name in sent_action.find_all('persName'):
            if sender_name.idno:
                sender_name.idno.decompose()
            senders.append(normalize_whitespaces(sender_name.text))
        senders_en = (revert_persname(sender) for sender in senders)

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

    hu_desciption.append(" és ".join(senders))
    hu_desciption.append("levél")
    hu_desciption.append(edition)
    en_description.append(" and ".join(senders_en))
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
    manuscript_description_hu = " és ".join(senders) + ", kézirat, " + institution_abr
    manuscript_description_en = " and ".join(senders_en) + ", manuscript" + institution_abr

    # Creation placeName
    place_name_manuscript = head.find('placeName')
    if place_name_manuscript:
        place_name_manuscript = normalize_whitespaces(place_name_manuscript.text)
    else:
        place_name_manuscript = "???"

    # Populate dictionary for manuscripts
    data_dict_manuscript['qid'] = ""
    data_dict_manuscript['P1'] = "Q15"
    data_dict_manuscript['Lhu'] = lhu_value
    data_dict_manuscript['Len'] = lhu_value
    data_dict_manuscript['Dhu'] = manuscript_description_hu
    data_dict_manuscript['Den'] = manuscript_description_hu.replace("elveszett", "lost").replace("kézirat",
                                                                                                 "manuscript")
    data_dict_manuscript['P7'] = sender_id
    data_dict_manuscript['P80'] = recipient_id
    data_dict_manuscript['P41'] = "Q26"
    data_dict_manuscript['P85'] = place_name_manuscript

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
