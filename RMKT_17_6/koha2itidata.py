import csv


def tsv_to_dict(tsv_path):
    koha_itidata_dict = dict()
    with open(tsv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            koha_itidata_dict[row[3]] = row[1]
    return koha_itidata_dict


def idno_koha2itidata(parsed_xml, xml_path, koha_itidata_dict):
    koha_list = []
    for idno_tag in parsed_xml.find_all('idno', {'type': 'KOHA_AUTH'}):
        # print(idno_tag.parent.name, idno_tag.string, idno_tag.get('corresp'))
        # if idno_tag.parent.name == 'persName':
            koha_key = idno_tag.string.replace('KOHA_AUTH:', '').strip()
            # print(idno_tag.string, xml_path)
            idno_tag['type'] = 'ITIdata'
            try:
                idno_tag.string = koha_itidata_dict[koha_key]
            except KeyError:
                print(idno_tag.text.split(":")[1])
    for idno_tag in parsed_xml.find_all('idno', {'type': 'KOHA_GEO'}):
        koha_key = idno_tag.string.replace('KOHA_GEO:', '').strip()
        idno_tag['type'] = 'ITIdata'
        try:
            idno_tag.string = koha_itidata_dict[koha_key]
        except KeyError:
            print(koha_key)
    return parsed_xml
