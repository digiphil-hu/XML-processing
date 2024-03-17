# !/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import logging
from pathlib import Path
from wikidataintegrator import wdi_core, wdi_login


def create_logger(logname):
    # Creating and Configuring Logger
    Log_Format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename=logname,
                        filemode="w",
                        format=Log_Format,
                        level=logging.INFO
                        )
    logger = logging.getLogger()
    logger.info("Logging started")
    return logger


# Lhu	Len	Dhu	Den	P1	P41	P7	P37	P80	P44	P57	P49	P106	P241	P242
WDI_DICT = {'P1': wdi_core.WDItemID,    # TODO: az aktuális fejlécnek megfelellően bővíthető
            'P7': wdi_core.WDItemID,
            'P80': wdi_core.WDItemID,
            'P85': wdi_core.WDItemID,
            'P41': wdi_core.WDItemID,
            'P44': wdi_core.WDItemID,
            'P49': wdi_core.WDString,
            'P106': wdi_core.WDString,
            'P37': wdi_core.WDString,
            # 'P18': wdi_core.WDMonolingualText,
            'P57': wdi_core.WDTime,
            'P218': wdi_core.WDTime,
            'P241': wdi_core.WDUrl,
            'P242': wdi_core.WDUrl
            }  # hogy lehessen variálni, ha kell (még túl lehetne tolni úgy a jövőben, hogy ez egy config fájlban van


def parse_tsv(tsvpath):
    # fejléc-érték párokba olvassa be
    with open(tsvpath) as inp:
        table_lines = inp.readlines()
        # tab_header = table_lines.pop(0).strip().split('\t')[1:]
        tab_header = table_lines.pop(0).strip().split('\t')
        for line in table_lines:
            line_dict = dict()
            for k, v in zip(tab_header, line.strip().split('\t')):
                line_dict[k] = v
            yield line, line_dict


def customize_record_api_input(data_dict):
    """"""
    prep_name_statements = []
    for prop_id in WDI_DICT.keys():
        vals_ = data_dict[prop_id].split(';')  # egy cellában több azonosító
        if len(vals_) > 0:  # üres cella
            for val_ in vals_:
                if len(val_) > 0:
                    val_type = WDI_DICT[prop_id]
                    if val_type == wdi_core.WDTime:
                        val_parts = data_dict[prop_id].split('/')  # +2014-01-01T00:00:00Z/9
                        prep_name_statements.append(val_type(val_parts[0], prop_nr=prop_id, precision=int(val_parts[1]),
                                                             check_qualifier_equality=False))
                    elif prop_id == 'P7' and val_.startswith('P39'):
                        qual_prop, qual_string = val_.split(':')
                        the_qual = wdi_core.WDString(qual_string, prop_nr=qual_prop, check_qualifier_equality=False,
                                                     is_qualifier=True)
                        _qualifiers = [the_qual]
                        statemen_withqual = wdi_core.WDString(value="somevalue", snak_type="somevalue",
                                                              prop_nr='P7',
                                                              check_qualifier_equality=False, qualifiers=_qualifiers)
                        prep_name_statements.append(statemen_withqual)
                    elif prop_id == 'P80' and val_.startswith('P39'):
                        qual_prop, qual_string = val_.split(':')
                        the_qual = wdi_core.WDString(qual_string, prop_nr=qual_prop, check_qualifier_equality=False,
                                                     is_qualifier=True)
                        _qualifiers = [the_qual]
                        statemen_withqual = wdi_core.WDString(value="somevalue", snak_type="somevalue",
                                                              prop_nr='P80',
                                                              check_qualifier_equality=False, qualifiers=_qualifiers)
                        prep_name_statements.append(statemen_withqual)
                    else:
                        print(val_, prop_id)
                        prep_name_statements.append(val_type(val_, prop_nr=prop_id, check_qualifier_equality=False))
    return data_dict, prep_name_statements


def create_new_item_simple_tsv(header_dict, item_statements):
    """STATEMENTS >>>
    Language 	Label 	Description 	Also known as
    """
    api_url = 'https://itidata.abtk.hu/w/api.php'
    it_name = header_dict['Lhu']
    try:
        login_instance = wdi_login.WDLogin(user="SárköziLindnerZsófia", pwd="",  # TODO !!!
                                           mediawiki_api_url=api_url)
        try:
            wdPage = wdi_core.WDItemEngine(data=item_statements, mediawiki_api_url=api_url)
            wdPage.set_label(header_dict['Lhu'], lang="hu")
            wdPage.set_label(header_dict['Lhu'], lang="en")
            wdPage.set_description(header_dict['Dhu'], lang="hu")
            wdPage.set_description(header_dict['Den'], lang="en")
            # wdPage.set_aliases(header_dict['aliases'], lang="hu")
            wdPage.write(login_instance)
            result = wdPage.get_wd_json_representation()
            new_id = list(result['claims'].items())[0][1][0]['id'].split('$')[0]
            ITI_LOG.info(f'import succedded:\t{new_id}:\t {result}')
            return new_id
        except Exception as w_ex:
            ITI_LOG.error(f'{w_ex}:\t{it_name}')
            return False
    except Exception as e:
        print('LOGIN ERROR')
        ITI_LOG.error(f'{e}:\t{it_name}')
        return False


def import_main(table_f):
    ret_file = open('import_test_olahus_plus_item_id.csv', 'a')
    # Katának: az eredeti táblázatot egészíti ki a létrehozott azonosítókkal
    for origi_line, rec_data in parse_tsv(table_f):
        rec_data_, item_statements_ = customize_record_api_input(rec_data)
        ret_create = create_new_item_simple_tsv(rec_data_, item_statements_)
        if ret_create:
            ret_line = f'{origi_line.strip()}\t{ret_create}\n'
            ret_file.write(ret_line)


if __name__ == '__main__':
    tsv_fn = Path('import_test_olahus.csv')
    ITI_LOG = create_logger(f'ITIData_{tsv_fn.stem}.log')
    import_main(tsv_fn)
