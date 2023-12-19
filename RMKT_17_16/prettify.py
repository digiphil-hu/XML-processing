from xml_methods import prettify_soup, get_filenames

path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/modified-rmkt-17-16/"]
new_path = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/XML/"

for parsed, path in get_filenames(path_list):
    new_filename = path.split("/")[-1]
    parsed = prettify_soup(parsed)
    with open(new_path + new_filename, 'w', encoding='utf-8') as file:
        file.write(parsed)