import csv

import get_geo_namespace_id_itidata
from xml_methods import get_filenames, normalize_whitespaces
from collections import defaultdict

# List of folders whete the TEI XML's are found
folder_list = ["/home/eltedh/GitHub/Olahus/Olahus 1", "/home/eltedh/GitHub/Olahus/Olahus 2"]

# List of strings to delete form names:
replace_string_list = ["(?)", "[?]", "[", "]"]

# Default dict to store person names and their occurrences
person_name_dict = defaultdict(int)

# Populate dictionary with itidata id's
itidata_names_dict = defaultdict(set)
with open("olah-persnames_itidata.csv", "r", encoding="utf8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        itidata_names_dict[row[2]].add(row[0])
        if row[1] != "":
            itidata_names_dict[row[2]].add(row[1])
# print(itidata_names_dict)

# Parse every XML
for parsed, path in get_filenames(folder_list):
    # Count occurrences of each person name and update the dictionary
    for name in parsed.teiHeader.profileDesc.find_all('persName'):
        normalized_name = name.string
        [normalized_name := normalized_name.replace(string, "") for string in replace_string_list]
        normalized_name = normalize_whitespaces(normalized_name).lstrip().rstrip()
        person_name_dict[normalized_name] += 1

# Sort the dictionary by the number of occurrences in descending order or alphabetically
sorted_person_name_dict = dict(sorted(person_name_dict.items(), key=lambda item: item[0].lower(), reverse=False))

for xml_name, occurence in sorted_person_name_dict.items():
    name_id_to_enrich = "Unknown"
    itidata_name = "None"
    for itidata_id, name_set in itidata_names_dict.items():
        if xml_name in name_set:
            name_id_to_enrich = itidata_id
            itidata_name = get_geo_namespace_id_itidata.get_eng_hun_item_labels_from_itidata(itidata_id, what_do_yo_need="")
    print(xml_name, "\t", occurence, "\t", name_id_to_enrich, "\t", itidata_name)