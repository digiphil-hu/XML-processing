from get_geo_namespace_id import get_wikidata_item_id_from_wikidata_api, get_wikidata_item_info, \
    get_subclasses_of_human_settlement, get_item_labels_from_wikidata
from get_geo_namespace_id_itidata import get_itidata_subclasses_of_human_settlement, get_itidata_item_info, \
    get_itidata_item_id, get_item_labels_from_itidata
from xml_methods import get_filenames
import csv

def get_koha_geo(soup, file):
    koha_geo_per_xml = set()
    for element in soup.teiHeader.find_all('note'):
        element.decompose()
    tag_list = ["creation", "correspDesc"]
    for tag in tag_list:
        for parent_tag in soup.teiHeader.find_all(tag):
            for placename in parent_tag.find_all('placeName'):
                if placename.string:
                    koha_geo_per_xml.add(placename.string)
    return koha_geo_per_xml


if __name__ == '__main__':
    # input_folders = ["/home/eltedh/GitHub/migration-ajom-17",
    #            "/home/eltedh/GitHub/migration-ajom-18",
    #            "/home/eltedh/GitHub/migration-ajom-19"]
    # koha_geo_global = set()
    # for parsed, path in get_filenames(input_folders):
    #     koha_geo_global.update(get_koha_geo(parsed, path))
    # with open("ajom_header_geonames.csv", "w") as outfile:
    #     for item in (sorted(koha_geo_global)):
    #         print(item, file=outfile)

    # Create a set from the subclass dictionarys
    wikidata_settlement_subclasses = get_subclasses_of_human_settlement()
    wikidata_subclass_set = set(item[0] for item in wikidata_settlement_subclasses)

    itidata_settlement_subclasses = get_itidata_subclasses_of_human_settlement()
    itidata_subclass_set = set(item[0] for item in itidata_settlement_subclasses)

    print("Wikidata human settlement subclasses:", len(wikidata_subclass_set))
    print("Itidata human settlement subclasses:", len(itidata_subclass_set))

    with open("/home/eltedh/PycharmProjects/XML-processing/Arany_letter_header/AJOM_GEO/ajom_header_geonames.csv",
              "r", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter="\n")
        for row in reader:
            label_to_search = row[0].strip()
            print(label_to_search)

            # Get the Itidata and Wikidata item ID using the API
            itidata_item_ids = get_itidata_item_id(label_to_search)
            wikidata_item_ids = get_wikidata_item_id_from_wikidata_api(label_to_search)

            # Get information for the specified Itidata and Wikidata item IDs
            itidata_result_dict = get_itidata_item_info(itidata_item_ids)
            wikidata_result_dict = get_wikidata_item_info(wikidata_item_ids)

            # Single out settlements
            for key, value in itidata_result_dict.items():
                if not set(value["instance_of"]).isdisjoint(itidata_subclass_set):
                    item_id_new = []
                    for item_id in value["instance_of"]:
                        item_id_new.append(get_item_labels_from_itidata(item_id))
                    value["instance_of"] = item_id_new
                    item_id_new = []
                    for item_id in value["country"]:
                        item_id_new.append(get_item_labels_from_itidata(item_id))
                    value["country"] = item_id_new
                    print("ITIdata: ", key, value)

            for key, value in wikidata_result_dict.items():
                if not set(value["instance_of"]).isdisjoint(wikidata_subclass_set):
                    item_id_new = []
                    for item_id in value["instance_of"]:
                        item_id_new.append(get_item_labels_from_wikidata(item_id))
                    value["instance_of"] = item_id_new
                    item_id_new = []
                    for item_id in value["country"]:
                        item_id_new.append(get_item_labels_from_wikidata(item_id))
                    value["country"] = item_id_new
                    print("Wikidata: ", key, value)
