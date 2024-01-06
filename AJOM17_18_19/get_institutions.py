from xml_methods import get_filenames

folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]

institution_set = set()
for parsed, path in get_filenames(folder_list):
    for inst in parsed.msDesc.find_all('institution'):
        if ";" in inst.text.strip():
            for inst_part in inst.text.split(";"):
                institution_set.add(inst_part.strip())
        else:
            institution_set.add(inst.text.strip())
for inst in institution_set:
    print(inst)
