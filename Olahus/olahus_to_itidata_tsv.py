import xml_methods as xm
import re

# List of folders whete the TEI XML's are found
folder_list = ["/home/eltedh/GitHub/Olahus/Olahus 1"
                # , "/home/eltedh/GitHub/Olahus/Olahus 2"
               ]

# Create empty csv file
with open("Olahus_letters_itidata.csv", "w", encoding="utf-8") as f:
    pass

# Create dictionary for the ITIdata statements
itidata_dict = dict()

# Parse every XML
for parsed, path in xm.get_filenames(folder_list):
    file_name = path.split("/")[-1]
    header = parsed.teiHeader

    # Get labels
    label = xm.normalize(header.title.string)
    # print(file_name, label)

    # Description
    sender_name = "Unknown"
    sender_act = header.find("correspAction", {"type": "sent"})
    if sender_act is not None:
        sender_name = sender_act.find("persName").string
        if sender_name is None or sender_name.strip() == "":
            sender_name = sender_act.find("orgName").string
    desc_eng = xm.normalize(sender_name) + ", " + "letter, " + "Epistulae. Pars I. 1523–1533, 2018"
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

    # Populate dictionary
    itidata_dict['Lhu'] = label
    itidata_dict['Len'] = label
    itidata_dict['Dhu'] = desc_hun
    itidata_dict['Den'] = desc_eng
    itidata_dict['P1'] = "P26"  # Instance of : letter
    itidata_dict['P41'] = "P26"  # Genre: letter
    itidata_dict['P44'] = "Q469927"  # Epistulae. Pars I. 1523–1533
    itidata_dict['P57'] = "+2018-00-00T00:00:00Z/9"
    itidata_dict['P49'] = page_num
    itidata_dict['P106'] = series_num

    # Write dictionary to a row of csv
    xm.write_to_csv(itidata_dict, "Olahus_letters_itidata.csv")
