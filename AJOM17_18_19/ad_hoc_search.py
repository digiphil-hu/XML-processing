from xml_methods import get_filenames

# folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
#                "/home/eltedh/GitHub/migration-ajom-18",
#                "/home/eltedh/GitHub/migration-ajom-19"]

folder_list = ["/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_GEO/XML"]

for parsed, path in get_filenames(folder_list):
    for idno in parsed.teiHeader.find_all("idno", {"type": "KOHA_GEO"}):
        if idno.parent.parent.name != "p":
            print(idno, idno.parent.name, idno.parent.parent.name, path)