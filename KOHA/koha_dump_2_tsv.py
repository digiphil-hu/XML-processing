from bs4 import BeautifulSoup


def parse_large_txt_file(input_file_path, output_tsv_path):
    # Open the TSV file for writing
    with open(output_tsv_path, 'w', encoding='utf-8') as tsv_file:
        # Write header to the TSV file
        tsv_file.write("Controlfield_001\t"
                       "Controlfield_003\t"
                       "Datafield_010\t"
                       "Datafield_100a\t"
                       "Datafield_100d}\t"
                       "Datafield_856u\t"
                       "Datafield_902a\t"
                       "Datafield_906a\n")

        # Open the large text file for reading line by line
        with open(input_file_path, 'r', encoding='utf-8') as file:
            in_record_segment = False
            record_segment = ""

            # Process each line in the file
            for line in file:
                if '<record>' in line:
                    in_record_segment = True
                    record_segment = line
                elif '</record>' in line and in_record_segment:
                    in_record_segment = False
                    record_segment += line

                    # Check if the segment contains the specified subfield
                    if '<subfield code="a">PERSO_NAME</subfield>' in record_segment:
                        # Parse the segment with BeautifulSoup
                        soup = BeautifulSoup(record_segment, 'xml')

                        # Extract values of controlfields
                        controlfield_001 = soup.find('controlfield',
                                                     {'tag': '001'}).text.strip().replace(' ', '')
                        controlfield_003 = soup.find('controlfield', {'tag': '003'}).text.strip()

                        # Extract the values of datafields
                        if soup.find('datafield', {'tag': '010'}):
                            datafield_010 = soup.find('datafield',{'tag': '010'}).find('subfield',
                                                    {'code': 'a'}).text.strip().replace(' ', '')
                        else:
                            datafield_010 = 'Unknown'

                        if soup.find('datafield', {'tag': '100'}).find('subfield', {'code': 'a'}):
                            datafield_100a = soup.find('datafield', {'tag': '100'}).find('subfield',
                                                                                     {'code': 'a'}).text.strip()
                        else:
                            datafield_100a = 'Unknown'
                        if soup.find('datafield', {'tag': '100'}).find('subfield', {'code': 'd'}):
                            datafield_100d = soup.find('datafield', {'tag': '100'}).find('subfield',
                                                                                     {'code': 'd'}).text.strip()
                        else:
                            datafield_100d = 'Unknown'
                        if soup.find('datafield', {'tag': '856'}):
                            datafield_856u = soup.find('datafield', {'tag': '856'}).find('subfield',
                                                                                         {'code': 'u'}).text.strip()
                        else:
                            datafield_856u = 'Unknown'

                        if soup.find('datafield', {'tag': '902'}):
                            datafield_902a = soup.find('datafield', {'tag': '902'}).find('subfield',
                                                                                         {'code': 'a'}).text.strip()
                        else:
                            datafield_902a = 'Unknown'
                        if soup.find('datafield', {'tag': '906'}):
                            datafield_906a = soup.find('datafield', {'tag': '906'}).find('subfield',
                                                                                         {'code': 'a'}).text.strip()
                        else:
                            datafield_906a = 'Unknown'

                        # Write values to the TSV file
                        tsv_file.write(f"{controlfield_001}\t{controlfield_003}\t{datafield_010}\t{datafield_100a}"
                                       f"\t{datafield_100d}\t{datafield_856u}\t{datafield_902a}\t{datafield_906a}\n")
                elif in_record_segment:
                    record_segment += line


# Example usage
input_file_path = '/home/eltedh/PycharmProjects/DATA/KOHA/auths.txt'
output_tsv_path = 'koha_pim.tsv'

parse_large_txt_file(input_file_path, output_tsv_path)