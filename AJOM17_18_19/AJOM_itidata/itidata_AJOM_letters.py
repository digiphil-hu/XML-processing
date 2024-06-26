import csv
import re
from get_geo_namespace_id_itidata import get_eng_hun_item_labels_from_itidata
from xml_methods import compare_text_normalize, normalize, visualize_diff, find_difference_strings, check_list_index
from collections import Counter
import time

# Get the list of letters present in itidata. Column[0] = item url, column[2] = letter id of the critical edition
# SPARQL query: https://tinyurl.com/228w58kt
with (open("itidata_ajom17_18_19_sparql_export.csv", "r", encoding="utf-8") as itidata_query_file):
    itidata_reader = csv.reader(itidata_query_file, delimiter="\t")
    letter_id_dict = dict()
    for row in itidata_reader:
        itidata_id = row[0].split("/")[-1]
        series_ordinal = row[2].strip(".")
        if itidata_id not in letter_id_dict:
            letter_id_dict[itidata_id] = series_ordinal
        else:
            print("DUPLICATE ITIDATA ID IN SPARQL EXPORT!", row)
    if len(list(letter_id_dict.values())) != len(set(list(letter_id_dict.values()))):
        counter = Counter(letter_id_dict.values())
        duplicates = [value for value, count in counter.items() if count > 1]
        if duplicates:
            print("DUPLUM!")
            print("Duplicated values:", duplicates)

# Single out letters present in itidata
with open("/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/xml_header_tsv_letter.tsv", "r",
          encoding="utf-8") as xml_tsv_file:
    with open("shortened_xml_letters.tsv", "w", encoding="utf-8") as shortened_xml_tsv_file:
        with open("shortened_xml_letters_not_in_itidata.tsv", "w", encoding="utf-8") as shortened_inverse_xml_tsv_file:
            shortened_xml_writer = csv.writer(shortened_xml_tsv_file, delimiter="\t")
            shortened_inverse_xml_writer = csv.writer(shortened_inverse_xml_tsv_file, delimiter="\t")
            xml_tsv_reader = csv.reader(xml_tsv_file, delimiter="\t")
            for row in xml_tsv_reader:
                if row[12] in list(letter_id_dict.values()):
                    itidata_id_list = [key for key, value in letter_id_dict.items() if value == row[12]]
                    if len(itidata_id_list) == 1:
                        row.insert(0, itidata_id_list[0])
                        shortened_xml_writer.writerow(row)
                    else:
                        print("DUPLUM: ", itidata_id_list, row[12])
                else:
                    shortened_inverse_xml_writer.writerow(row)

# Compare itidata items sparql export and xml based tsv
with (open("shortened_xml_letters.tsv", "r", encoding="utf-8") as shortened_xml_tsv_file):
    with open("AJOM_error_list_letters.tsv", "w", encoding="utf-8") as AJOM17_error_list_file:
        shortened_xml_reader = csv.reader(shortened_xml_tsv_file, delimiter="\t")
        AJOM17_error_list_file_writer = csv.writer(AJOM17_error_list_file, delimiter="\t")
        for row in shortened_xml_reader:
            index = 0
            error_row_letter = []
            itidata_id = row[0]
            error_row_letter.insert(index, itidata_id)
            itidata_json = get_eng_hun_item_labels_from_itidata(itidata_id, "json")

            # Insert XML filename
            index += 1
            xml_filename = row[2]
            # print(xml_filename)
            error_row_letter.insert(index, xml_filename)

            # Check if itidata Hungarian and English lables are identical:
            index += 1
            try:

                if itidata_json["entities"][itidata_id]["labels"]["hu"]["value"] != \
                        itidata_json["entities"][itidata_id]["labels"]["en"]["value"]:
                    error_row_letter.insert(index, "ITIDATA LABEL @hu != @en")
            except KeyError:
                error_row_letter.insert(index, "ITIDATA LABEL MISSING")
            check_list_index(index, error_row_letter)

            # Check if xml tsv lable and itidata lable are identical
            index += 1
            tsv_xml_lhu = compare_text_normalize(row[3])
            itidata_json_lhu = compare_text_normalize(itidata_json["entities"][itidata_id]["labels"]["hu"]["value"])
            if compare_text_normalize(itidata_json["entities"][itidata_id]["labels"]["hu"]["value"]
                                      ) != compare_text_normalize(row[3]):
                error_row_letter.insert(index, f'CHECK LABEL: {find_difference_strings(itidata_json_lhu, tsv_xml_lhu)}')
                # print(find_difference_strings(itidata_json_lhu, tsv_xml_lhu))
            check_list_index(index, error_row_letter)

            # Check if xml tsv description and itidata description are identical for English and Hungarian
            index += 1
            description_error = []
            try:
                tsv_description_xml_hu = compare_text_normalize(
                    itidata_json["entities"][itidata_id]["descriptions"]["hu"]["value"])
                tsv_descpiptions_xml_en = compare_text_normalize(
                    itidata_json["entities"][itidata_id]["descriptions"]["en"]["value"])
                itidata_json_description_hu = compare_text_normalize(row[5])
                itidata_json_description_en = compare_text_normalize(row[6])
                if tsv_description_xml_hu != itidata_json_description_hu:
                    description_error.append(f'CHECK DESCRIPTION @hu:'
                                            f'{find_difference_strings(tsv_description_xml_hu, itidata_json_description_hu)}')
                if tsv_descpiptions_xml_en != itidata_json_description_en:
                    description_error.append(f'CHECK DESCRIPTION @en: '
                                            f'{find_difference_strings(tsv_descpiptions_xml_en, itidata_json_description_en)}')
            except KeyError:
                description_error.append(f'CHECK DESCRIPTION, MISSING LABEL')
            if len(description_error) > 0:
                error_row_letter.insert(index, "; ".join(description_error))
            check_list_index(index, error_row_letter)

            # Check Property - Value pairs:
            property_value_pairs = [("P1", 7),
                                    ("P7", 8),
                                    ("P80", 9),
                                    ("P41", 10),
                                    ("P44", 11),
                                    ]

            for num, pair in enumerate(property_value_pairs):
                # print(pair[0], row[pair[1]])
                index += 1
                try:
                    if itidata_json["entities"][itidata_id]["claims"][pair[0]][0]["mainsnak"]["datavalue"]["value"]["id"] != row[pair[1]]:
                        error_row_letter.insert(index, f'CHECK {pair[0]}: (ITIdata: {itidata_json["entities"][itidata_id]["claims"][pair[0]][0]["mainsnak"]["datavalue"]["value"]["id"]}, XML: {row[pair[1]]})')
                except KeyError:
                    error_row_letter.insert(index, f'CHECK {pair[0]}: {row[pair[1]]}')

                check_list_index(index, error_row_letter)

            # Check page numbers
            index += 1
            try:
                page_number = itidata_json["entities"][itidata_id]["claims"]["P49"][0]["mainsnak"]["datavalue"]["value"]
                pattern = r'^\d+([-–‒]\d+)?\.$'
                if not bool(re.match(pattern, page_number)):
                    error_row_letter.insert(index, "CHECK PAGE NUMBER (P49) SYNTAX.")
                    print("PAGE NUMBER ERROR", xml_filename, page_number)
            except KeyError:
                error_row_letter.insert(index, "CHECK MISSING PAGE NUMBER (P49).")
            check_list_index(index, error_row_letter)

            # Check letter numbers
            index += 1
            if itidata_json["entities"][itidata_id]["claims"]["P106"][0]["mainsnak"]["datavalue"]["value"].strip(".") != \
                    row[13]:
                error_row_letter.insert(index, f'CHECK "SERIES ORDINAL" (P106): "{row[13]}"')
                print(row[13])
            check_list_index(index, error_row_letter)

            # Check annotation
            index += 1
            pattern = r'^Kritikai jegyzetek:\s+\d+([-–]\d+)?\.$'
            try:
                annotation = itidata_json["entities"][itidata_id]["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"][
                    "text"]
                annotation_language = \
                    itidata_json["entities"][itidata_id]["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"]["language"]
                if (not bool(re.match(pattern, annotation))) or annotation_language != "hu":
                    error_row_letter.insert(index, f'CHECK "ANNOTATION" (P18) "{annotation}" @{annotation_language}')
            except KeyError:
                error_row_letter.insert(index, f'MISSING "ANNOTATION" (P18)')
            check_list_index(index, error_row_letter)

            # Check related item
            try:
                index += 1
                related_item_id = \
                    itidata_json["entities"][itidata_id]["claims"]["P129"][0]["mainsnak"]["datavalue"]["value"]["id"]
                related_item_label = get_eng_hun_item_labels_from_itidata(related_item_id, "")[0]
                # label_hu = itidata_json["entities"][itidata_id]["labels"]["hu"]["value"]
                label_hu = get_eng_hun_item_labels_from_itidata(itidata_id, "")[0]

                if normalize(related_item_label) != normalize(label_hu):
                    error_row_letter.insert(index, f'CHECK "RELATED TO" (P129) LABEL MISMACH "{related_item_label}"')
                    visualize_diff(normalize(related_item_label), normalize(label_hu))
            except KeyError:
                label_hu = "NO RELATED ITEM"
            check_list_index(index, error_row_letter)

            # Publication date
            index += 1
            publlication_date = []
            if itidata_json["entities"][itidata_id]["claims"].get("P218"):
                publlication_date.append("NO CREATION DATE (P218) IS NEEDED")
            if not itidata_json["entities"][itidata_id]["claims"].get("P57"):
                publlication_date.append("PUBLICATION DATE (P57) MISSING")
            else:
                if itidata_json["entities"][itidata_id]["claims"]["P57"][0]["mainsnak"]["datavalue"]["value"]["time"] != \
                        row[15].split("/")[0] and \
                        itidata_json["entities"][itidata_id]["claims"]["P57"][0]["mainsnak"]["datavalue"]["value"][
                            "precision"] != row[15].split("/")[1]:
                    publlication_date.append("PUBLICATION DATE (P57) INCORRECT")
                    # print(itidata_json["entities"][itidata_id]["claims"]["P57"][0]["mainsnak"]["datavalue"]["value"])
                    # print(row[15])
            if len(publlication_date) > 0:
                error_row_letter.insert(index, "; ".join(publlication_date))
            check_list_index(index, error_row_letter)

            # for num in range(len(error_row_letter)):
            #     print(num, error_row_letter[num])
            # print(error_row_letter, len(error_row_letter))
            AJOM17_error_list_file_writer.writerow(error_row_letter)


            # Check <term> and <supplied> "Elveszett" and comapre to "Raktári szám": elveszett

