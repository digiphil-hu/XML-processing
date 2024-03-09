# This code creates a tsv which consists the data of missing manuscripts of existing letters of AJOM17-18-19
import csv

from get_geo_namespace_id_itidata import get_eng_hun_item_labels_from_itidata
from xml_methods import find_difference_strings, write_to_csv

with open('manuscript_to_itidata.csv', 'w', encoding='utf8') as f:
    pass

with open("itidata_letters_no_manuscript.csv", "r", encoding="utf8") as letters_list:
    with open("/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/xml_header_tsv_manuscript.tsv", "r",
              encoding="utf8") as xml_tsv:
        letters_reader = csv.reader(letters_list, delimiter="\t")
        xml_tsv_reader = csv.reader(xml_tsv, delimiter="\t")
        xml_tsv_list = list(xml_tsv_reader)
        for row in letters_reader:
            manuscript_dict = dict()
            letter_id = row[0].split("/")[-1]
            letter_pid = row[1]
            letter_json = get_eng_hun_item_labels_from_itidata(letter_id, what_do_yo_need="json")
            xml_tsv_row = [rows for rows in xml_tsv_list if rows[2] == letter_pid]
            print(f'Letter id: {letter_id}, PID: {letter_pid}, {xml_tsv_row[0][2]}')

            manuscript_dict["P1"] = "Q15"  # Instance of: manuscript
            manuscript_dict['P41'] = "Q26"  # Genre: letter
            manuscript_dict['Lhu'] = letter_json["entities"][letter_id]["labels"]["hu"]["value"]
            manuscript_dict['Lhu_dif'] = find_difference_strings(letter_json["entities"][letter_id]
                                                                 ["labels"]["hu"]["value"], xml_tsv_row[0][3])
            manuscript_dict['P129'] = letter_id
            manuscript_dict['Dhu'] = xml_tsv_row[0][5]
            manuscript_dict['Den'] = xml_tsv_row[0][6]
            manuscript_dict['P7'] = xml_tsv_row[0][7]
            try:
                if xml_tsv_row[0][7] != letter_json["entities"][letter_id]["claims"]["P7"][0]\
                        ["mainsnak"]["datavalue"]["value"]["id"]:
                    print("P7 MISSMACH!")
            except:
                pass
            manuscript_dict['P80'] = xml_tsv_row[0][8]
            try:
                if xml_tsv_row[0][8] != letter_json["entities"][letter_id]["claims"]["P80"][0]\
                        ["mainsnak"]["datavalue"]["value"]["id"]:
                    print("P80 MISSMACH!")
            except:
                pass
            manuscript_dict['P85'] = xml_tsv_row[0][9]
            manuscript_dict['P203'] = xml_tsv_row[0][10]
            manuscript_dict['P204'] = xml_tsv_row[0][11]
            manuscript_dict['P2018'] = xml_tsv_row[0][12]

            write_to_csv(manuscript_dict, "manuscript_to_itidata.csv")
