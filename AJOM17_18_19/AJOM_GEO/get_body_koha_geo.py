from AJOM17_18_19.AJOM_GEO.get_header_koha_geo import get_koha_geo
from xml_methods import get_filenames

folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]

counter = 0
header_corresp_set = set()
koha_head_geo_set = set()
for parsed, path in get_filenames(folder_list):
    for koha_geo in parsed.teiHeader.find_all("idno", {"type": "KOHA_GEO"}):
        if koha_geo.string:
            print(koha_geo.string)
        corresp = koha_geo.get("corresp")
        if corresp:
            header_corresp_set.add(koha_geo["corresp"])
            counter += 1
    for element in get_koha_geo(parsed, ""):
        koha_head_geo_set.add(element)
print("Count:", counter)
print(len(header_corresp_set))
print(len(koha_head_geo_set))
missing_elements = header_corresp_set.difference(koha_head_geo_set)
for element in missing_elements:
    print(element)
