# This python code reads data from the TEI header of the Arany correcpondence files
# and formats them to be uploaded to a wikibase instance
import csv

from xml_methods import get_filenames, revert_persname, normalize_allcaps, normalize_whitespaces, write_to_csv, \
    format_date

with open(
        "/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_itidata/itidata_query_manuscript_collection.csv",
        "r", encoding="utf-8") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter="\t")
    insitution_name_dict = {}
    for row in csv_reader:
        insitution_name_dict[row[2]] = (row[0], row[3])
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
    place_name_letter = get_text_with_supplied(head, 'placeName', children=False)
    place_name_letter = normalize_whitespaces(place_name_letter)
    if place_name_letter != "":
        place_name_letter += ", "
    try:
        if head.date.next_sibling and head.date.next_sibling.name is None:
            pass
            # if head.date.next_sibling.text.replace(r"\s", "") != "":
            #     print(head.date.next_sibling.name, "///", normalize_whitespaces(head.date.next_sibling.text), "///", path.split("/")[-1])
    except AttributeError:
        pass
        # print("No date in <head>", path)
    date = get_text_with_supplied(head, 'date', children=True)
    date = normalize_whitespaces(date)

    lhu_value = f"{title}{elveszett} {place_name_letter}{date}"
    # print(lhu_value, path)

    # Sender and receiver namespace identity
    sender_id_list = []
    sent_action = soup.profileDesc.find("correspAction", attrs={"type": "sent"})
    if sent_action:
        sender_name_list = sent_action.find_all('persName')
        #Chech if there are more then one sender.
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
        # Check if there are multiple recievers
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
        senders_en = [revert_persname(sender) for sender in senders]

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

    # Manuscript description, manuscript institution, institution id
    institution_abbr = []
    institution_id = []
    if soup.msDesc.msIdentifier.find('institution') is not None:
        if soup.msDesc.msIdentifier.find('institution').text.strip() != "":
            institutions = soup.msDesc.msIdentifier.institution.text.split(";")
            for institution in institutions:
                institution = normalize_whitespaces(institution).lstrip()
                if institution in insitution_name_dict:
                    institution_abbr.append(insitution_name_dict[institution][1])
                    institution_id.append(insitution_name_dict[institution][0].split("/")[-1])
                else:
                    print("Unknown insitution name: ", institution)
    abbr_hu = " – ".join(institution_abbr) if len(institution_abbr) > 0 else "elveszett"
    abbr_en = " – ".join(institution_abbr) if len(institution_abbr) > 0 else "lost"
    manuscript_description_hu = " és ".join(senders) + ", kézirat, " + abbr_hu
    manuscript_description_en = " and ".join(senders_en) + ", manuscript, " + abbr_en

    # Manuscript institution record id
    record_id = ""
    itidata_id = ""
    for idno in parsed.msIdentifier.find_all("idno"):
        if idno.get("type") == "ITIdata" or idno.get("type") == "ITIData":
            itidata_id = normalize_whitespaces(idno.text)
        else:
            record_id = normalize_whitespaces(idno.text)

    # Creation placeName
    place_name_manuscript = soup.creation.find('placeName')
    if place_name_manuscript:
        place_name_manuscript = normalize_whitespaces(place_name_manuscript.idno.text)
    else:
        place_name_manuscript = "Unknown"

    # Creation date
    exact_date, from_date, to_date = "", "", ""
    if parsed.creation.find("date"):
        if parsed.creation.find("date").get("when"):
            exact_date = format_date(parsed.creation.find("date").get("when"))
        if parsed.creation.find("date").get("from"):
            from_date = format_date(parsed.creation.find("date").get("from"))
        if parsed.creation.find("date").get("to"):
            to_date = format_date(parsed.creation.find("date").get("to"))
        if exact_date == "Invalid date format" or from_date == "Invalid date format" or exact_date == "Invalid date format":
            print("Invalid date: ", path)
    # if exact_date != "":
    #     print("Exact date: ", exact_date)
    # if from_date != "":
    #     print("From date: ", from_date)
    # if to_date != "":
    #     print("To date: ", to_date)

    # Populate dictionary for manuscripts
    data_dict_manuscript['qid'] = itidata_id
    data_dict_manuscript['P1'] = "Q15"
    data_dict_manuscript['Lhu'] = lhu_value
    data_dict_manuscript['Len'] = lhu_value
    data_dict_manuscript['Dhu'] = manuscript_description_hu
    data_dict_manuscript['Den'] = manuscript_description_en
    data_dict_manuscript['P7'] = sender_id
    data_dict_manuscript['P80'] = recipient_id
    data_dict_manuscript['P41'] = "Q26"
    data_dict_manuscript['P85'] = place_name_manuscript
    data_dict_manuscript['P203'] = ";".join(institution_id)
    data_dict_manuscript['P204'] = record_id
    data_dict_manuscript['P2018'] = exact_date if exact_date != "" else from_date + "--" + to_date

    write_to_csv(data_dict_manuscript, 'xml_header_tsv_manuscript.tsv')


def get_text_with_supplied(soup, tag_name, children):
    """
    Gets the text value for the given tag, and adds '[' and ']' if it is under the 'supplied' tag.
    If the supplied text is a child, '[' and ']' are added
    """
    tag = soup.find(tag_name)
    if tag:
        tag_to_delete = ["orig", "del"]
        for del_tag in tag.find_all(element for element in tag_to_delete):
            del_tag.decompose()
        for add_tag in tag.find_all("add"):
            # print(add_tag.string, add_tag.parent.name, path)
            add_tag.unwrap()
        for supplied_tag in tag.find_all('supplied'):
            supplied_tag.string = "[" + supplied_tag.text + "]"
            supplied_tag.unwrap()
        tag_text_no_child = [text for text in tag.stripped_strings]
        tag_text_with_child = tag.text
        if tag.parent.name == 'supplied' or tag.parent.parent.name == 'supplied':
            return f"[{tag_text_with_child.strip()}]" if children else f"[{tag_text_no_child[0].strip()}]"
        else:
            return tag_text_with_child.strip() if children else tag_text_no_child[0].strip()
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
