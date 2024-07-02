import csv
from collections import defaultdict

folder_list = [
    "/home/pg/Documents/GitHub/XML-processing/AJOM15_16/AJOM_15-16_itidata_koha_pim_biblio_modified.csv",
    "/home/pg/Documents/GitHub/XML-processing/AJOM17_18_19/AJOM17-18-19_itidata_koha_pim_biblio_modified.csv"
            ]

koha_itidata_dict = defaultdict(set)
for element in folder_list:
    with open(element, "r", encoding="utf8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            koha_id = row[3]
            itidata_id = row[1]
            # if not itidata_id.lstrip("Q").isdigit():
            #     itidata_id =
            # if itidata_id.lstrip("Q").isdigit() and itidata_id not in koha_itidata_dict[koha_id]:
            koha_itidata_dict[koha_id].add(itidata_id)

for key, values in koha_itidata_dict.items():
    has_itidata = False
    for value in values:
        if value.lstrip("Q").isdigit():
            has_itidata = True
    if has_itidata is False:
        print(key, values)