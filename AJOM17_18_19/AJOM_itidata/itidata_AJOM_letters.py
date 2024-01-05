import csv
import re
from get_geo_namespace_id_itidata import get_eng_hun_item_labels_from_itidata
from xml_methods import compare_text_normalize, normalize
import difflib


# Get the list of letters present in itidata
with (open("itidata_ajom17_sparql_export.tsv", "r", encoding="utf-8") as itidata_query_file):
    itidata_reader = csv.reader(itidata_query_file, delimiter="\t")
    letter_id_dict = dict()
    for row in itidata_reader:
        letter_id_dict[row[0].split("/")[-1]] = row[4].strip(".")
    if len(list(letter_id_dict.values())) != len(set(list(letter_id_dict.values()))):
        print("DUPLUM!")

# Single out letters present in itidata
with open("/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/output.tsv", "r", encoding="utf-8") as xml_tsv_file:
    with open("shortened_xml.tsv", "w", encoding="utf-8") as shortened_xml_tsv_file:
        shortened_xml_writer = csv.writer(shortened_xml_tsv_file, delimiter="\t")
        xml_tsv_reader = csv.reader(xml_tsv_file, delimiter="\t")
        for row in xml_tsv_reader:
            if row[11] in list(letter_id_dict.values()):
                itidata_id_list = [key for key, value in letter_id_dict.items() if value == row[11]]
                if len(itidata_id_list) == 1:
                    row.insert(0, itidata_id_list[0])
                    shortened_xml_writer.writerow(row)
                else:
                    print("DUPLUM: ", itidata_id_list, row[11])

# Compare itidata items sparql export and xml based tsv
with open("shortened_xml.tsv", "r", encoding="utf-8") as shortened_xml_tsv_file:
    with open("AJOM17_error_list.tsv", "w", encoding="utf-8") as AJOM17_error_list_file:
        shortened_xml_reader = csv.reader(shortened_xml_tsv_file, delimiter="\t")
        AJOM17_error_list_file_writer = csv.writer(AJOM17_error_list_file, delimiter="\t")
        for row in shortened_xml_reader:
            error_row = []
            itidata_id = row[0]
            error_row.insert(0, itidata_id)
            itidata_json = get_eng_hun_item_labels_from_itidata(itidata_id, "json")

            # Check if itidata Hungarian and English lables are identical:
            if itidata_json["entities"][itidata_id]["labels"]["hu"]["value"] != itidata_json["entities"][itidata_id]["labels"]["en"]["value"]:
                error_row.append("ITIDATA LABEL @hu != @en")

            # Check if xml tsv lable and itidata lable are identical
            if compare_text_normalize(itidata_json["entities"][itidata_id]["labels"]["hu"]["value"]
                                      ) != compare_text_normalize(row[2]):
                error_row.append(f'CHECK LABEL: "{row[2]}"')

            # Check if xml tsv description and itidata description are identical for English and Hungarian
            if compare_text_normalize(itidata_json["entities"][itidata_id]["descriptions"]["hu"]["value"]
                                      ) != compare_text_normalize(row[4]):
                error_row.append(f'CHECK DESCRIPTION @hu: "{row[4]}"')
            if compare_text_normalize(itidata_json["entities"][itidata_id]["descriptions"]["en"]["value"]
                                      ) != compare_text_normalize(row[5]):
                error_row.append(f'CHECK DESCRIPTION @en: "{row[5]}"')

            # Check Property - Value pairs:
            property_value_pairs = [("P1", 6),
                                    # ("P7", 7),
                                    # ("P80", 8),
                                    ("P41", 9),
                                    ("P44", 10),
                                    ]

            for pair in property_value_pairs:
                # print(pair[0], row[pair[1]])
                try:
                    if itidata_json["entities"][itidata_id]["claims"][pair[0]][0]["mainsnak"]["datavalue"]["value"]["id"] != row[pair[1]]:
                        error_row.append(f'CHECK {pair[0]}: {row[pair[1]]}')
                except KeyError:
                    error_row.append(f'CHECK {pair[0]}: {row[pair[1]]}')

            # Check page numbers
            try:
                page_number = itidata_json["entities"][itidata_id]["claims"]["P49"][0]["mainsnak"]["datavalue"]["value"]
                pattern = r'^\d+([-–]\d+)?\.$'
                if not bool(re.match(pattern, page_number)):
                    error_row.append("CHECK PAGE NUMBER (P49) SYNTAX.")
                    print(page_number)
            except KeyError:
                error_row.append("CHECK MISSING PAGE NUMBER (P49).")

            # Check letter numbers
            if itidata_json["entities"][itidata_id]["claims"]["P106"][0]["mainsnak"]["datavalue"]["value"].strip(".") != row[12]:
                error_row.append(f'CHECK "SERIES ORDINAL" (P106): "{row[12]}"')
                print(row[12])

            # Check annotation
            pattern = r'^Kritikai jegyzetek:\s+\d+([-–]\d+)?\.$'
            annotation = itidata_json["entities"][itidata_id]["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"]["text"]
            annotation_language = itidata_json["entities"][itidata_id]["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"]["language"]
            if (not bool(re.match(pattern, annotation))) or annotation_language != "hu":
                error_row.append(f'CHECK "ANNOTATION" (P18) "{annotation}" @{annotation_language}')

            # Check related item
            related_item_id = itidata_json["entities"][itidata_id]["claims"]["P129"][0]["mainsnak"]["datavalue"]["value"]["id"]
            related_item_label = get_eng_hun_item_labels_from_itidata(related_item_id, "")[0]
            # label_hu = itidata_json["entities"][itidata_id]["labels"]["hu"]["value"]
            label_hu = get_eng_hun_item_labels_from_itidata(itidata_id, "")[0]

            if normalize(related_item_label) != normalize(label_hu):
                error_row.append(f'CHECK "RELATED TO" (P129) LABEL MISMACH "{related_item_label}"')
                differ = difflib.Differ()
                diff = list(differ.compare(label_hu, related_item_label))
                highlighted_diff = []
                for item in diff:
                    if item.startswith('- '):
                        highlighted_diff.append(f'\033[91m{item[2:]}\033[0m')  # Red color for deletions
                    elif item.startswith('+ '):
                        highlighted_diff.append(f'\033[92m{item[2:]}\033[0m')  # Green color for additions
                    else:
                        highlighted_diff.append(item)
                print(''.join(highlighted_diff))

            # print(error_row)
            AJOM17_error_list_file_writer.writerow(error_row)





