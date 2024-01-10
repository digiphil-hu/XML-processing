import csv
import re
from xml_methods import get_filenames, prettify_soup
from bs4 import BeautifulSoup


folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]

koha_itidata_dict = {}
with open("/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_itidata_koha_pim_biblio.csv", "r",
          encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        koha_itidata_dict[row[5]] = row[1]

counter_itidata = 0
counter_empty_koha_auth = 0
for parsed, path in get_filenames(folder_list):
    # new_path = "/home/eltedh/PycharmProjects/XML-processing/AJOM17_18_19/AJOM_itidata/XML/" + path.split("/")[-1]
    print(path)
    for idno_tag in parsed.find_all('idno', {'type': 'KOHA_GEO'}):
        if idno_tag.text:
            idno_text = re.sub(r'\D', '', idno_tag.text)
            if idno_text not in koha_itidata_dict:
                print(idno_text)
            else:
                idno_tag.string = koha_itidata_dict[idno_text]
                idno_tag['type'] = 'ITIdata'
                counter_itidata += 1
    for idno_tag in parsed.find_all('idno', {'type': 'KOHA_GEO'}):
        del idno_tag.attrs['type']
        counter_empty_koha_auth += 1
    # with open(path, "w", encoding="utf-8") as outfile:
    #     outfile.write(prettify_soup(parsed))
print(counter_itidata)
print(counter_empty_koha_auth)
