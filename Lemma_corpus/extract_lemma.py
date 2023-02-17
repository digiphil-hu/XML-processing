import os
from bs4 import BeautifulSoup
import  time


def file_list(path_in):
    filelist_in = []
    for dirpath, subdirs, files in os.walk(path_in):
        for x in files:
            if x.endswith(".xml"):
                filelist_in.append(os.path.join(dirpath, x))
    filelist_in.sort()
    return filelist_in


def write_corpus(file_path):
    l_list = lemma_list(file_path)
    with open("corpus.cor", "a", encoding="utf8") as f_cor:






def lemma_list(path):
    soup = BeautifulSoup(path, "xml")
    lem_list = [w["lemma"] for w in soup.find_all("w")]
    return lem_list




if __name__ == '__main__':
    with open("corpus.cor", "w", encoding="utf8") as f:
        actual_path = "/home/eltedh/PycharmProjects/DATA"

