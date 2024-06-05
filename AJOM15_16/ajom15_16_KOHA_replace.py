from xml_methods import get_filenames, prettify_soup, normalize

folder_list = ["/home/pg/Documents/GitHub/Arany_15/tei xml", "/home/pg/Documents/GitHub/Arany_16/tei xml"]

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

place_names = set()
for parsed, path in get_filenames(folder_list):
    if "adat" not in path:
        for place_name in parsed.teiHeader.creation.find_all("placeName"):
            if place_name.text != "":
                place_names.add(normalize(place_name.text.strip()))
        for corr_act in parsed.teiHeader.correspDesc.find_all("correspAction"):
            if corr_act.get("type") == "sent" or corr_act.get("type") == "recieved":
                for place_name in corr_act.find_all("placeName"):
                    place_names.add(normalize(place_name.text.strip()))
            else:
                for place_name in corr_act.find_all("placeName"):
                    print("Adress: ", prettify_soup(place_name.text.strip()), place_name.find("idno").get("corresp"))

# for place_name in place_names:
#     print(place_name)

# print(path.split("/")[-1], prettify_soup(place_name.parent), place_name.text)