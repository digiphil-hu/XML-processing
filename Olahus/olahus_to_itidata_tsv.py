from collections import defaultdict
import csv
import xml_methods as xm
import re

# List of folders whete the TEI XML's are found
folder_list = ["/home/eltedh/GitHub/Olahus/Olahus 1"
                , "/home/eltedh/GitHub/Olahus/Olahus 2"
               ]

# Create empty csv file
with open("Olahus_letters_itidata_1.csv", "w", encoding="utf-8") as f:
    pass
with open("Olahus_letters_itidata_2.csv", "w", encoding="utf-8") as f:
    pass

# List of strings to delete from names
replace_string_list = ["(?)", "[?]", "[", "]"]

# # Parse every XML and populate dict for lettet-to-letter references
# related_item_ref_dict = defaultdict(set)
# pid_error_list = []
# for parsed, path in xm.get_filenames(folder_list):
#     for ref_urls in [related_item.find_all("ref") for related_item in parsed.find_all("relatedItem")]:
#         for ref_url in ref_urls:
#             ref_target = xm.normalize(ref_url.get("target").replace("http:/digiphil.hu/o:olahus.tei.", ""))
#             if ref_target != "":
#                 related_item_ref_dict[path.split("/")[-1]].add(ref_target)
#     for ref_tag in parsed.find_all("ref"):
#         if ref_tag.string is not None:
#             ref_match = re.search(r"15\d+_\d(sz)?$", ref_tag.string)
#             if ref_match:
#                 ref_target = ref_match.group()
#                 related_item_ref_dict[path.split("/")[-1]].add(ref_target)

# Populate dictionary with itidata id's and Unknown, Unidetified names
itidata_names_dict = defaultdict(set)
with open("olah-persnames_3.csv", "r", encoding="utf8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if row[2].strip().replace("Q", "").replace(" ", "").isnumeric():
            itidata_id = row[2].strip().replace(" ", "")
            itidata_names_dict[itidata_id].add(row[0].strip())
        elif row[2].strip() == "Unknown" or row[2].strip() == "Unidentified":
            itidata_names_dict[row[2].strip()].add(row[0].strip())
        else:
            print("NAME CSV ERROR: ", row)
print(itidata_names_dict)

# Parse every XML
# Create dictionary for the ITIdata statements
for parsed, path in xm.get_filenames([folder_list[0]]):
    itidata_dict = dict()
    file_name = path.split("/")[-1]
    header = parsed.teiHeader

    # Get labels
    if header.find("title", {"type": "main"}):
        label = xm.normalize(header.find("title", {"type": "main"}).string)
    else:
        label = xm.normalize(header.find("title").string)
    # print(file_name, label)

    # Description
    sender_name = ""
    name_itidata_id = None
    sender_act = header.find("correspAction", {"type": "sent"})
    person = sender_act.find_all("persName")
    if len(person) > 1:
        print(file_name, person)

    if sender_act is not None and sender_act.find("persName") is not None:
        if sender_act.find("idno"):
            name_itidata_id = sender_act.find("idno").string
            sender_act.idno.decompose()
        sender_name = sender_act.find("persName").string
        # print(sender_name)
    else:
        sender_name = sender_act.find("orgName").string
        print(sender_name)
    if sender_name is None or sender_name.strip() == "":
        sender_name = 'Unknown'
        print("ERROR: NO SENDER!", file_name)
    sender_name = xm.normalize(sender_name)
    sender_name_namespaced = sender_name
    [sender_name_namespaced := sender_name_namespaced.replace(string, "") for string in replace_string_list]

    desc_eng = sender_name + ", " + "letter, " + "Epistulae. Pars I. 1523–1533, 2018"
    desc_hun = desc_eng.replace("letter", "levél")
    # print(desc_eng)

    # Page and series ordinal
    page_num = ""
    pattern = r'^\d+([–]\d+)?\.$'
    series_num = ""
    try:
        page_num = header.find("biblScope", {"unit": "page"}).string.strip()
        page_num = page_num.replace("-", "–")
        if page_num.isdigit():
            page_num += "."
        if not bool(re.match(pattern, page_num)):
            print("MALFORMED PAGE NUMBER! ", file_name, page_num)
        series_num = header.find("biblScope", {"unit": "entry"}).string.strip()
        if not series_num.isdigit():
            print("SERIES NUMBER IS NOT NUMERIC!", file_name)
        # print(page_num, series_num)
    except:
        print("NUM ERROR: ", file_name)

    # PID
    pid = xm.normalize(header.find("idno", {"type": "PID"}).string.strip()[2:])
    if file_name.rstrip('.xml') != pid.replace("olahus.tei.", ""):
        print("PID ERROR: ", file_name, pid)

    # Populate dictionary
    itidata_dict['Lhu'] = label
    itidata_dict['Len'] = label
    itidata_dict['Dhu'] = desc_hun
    itidata_dict['Den'] = desc_eng
    itidata_dict['P1'] = "P26"  # Instance of : letter
    itidata_dict['P41'] = "P26"  # Genre: letter
    if name_itidata_id is not None:
        itidata_dict['P7'] = name_itidata_id
        itidata_dict['P37'] = None
    else:
        if sender_name_namespaced.strip() in itidata_names_dict["Unidentified"]:
            itidata_dict['P7'] = None
            itidata_dict['P37'] = sender_name
        else:
            itidata_dict['P7'] = "P39:" + sender_name
            itidata_dict['P37'] = None
    itidata_dict['P44'] = "Q469927"  # Epistulae. Pars I. 1523–1533
    itidata_dict['P57'] = "+2018-00-00T00:00:00Z/9"
    itidata_dict['P49'] = page_num
    itidata_dict['P106'] = series_num
    itidata_dict['P241'] = "https://doi.org/10.5281/zenodo.10817873"
    itidata_dict['P242'] = "https://hdl.handle.net/20.500.14368/" + pid


    # Write dictionary to a row of csv
    xm.write_to_csv(itidata_dict, "Olahus_letters_itidata_1.csv")


# Parse every XML
# Create dictionary for the ITIdata statements
for parsed, path in xm.get_filenames([folder_list[1]]):
    itidata_dict = dict()
    file_name = path.split("/")[-1]
    header = parsed.teiHeader

    # Get labels
    label = xm.normalize(header.find("title", {"type": "main"}).string)
    # print(file_name, "\n", label)

    # Description
    sender_name = ""
    name_itidata_id = None
    sender_act = header.find("correspAction", {"type": "sent"})
    person = sender_act.find_all("persName")
    if len(person) > 1:
        print(file_name, person)

    if sender_act is not None and sender_act.find("persName") is not None:
        if sender_act.find("idno"):
            name_itidata_id = sender_act.find("idno").string
            sender_act.idno.decompose()
        sender_name = sender_act.find("persName").string
        # print(sender_name)
    else:
        sender_name = sender_act.find("orgName").string
    if sender_name is None or sender_name.strip() == "":
        sender_name = 'Unknown'
        print("ERROR: NO SENDER!", file_name)
    sender_name = xm.normalize(sender_name)
    sender_name_namespaced = sender_name
    [sender_name_namespaced := sender_name_namespaced.replace(string, "") for string in replace_string_list]

    desc_eng = xm.normalize(sender_name) + ", " + "letter, " + "Epistulae. Pars II. 1534–1553, 2022"
    desc_hun = desc_eng.replace("letter", "levél")
    # print(desc_eng)

    # Series ordinal
    series_num = ""
    series_num = header.find("title", {"type": "num"}).string.strip()
    if not series_num.isdigit():
        print("ERROR: SERIES NUMBER IS NOT NUMERIC!", file_name)
        # print(page_num, series_num)

    # PID
    pid = xm.normalize(header.find("idno", {"type": "PID"}).string.strip()[2:])
    if file_name.rstrip('.xml') != pid.replace("olahus.tei.", ""):
        # pid_error_list.append((file_name.rstrip('.xml'), pid.replace("olahus.tei.", "")))
        print("PID ERROR: ", file_name, pid)

    # Populate dictionary
    itidata_dict['Lhu'] = label
    itidata_dict['Len'] = label
    itidata_dict['Dhu'] = desc_hun
    itidata_dict['Den'] = desc_eng
    itidata_dict['P1'] = "P26"  # Instance of : letter
    itidata_dict['P41'] = "P26"  # Genre: letter
    if name_itidata_id is not None:
        itidata_dict['P7'] = name_itidata_id
        itidata_dict['P37'] = None
    else:
        if sender_name_namespaced.strip() in itidata_names_dict["Unidentified"]:
            itidata_dict['P7'] = None
            itidata_dict['P37'] = sender_name
        else:
            itidata_dict['P7'] = "P39:" + sender_name
            itidata_dict['P37'] = None
    itidata_dict['P44'] = "Q469915"  # Epistulae. Pars II. 1534–1553
    itidata_dict['P57'] = "+2022-00-00T00:00:00Z/9"
    itidata_dict['P106'] = series_num
    itidata_dict['P241'] = "https://doi.org/10.5281/zenodo.8011469"
    itidata_dict['P242'] = "https://hdl.handle.net/20.500.14368/" + pid


    # Write dictionary to a row of csv
    xm.write_to_csv(itidata_dict, "Olahus_letters_itidata_2.csv")




# for items in pid_error_list:
#     for key, value in related_item_ref_dict.items():
#         if items[0] in value or items[1] in value:
#             print("PID ERROR WITH REF PROBLEM: ", items, key, value)
#     print("PID ERROR: ", items)

# for key, value in related_item_ref_dict.items():
#     print(key, "\t", value)
