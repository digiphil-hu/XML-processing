from collections import defaultdict
import csv

dhu_dict = defaultdict(int)
with open("Olahus_letters_itidata_2.csv", "r", encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file, delimiter="\t")
    for row in reader:
        dhu_dict[row[0].strip()] += 1
    for key, value in dhu_dict.items():
        if value > 1:
            print(key, value)


with open("Olahus_letters_itidata_2.csv", "r", encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file, delimiter="\t")
    duplum = False
    for row in reader:
        if duplum:
            row[0] += " II."
            row[1] += " II."
            print("\t".join(row))
        duplum = False
        if dhu_dict[row[0].strip()] > 1:
            duplum = True