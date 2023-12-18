from xml_methods import get_filenames, normalize

path_list = ["/home/eltedh/GitHub/RMKT-XVII-16/modified-rmkt-17-16/"]
new_path = "/home/eltedh/PycharmProjects/XML-processing/RMKT_17_16/XML/"

title_num_filename_dict = dict()
for parsed, path in get_filenames(path_list):
    if parsed.titleStmt.find("title", {"type": "num"}) is not None:
        title_num_tag = parsed.titleStmt.find("title", {"type": "num"})
        if title_num_tag.text.replace(".", "").isdigit() is not True:
            print(title_num_tag)
        title_num_filename_dict[title_num_tag.text] = path.split("/")[-1].replace(".xml", "")

for parsed, path in get_filenames(path_list):
    write_file = False
    for ref in parsed.find_all("ref"):
        new_filename = path.split("/")[-1]
        if ref.get("type") is None and ref.get("target") is None:
            ref_text = normalize(ref.text)
            if ref_text.split(".")[0].isdigit():
                num_key = ref_text.split(".")[0] + "."
                ref["target"] = title_num_filename_dict[num_key]
                print(f"Ref: {ref_text} -> {num_key} -> {title_num_filename_dict[num_key]}")
                write_file = True

    if write_file:
        with open(new_path + new_filename, 'w', encoding='utf-8') as file:
            file.write(str(parsed))
