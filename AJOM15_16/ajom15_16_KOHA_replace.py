from xml_methods import get_filenames, prettify_soup

folder_list = ["/home/pg/Documents/GitHub/Arany_15/tei xml", "/home/pg/Documents/GitHub/Arany_16/tei xml"]

koha_persname = set()
for parsed, path in get_filenames(folder_list):
    for person in parsed.find_all("persName"):
        if person.find("idno") is not None:
            if person.idno.get("type") is not None:
                if "KOHA" in person.idno["type"]:
                    koha_persname.add(prettify_soup(person.idno))

for person in koha_persname:
    print(person)
