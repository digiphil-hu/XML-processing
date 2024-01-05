import csv

from get_geo_namespace_id_itidata import get_eng_hun_item_labels_from_itidata

# Get the list of letters present in itidata
with (open("itidata_ajom17_sparql_export_short.tsv", "r", encoding="utf-8") as itidata_query_file):
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
        AJOM17_error_list_file_writer = csv.writer(AJOM17_error_list_file)
        for row in shortened_xml_reader:
            itidata_id = row[0]

            # Check if Hungarian and English lables are identical:
            label_hu_eng = get_eng_hun_item_labels_from_itidata(itidata_id)
            # if label_hu_eng[0] != label_hu_eng[1]:
            print(itidata_id, label_hu_eng)



