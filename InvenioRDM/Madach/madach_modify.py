import csv

from xml_methods import get_filenames, normalize, prettify_soup

path_list = ["/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Megállapított-szöveg"
             ,"/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Genetikus-szöveg"
             ,"/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Tanulmányok"]



for parsed, path in get_filenames(path_list):
    for ref in parsed.find_all("ref", {"target": True}):
        for old_target in ref_dict.keys():
            if old_target in ref["target"]:
                ref["target"] = ref["target"].replace(old_target, ref_dict[old_target])
        print(ref["target"])

    with open(path, "w", encoding="utf8") as f:
        f.write(prettify_soup(parsed))



"""
with open("madach-PID-newPID.csv", "r", encoding="utf-8") as csv_file:
    ref_dict = dict()
    csv_reader = csv.reader(csv_file, delimiter="\t", quotechar='"')
    for row in csv_reader:
        ref_dict[row[0].strip()] = row[1].strip()
"""