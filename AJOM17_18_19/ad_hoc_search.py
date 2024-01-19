from xml_methods import get_filenames, normalize_whitespaces

folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]

# folder_list = ["/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_GEO/XML"]

for parsed, path in get_filenames(folder_list):
    if parsed.body.head.find("placeName") is None:
        for placename in parsed.teiHeader.creation.find_all("placeName"):
            if placename.string:
                print(normalize_whitespaces(str(placename.parent)))
        try:
            for placename in parsed.correspDesc.find_all("placeName"):
                if placename.string:
                    print(normalize_whitespaces(str(placename.parent)))
        except AttributeError:
            pass
        print(path)
