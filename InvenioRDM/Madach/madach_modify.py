import csv

from xml_methods import get_filenames, normalize, prettify_soup, remove_comments

path_list = ["/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Megállapított-szöveg"
             ,"/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Genetikus-szöveg"
             ,"/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja/Tanulmányok"]



for parsed, path in get_filenames(path_list):
    new_path = path.replace("/home/pg/Documents/GitHub/Madach_Az_ember_tragediaja", "/home/pg/Documents/GitHub/XML-processing/InvenioRDM/Madach")
    for ref in parsed.find_all("ref", {"target": True}):
        if ref["target"].startswith("mi-aet"):
            ref["target"] = "https://hdl.handle.net/20.500.14368/" + ref["target"]
            if "°" in ref.text:
                ref.string = ""
    parsed_new = remove_comments(parsed)

    with open(new_path, "w", encoding="utf8") as f:
        f.write(prettify_soup(parsed))



"""
with open("madach-PID-newPID.csv", "r", encoding="utf-8") as csv_file:
    ref_dict = dict()
    csv_reader = csv.reader(csv_file, delimiter="\t", quotechar='"')
    for row in csv_reader:
        ref_dict[row[0].strip()] = row[1].strip()
"""