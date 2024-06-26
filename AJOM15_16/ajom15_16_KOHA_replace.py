import csv
from xml_methods import get_filenames, prettify_soup, normalize, delete_empty_tags
from bs4 import BeautifulSoup

folder_list = ["/home/pg/Documents/GitHub/migration-ajom-15", "/home/pg/Documents/GitHub/migration-ajom-16"]

# koha_persname = set()
# for parsed, path in get_filenames(folder_list):
#     for person in parsed.find_all("persName"):
#         if person.find("idno") is not None:
#             if person.idno.get("type") is not None:
#                 if "KOHA" in person.idno["type"]:
#                     koha_persname.add(prettify_soup(person.idno))
#
# for person in koha_persname:
#     print(person)

# institution_list = set()
# for parsed, path in get_filenames(folder_list):
#     for institution_name in parsed.find_all("institution"):
#         if institution_name.string:
#             institution_list.add(institution_name.string)
# for item in institution_list:
#     print(item)

# for parsed, path in get_filenames(folder_list):
#     for action in parsed.find_all("correspAction"):
#         if action.get("type") == "sent":
#             if action.persName is None:
#                 print("Missing sent person name", prettify_soup(action))
#             elif "KOHA" not in action.persName.text:
#                 print(path.split("/")[-1], "\t"," Sender: ", "\t", action.persName.text.strip())
#         if action.get("type") == "recieved":
#             if action.persName is None:
#                 print("Missing received person name", prettify_soup(action))
#             elif "KOHA" not in action.persName.text:
#                 print(path.split("/")[-1], "\t", "Receiver: ", "\t", action.persName.text.strip())

# place_names = set()
# for parsed, path in get_filenames(folder_list):
#     if "adat" not in path:
#         for place_name in parsed.teiHeader.creation.find_all("placeName"):
#             if place_name.text != "":
#                place_name_text = normalize(place_name.text.split("Q")[0])
#                place_names.add(place_name_text)
#         for corr_act in parsed.teiHeader.correspDesc.find_all("correspAction"):
#             if corr_act.get("type") == "sent" or corr_act.get("type") == "received":
#                 for place_name in corr_act.find_all("placeName"):
#                     place_name_text = normalize(place_name.text.split("Q")[0])
#                     place_names.add(place_name_text)
#             else:
#                 if corr_act.get("type") != "address":
#                     print("Corresp Action ERROR: ", path)
#                 else:
#                     for place_name in corr_act.find_all("placeName"):
#                         if place_name.find("idno"):
#                             if place_name.idno.get("corresp"):
#                                 place_names.add(place_name.idno.get("corresp").strip())
#                                 print("Address corresp: ", place_name.idno.get("corresp").strip())
#
# for place_name in place_names:
#     print(place_name)

# print(path.split("/")[-1], prettify_soup(place_name.parent), place_name.text)

# Open place names from CSV and parse it as dictionary
geo_dict = {}
with open("./Ajom15-16_place_names.csv", "r", encoding="utf-8" ) as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        geo_dict[row[0].strip()] = row[1].strip()

for parsed, path in get_filenames(folder_list):
    if "adat" not in path:

        # Delete empty placeName, persName, idno
        parsed = delete_empty_tags(parsed=parsed, tag_list=["persName", "placeName", "idno"])

        # Delete KOHA_GEO
        for idno_tag in parsed.find_all("idno"):
            if idno_tag.get("type") == "KOHA_GEO":
                if idno_tag.text.strip() != "":
                    print(path, idno_tag)

            # Check if idno text is numeric.
            if idno_tag.text.strip() != "":
                if idno_tag.get("type"):
                    if idno_tag.get("type") != "PID" and idno_tag.get("type") != "URL":
                        idno_text = idno_tag.text.strip()
                        if ":" in idno_text:
                            idno_text = idno_text.split(":")[1]
                        if idno_text.startswith("Q"):
                            idno_text = idno_text.replace("Q", "")
                        if idno_text.isdigit():
                            print(idno_tag)

        # Add identifier to placeNames in creation
        for place_name in parsed.teiHeader.creation.find_all("placeName"):

            # If idno already exists check if identifier is correct
            if place_name.find("idno"):
                if place_name.text.strip() == "":
                    print("ERROR in <creation><placeName>: ", path, place_name)
                else:
                    if geo_dict[place_name.text.split("Q")[0]] != place_name.idno.text.strip():
                        print("ERROR in <creation><placeName>: ", path, place_name)

            # Create idno and add identifier
            else:
                idno_tag = parsed.new_tag(name="idno")
                idno_tag["type"] = "ITIdata"
                idno_tag.string = geo_dict[place_name.text.strip()]
                place_name.insert(1, idno_tag)

        # placeName-s in correspDesc
        for corr_act in parsed.teiHeader.correspDesc.find_all("correspAction"):
            for place_name in corr_act.find_all("placeName"):
