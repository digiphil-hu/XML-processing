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
                        idno_tag["type"] = "ITIdata"
                        placename.append(idno_tag)
    for note_tag in parsed.teiHeader.find_all('note'):
        note_tag.decompose()
    for koha_geo_idno in parsed.teiHeader.find_all("idno", {"type": "KOHA_GEO"}):
        if koha_geo_idno.string:
            print(path, koha_geo_idno.string)
        else:
            if koha_geo_idno.get("corresp"):
                koha_corresp = normalize_whitespaces(koha_geo_idno["corresp"])
                if koha_corresp in AJOM_geo_dict:
                    koha_geo_idno.string = AJOM_geo_dict[koha_corresp][1]
                    koha_geo_idno["type"] = "ITIdata"
                    if AJOM_geo_dict[koha_corresp][0].strip() != "":
                        koha_geo_idno["corresp"] = AJOM_geo_dict[koha_corresp][0]
                else:
                    print(path, koha_geo_idno)
            else:
                placename = koha_geo_idno.parent
                if placename.name != "placeName":
                    print(placename)
                if placename.parent.name != "p" and placename.parent.name != "supplied":
                    placename_string = normalize_whitespaces(placename.text)
                    if placename_string in AJOM_geo_dict:
                        koha_geo_idno.string = AJOM_geo_dict[placename_string][1]
                        koha_geo_idno["type"] = "ITIdata"
                    else:
                        print(placename_string, placename.parent.name, placename.parent.parent.name, placename.parent.parent.parent.name, path)
    for koha_geo_idno in parsed.body.head.find_all("idno", {"type": "KOHA_GEO"}):
        if koha_geo_idno.string:
            print("Error: idno has string", path, koha_geo_idno.string)
        else:
            if koha_geo_idno.get("corresp"):
                koha_corresp = normalize_whitespaces(koha_geo_idno["corresp"])
                if koha_corresp in AJOM_geo_dict:
                    koha_geo_idno.string = AJOM_geo_dict[koha_corresp][1]
                    koha_geo_idno["type"] = "ITIdata"
                    if AJOM_geo_dict[koha_corresp][0].strip() != "":
                        koha_geo_idno["corresp"] = AJOM_geo_dict[koha_corresp][0]
                else:
                    print("Error: placename not in change list. ", path, koha_geo_idno["corresp"])

    # Now let's find the placenames in head where there is no idno, or it is empty:
    for head_place_name in parsed.body.head.find_all("placeName"):
        # If idno exists, but it is empty, let's delete it.
        if head_place_name.find("idno"):
            if head_place_name.idno.get("corresp") is None and head_place_name.idno.string is None:
                head_place_name.idno.decompose()
        if head_place_name.find("idno") is None:
            placename_string = normalize_whitespaces(head_place_name.string)
            if placename_string in AJOM_geo_dict:
                idno_tag = parsed.new_tag("idno")
                idno_tag.string = AJOM_geo_dict[placename_string][1]
                idno_tag["type"] = "ITIdata"
                if AJOM_geo_dict[placename_string][0] != "":
                    idno_tag["corresp"] = AJOM_geo_dict[placename_string][0]
                head_place_name.append(idno_tag)
                # print(head_place_name)
            else:
                print(head_place_name.string)

    with open(new_path + path.split("/")[-1], "w", encoding="utf-8") as f:
         f.write(str(parsed))
