import csv

from get_geo_namespace_id_itidata import get_eng_hun_item_labels_from_itidata
from xml_methods import compare_text_normalize

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

            # Check if Hungarian and English lables are identical:
            if itidata_json["entities"][itidata_id]["labels"]["hu"]["value"] != itidata_json["entities"][itidata_id]["labels"]["en"]["value"]:
                error_row.append("ITIDATA LABEL @hu != @en")

            # Check if xml tsv lable and itidata lable are identical
            if compare_text_normalize(itidata_json["entities"][itidata_id]["labels"]["hu"]["value"]
                                      ) != compare_text_normalize(row[2]):
                error_row.append("CHECK LABEL:" + row[2])

            # Check if xml tsv description and itidata description are identical for English and Hungarian
            if compare_text_normalize(itidata_json["entities"][itidata_id]["descriptions"]["hu"]["value"]
                                      ) != compare_text_normalize(row[4]):
                error_row.append("CHECK DESCRIPTION @hu:" + row[4])
            if compare_text_normalize(itidata_json["entities"][itidata_id]["descriptions"]["en"]["value"]
                                      ) != compare_text_normalize(row[5]):
                error_row.append("CHECK DESCRIPTION @en:" + row[5])

            # Check Property - Value pairs:
            property_value_pairs = [("P1", 6),
                                    # ("P7", 7),
                                    # ("P80", 8),
                                    ("P41", 9),
                                    ("P44", 10)
                                    ]

            for pair in property_value_pairs:
                # print(pair[0], row[pair[1]])
                try:
                    if itidata_json["entities"][itidata_id]["claims"][pair[0]][0]["mainsnak"]["datavalue"]["value"]["id"] != row[pair[1]]:
                        error_row.append(f"CHECK {pair[0]}: " + row[pair[1]])
                except KeyError:
                    error_row.append(f"CHECK {pair[0]}: " + row[pair[1]])

            # Check page numbers
            try:
                page_number = itidata_json["entities"][itidata_id]["claims"]["P49"][0]["mainsnak"]["datavalue"]["value"]
                if not page_number.endswith(".") or page_number.replace(".", "").replace("-", "").isnumeric():
                    error_row.append("CHECK PAGE NUMBER (P49) SYNTAX.")
            except KeyError:
                error_row.append("CHECK MISSING PAGE NUMBER (P49).")



            AJOM17_error_list_file_writer.writerow(error_row)





