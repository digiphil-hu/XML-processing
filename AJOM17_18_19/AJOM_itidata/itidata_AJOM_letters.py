import csv

# Get the list of letters present in itidata
with (open("itidata_ajom17_sparql_export.tsv", "r", encoding="utf-8") as itidata_query_file):
    itidata_reader = csv.reader(itidata_query_file, delimiter="\t")
    letter_id_list = []
    for row in itidata_reader:
        letter_id_list.append(row[4].strip("."))
    if len(letter_id_list) != len(set(letter_id_list)):
        print("DUPLUM!", len(letter_id_list), len(set()))

# Single out letters
with open("/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/output.tsv", "r", encoding="utf-8") as xml_tsv_file:
    xml_tsv_reader = csv.reader(xml_tsv_file, delimiter="\t")
    for row in xml_tsv_reader:
        if row[0] in letter_id_list:

