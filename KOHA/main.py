# This code parses XML files, reads person name ID-s, map them to vocabularies and then change the ID-s.
from KOHA.koha_pim_biblio import koha_pim_biblio
from koha_2_tsv import create_koha_id_tsv
from itidata_query import itidata_query

# 1: extract KOHA and VIAF ID's from XML files of a given list of folders

github_folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
                      "/home/eltedh/GitHub/migration-ajom-18",
                      "/home/eltedh/GitHub/migration-ajom-19",
                      "/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-6",
                      "/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-12",
                      "/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-16",
                      "/home/eltedh/GitHub/Petofi_Sandor"]

output_path = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/"
create_koha_id_tsv(github_folder_list, output_path)

# 2: Looking up KOHA ID's in a TSV (koha_pim.tsv) created from the KOHA dump (auths.txt) by koha_dump_2_tsc.py
# Output:KOHA/KOHA_output_data/koha_pim_biblio.tsv

koha_pim_biblio("/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/koha_id_list.tsv",
                "/home/eltedh/PycharmProjects/XML-processing/KOHA/koha_pim.tsv",
                "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/koha_pim_biblio.tsv")

# 3: Run a query to find ITIdata item id-s based on the PIM id-s. PIM ID-s are taken form KOHA koha_pim_biblio.tsv
# Input, output TSV file path
path_in = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/koha_pim_biblio.tsv"
path_out = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/itidata_koha_pim_biblio.tsv"
itidata_query(path_in, path_out)

