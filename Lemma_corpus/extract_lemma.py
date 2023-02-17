import os
from bs4 import BeautifulSoup
import time
import lxml
from multiprocessing import Pool


def file_list(path_in):
    filelist_in = []
    for dirpath, subdirs, files in os.walk(path_in):
        for x in files:
            if x.endswith(".xml"):
                filelist_in.append(os.path.join(dirpath, x))
    filelist_in.sort()
    return filelist_in


def write_corpus(file_path):
    begin = time.time()
    l_list = lemma_list(file_path)
    with open("corpus.cor", "a", encoding="utf8") as f_cor:
        print(" ".join(l_list), file=f_cor)
        end = time.time()
        print(file_path, end-begin)


def lemma_list(path):
    with open(path, "r", encoding="utf8") as f_xml:
        soup = BeautifulSoup(f_xml, "xml")
        lem_list = [w["lemma"] for w in soup.find_all("w")]
        return lem_list


if __name__ == '__main__':
    actual_path = input("Path of the files to process?\nDefault: /home/eltedh/PycharmProjects/DATA\n")
    if actual_path.replace(" ", "") == "":
        actual_path = "/home/eltedh/PycharmProjects/DATA"
    overwrite = input("Add new lemmas to corpus(a) or start new (w)? Default: start new.\n")
    if overwrite == "a":
        pass
    else:
        overwrite = "w"
    with open("corpus.cor", overwrite, encoding="utf8") as f:
        files = file_list(actual_path)
        with Pool() as p:
            p.map(write_corpus, files)
