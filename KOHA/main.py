# This code parses XML files, reads person name ID-s, map them to vocabularies and then change the ID-s.

from koha_2_tsv import create_koha_id_tsv

# First step: extract KOHA and VIAF ID's from XML files of a given list of folders

github_folder_list = ["/home/eltedh/GitHub/migration-ajom-17",
                      "/home/eltedh/GitHub/migration-ajom-18",
                      "/home/eltedh/GitHub/migration-ajom-19",
                      "/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-6",
                      "/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-12",
                      "/home/eltedh/GitHub/RMKT-XVII-16/RMKT-XVII-16",
                      "/home/eltedh/GitHub/Petofi_Sandor"]

output_path = "/home/eltedh/PycharmProjects/XML-processing/KOHA/KOHA_output_data/"
create_koha_id_tsv(github_folder_list, output_path)
