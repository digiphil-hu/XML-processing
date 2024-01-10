import csv

import bs4

from xml_methods import get_filenames, normalize_whitespaces

folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]

AJOM_geo_dict = {}
with open("ajom_header_geonames_itidata.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter="\t")
    # header = next(reader)
    for row in reader:
        AJOM_geo_dict[row[0]] = (row[1], row[2])

for parsed, path in get_filenames(folder_list):
    new_path = "/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_GEO/XML/"
    tag_list = ["creation", "correspDesc"]
    for tag in tag_list:
        for parent_tag in parsed.teiHeader.find_all(tag):
            for placename in parent_tag.find_all('placeName'):
                if placename.string:
                    placename_string = normalize_whitespaces(placename.string)
                    placename_string = placename_string.replace("?", "").strip()
                    if placename_string not in AJOM_geo_dict:
                        print(placename_string)
                    if placename.find('idno'):
                        print(path, placename_string)
                    else:
                        idno_tag = parsed.new_tag('idno')
                        if AJOM_geo_dict[placename_string][0].strip() != "":
                            idno_tag["corresp"] = AJOM_geo_dict[placename_string][0]
                        idno_tag.string = AJOM_geo_dict[placename_string][1]
                        placename.append(idno_tag)
    with open(new_path + path.split("/")[-1], "w", encoding="utf-8") as f:
        f.write(str(parsed))
