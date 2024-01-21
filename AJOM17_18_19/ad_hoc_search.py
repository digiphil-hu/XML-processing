from xml_methods import get_filenames, normalize_whitespaces, prettify_soup

folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]

# folder_list = ["/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_GEO/XML"]

for parsed, path in get_filenames(folder_list):
    if parsed.head.find("placeName") and parsed.creation.find("placeName"):
        if parsed.head.find("placeName").idno.text.strip() != parsed.creation.find("placeName").idno.text.strip():
            # no_child_text = [text for text in parsed.creation.placeName.stripped_strings]
            print(no_child_text)