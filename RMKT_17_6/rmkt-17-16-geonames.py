import csv

def write_selected_geonames(short_list, geo_koha_dump, output_file):
    with open(short_list, 'r', encoding='utf') as list_file:
        short_list_set = set()
        for line in list_file:
            short_list_set.add(line.strip())
    print('Short list set:', short_list_set)
    with open(geo_koha_dump, 'r', encoding='utf-8') as dump_file:
        with open(output_file, 'w', encoding='utf') as output_file:
            reader = csv.reader(dump_file, delimiter='\t')
            writer = csv.writer(output_file, delimiter='\t')
            for row in reader:
                if row[0] in short_list_set:
                    writer.writerow(row)


geo_koha_dump = "/home/eltedh/PycharmProjects/XML-processing/KOHA/geonames_form_koha_dump.tsv"
short_list = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/KOHA_GEO_list.txt"
selected_geo_dump = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/selected_geo_dump.tsv"

write_selected_geonames(short_list, geo_koha_dump, selected_geo_dump)