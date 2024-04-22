from xml_methods import get_filenames, prettify_soup

path_list = ["/home/pg/Documents/GitHub/rmkt-17-6"]
path_out = "/home/pg/Documents/GitHub/XML-processing/RMKT_17_6/XML/"

for parsed, path in get_filenames(path_list):
    title_tag = parsed.find("title", {"type": "main"})
    if title_tag.get("key") is None:
        key_num = path.rstrip(".xml").split(".")[-1]
        if key_num.isdigit():
            title_tag["key"] = "body"
            title_tag["n"] = key_num
            if key_num != parsed.find("title", {"type": "num"}).text.rstrip("."):
                print("num error: ", path)
            with open(path_out + path.split("/")[-1], "w", encoding="utf-8") as new_xml:
                new_xml.write(prettify_soup(parsed))
        else:
            print("key num error: ", path)
    else:
        print("key num exists: ", path)

