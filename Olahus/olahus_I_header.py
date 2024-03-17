import csv

from bs4 import BeautifulSoup
import xml_methods as xml

# Get ITIdata id for each letter
letter_itidata_id = dict()
with open("import_test_olahus_plus_item_id.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter="\t")
    for row in reader:
        letter_itidata_id[row[17]] = row[16].split(".")[-1]
# for key, value in letter_itidata_id.items():
#     print(key, value)

# List of folders whete the TEI XML's are found
folder_list = ["/home/eltedh/GitHub/Olahus/Olahus 1"]

with open("header_pattern_1.xml", "r", encoding="utf-8") as xml_file:
    soup = BeautifulSoup(xml_file, "xml")
    new_header = soup.find("teiHeader")

for parsed, path in xml.get_filenames(folder_list):
    with open("header_pattern_1.xml", "r", encoding="utf-8") as xml_file:
        soup = BeautifulSoup(xml_file, "xml")
        new_header = soup.find("teiHeader")
    old_header = parsed.find("teiHeader")
    file_name = path.split("/")[-1]

    # Title type num
    num = old_header.find("biblScope", {"unit": "entry"}).string.strip()
    new_header.titleStmt.find("title", {"type": "num"}).string = num
    # print(new_header.find("title", {"type": "num"}))

    # Title type main
    for title_tag in old_header.titleStmt.find_all("title"):
        if len(title_tag.attrs) == 0 or title_tag.get("type") == "main":
            main_title = xml.normalize_whitespaces(title_tag.string.strip())
            new_header.titleStmt.find("title", {"type": "main"}).string = main_title
            new_header.titleStmt.find("title", {"type": "main"})["n"] = num
            # print(new_header.titleStmt.find("title", {"type": "main"}))
        elif title_tag.get("type") != "num":
            print(title_tag)

    # PID
    pid = old_header.find("idno", {"type": "PID"}).string.strip()
    if ":" in pid:
        pid = pid.split(":")[-1]
    if pid.split(".")[-1] != file_name.replace(".xml", ""):
        print(pid, file_name)
    new_header.find("idno", {"type": "PID"}).string = pid

    # Itidata id
    for key, value in letter_itidata_id.items():
        if value == file_name.replace(".xml", ""):
            letter_id = key
    for idno_tag in new_header.publicationStmt.find_all("idno", {"type": "ITIdata"}):
        if idno_tag.text == "letter_itidata":
            idno_tag.string = letter_id

    # Github link
    new_header.publicationStmt.find("ref", target=True)["target"] = "https://github.com/digiphil-hu/nicolaus-olahus-epistulae-pars-I/blob/main/" + file_name
    # print(new_header.publicationStmt.find("ref", target=True))

    # notesStmt
    notes_stms = old_header.find("notesStmt")
    for note_tag in notes_stms.find_all("note"):
        if xml.normalize(note_tag.text.strip()) == "":
            note_tag.decompose()
    for ref_target in notes_stms.find_all("ref", target=True):
        if (xml.normalize(ref_target.text.strip()) == ""
                and ref_target["target"].replace("http:/digiphil.hu/o:olahus.tei.", "")) == "":
            ref_target.decompose()
        else:
            ref_target["target"] = ref_target["target"].replace("http:/digiphil.hu/o:olahus.tei.", "")
    new_header.fileDesc.append(notes_stms)

    # msDesc
    new_header.sourceDesc.append(old_header.sourceDesc.msDesc)

    # listWit
    if old_header.sourceDesc.find("listWit"):
        new_header.sourceDesc.append(old_header.sourceDesc.listWit)

    # biblScope
    new_header.find("biblScope", {"unit": "entry"}).string = old_header.find("biblScope", {"unit": "entry"}).string
    new_header.find("biblScope", {"unit": "page"}).string = old_header.find("biblScope", {"unit": "page"}).string

    # encodingDesc
    if "sz" not in file_name:
        new_header.encodingDesc.decompose()

    # creation, correspDesc
    new_header.profileDesc.append(old_header.profileDesc.creation)
    new_header.profileDesc.append(old_header.profileDesc.correspDesc)


    with open("")

