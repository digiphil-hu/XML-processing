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
    input_folders = ["/home/eltedh/GitHub/migration-ajom-17",
               "/home/eltedh/GitHub/migration-ajom-18",
               "/home/eltedh/GitHub/migration-ajom-19"]
    koha_geo_global = set()
    for parsed, path in get_filenames(input_folders):
        koha_geo_global.update(get_koha_geo(parsed, path))
    with open("ajom_header_geonames.csv", "w") as outfile:
        for item in (sorted(koha_geo_global)):
            print(item, file=outfile)