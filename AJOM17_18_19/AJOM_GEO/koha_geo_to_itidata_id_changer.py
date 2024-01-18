import csv
import bs4

from xml_methods import get_filenames, normalize_whitespaces, get_parent_tags, prettify_soup

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

    # Let's delete empty idno's
    for idno in parsed.find_all("idno", {"type": "KOHA_GEO"}):
        del idno["type"]
        if idno.string:
            print(idno.string)
        if (idno.string is None or idno.string.strip() == "") and idno.get("corresp") is None:
            idno.decompose()
        else:
            parent_tag_set = set(get_parent_tags(idno))
            if "body" not in parent_tag_set:
                if not idno["corresp"] in AJOM_geo_dict:
                    print(idno)

    # Header placename idno corresp to itidata
    for placename in parsed.teiHeader.find_all("placeName"):
        parent_tag_set = set(get_parent_tags(placename))
        if placename.find("idno"):
            if placename.idno.get("corresp"):
                if normalize_whitespaces(placename.idno["corresp"]) not in AJOM_geo_dict:
                    print(placename.idno["corresp"])
                else:
                    placename.idno.string = AJOM_geo_dict[normalize_whitespaces(placename.idno["corresp"])][1]
                    placename.idno["type"] = "ITIdata"
        else:
            # Header persNames without idno to ITIdata
            placename_text = normalize_whitespaces(placename.text).replace("?", "").strip()
            if "p" not in parent_tag_set and "note" not in parent_tag_set:
                if placename_text not in AJOM_geo_dict:
                    print(path, placename.parent.name, placename)
                else:
                    idno_tag = parsed.new_tag('idno')
                    if AJOM_geo_dict[placename_text][0].strip() != "":
                        idno_tag["corresp"] = AJOM_geo_dict[placename_text][0]
                    idno_tag.string = AJOM_geo_dict[placename_text][1]
                    idno_tag["type"] = "ITIdata"
                    placename.append(idno_tag)

    # Body//head to ITIdata
    for placename in parsed.body.head.find_all("placeName"):
        placename_text = normalize_whitespaces(placename.text)
        # If there is an idno corresp value:
        if placename.find("idno"):
            if placename.idno.get("corresp"):
                placename_text = normalize_whitespaces(placename.idno["corresp"])
                if placename_text not in AJOM_geo_dict:
                    print("Corresp", placename_text)
                else:
                    placename.idno["type"] = "ITIdata"
                    placename.idno.string = AJOM_geo_dict[placename_text][1]
                    # print(placename)
            # If there is idno but no corresp
            else:
                if placename_text not in AJOM_geo_dict:
                    print(placename_text)
                else:
                    placename.idno.string = AJOM_geo_dict[placename_text][1]
        # If no idno
        else:
            idno_tag = parsed.new_tag('idno')
            if AJOM_geo_dict[placename_text][0] != "":
                idno_tag["corresp"] = AJOM_geo_dict[placename_text][0]
            else:
                idno_tag["corresp"] = placename_text
            idno_tag.string = AJOM_geo_dict[placename_text][1]
            idno_tag["type"] = "ITIdata"
            placename.append(idno_tag)

    with open(new_path + path.split("/")[-1], "w", encoding="utf-8") as f:
        f.write(prettify_soup(parsed))

