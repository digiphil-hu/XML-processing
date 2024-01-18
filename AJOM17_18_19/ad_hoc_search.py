from xml_methods import get_filenames

# folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
#                "/home/eltedh/GitHub/migration-ajom-18",
#                "/home/eltedh/GitHub/migration-ajom-19"]

folder_list = ["/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_GEO/XML"]

placename_header_note = set()
for parsed, path in get_filenames(folder_list):
    for place in parsed.teiHeader.find_all("placeName"):
        if place.find("idno"):
            if place.idno.get("corresp"):
                placename_header_note.add(place.idno["corresp"])
print(placename_header_note)
