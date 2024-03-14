import csv
import get_geo_namespace_id_itidata
from xml_methods import get_filenames, normalize_whitespaces, process_dictionary, prettify_soup
from collections import defaultdict

# List of folders whete the TEI XML's are found
folder_list = ["/home/eltedh/GitHub/Olahus/Olahus 1", "/home/eltedh/GitHub/Olahus/Olahus 2"]

# List of strings to delete form names:
replace_string_list = ["(?)", "[?]", "[", "]"]

# Default dict to store person names and their occurrences
person_name_dict = defaultdict(int)

# Populate dictionary with itidata id's
itidata_names_dict = defaultdict(set)
with open("olah-persnames_3.csv", "r", encoding="utf8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if row[2].strip().replace("Q", "").replace(" ", "").isnumeric():
            itidata_id = row[2].strip().replace(" ", "")
            itidata_names_dict[itidata_id].add(row[0].strip())
        # if row[1].strip() != "":
        #     itidata_names_dict[row[2].strip()].add(row[1].stip())
print(itidata_names_dict)

# Parse every XML
for parsed, path in get_filenames(folder_list):
    # Count occurrences of each person name and update the dictionary
    for name_tag in parsed.teiHeader.profileDesc.find_all('persName'):
        normalized_name = name_tag.string
        [normalized_name := normalized_name.replace(string, "") for string in replace_string_list]
        normalized_name = normalize_whitespaces(normalized_name).lstrip().rstrip()
        person_name_dict[normalized_name] += 1
        for key, value in itidata_names_dict.items():
            if normalized_name in value:
                # Create a new 'idno' tag with the attribute 'ITIdata'
                idno_tag = parsed.new_tag('idno', type='ITIdata')
                idno_tag.string = key
                name_tag.append(idno_tag)
    # Write XML's with names enriched
    path_out = "/home/eltedh/PycharmProjects/XML-processing/Olahus/Olahus_name_id/"
    file_name = path.split("/")[-1]
    with open(path, "w", encoding="utf8") as f:
        f.write(prettify_soup(parsed))


# # Sort the dictionary by the number of occurrences in descending order or alphabetically
# sorted_person_name_dict = dict(sorted(person_name_dict.items(), key=lambda item: item[0].lower(), reverse=False))
#
# for xml_name, occurence in sorted_person_name_dict.items():
#     name_id_to_enrich = "Unknown"
#     itidata_name = "None"
#     itidata_property_values = ""
#     for itidata_id, name_set in itidata_names_dict.items():
#         if xml_name in name_set:
#             name_id_to_enrich = itidata_id
#             itidata_property_values = process_dictionary(
#                 get_geo_namespace_id_itidata.get_eng_hun_item_labels_from_itidata(itidata_id, what_do_yo_need="json"))
#             itidata_name = get_geo_namespace_id_itidata.get_eng_hun_item_labels_from_itidata(
#                         itidata_id, what_do_yo_need="labels")
#
#     print(xml_name, "\t", occurence, "\t", name_id_to_enrich, "\t", itidata_name, "\t", itidata_property_values)