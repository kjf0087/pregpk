import warnings
import requests
import time
import json
from tqdm import tqdm
from . import gen_utils


def query_from_pmids(pmids: list) -> str:
    """
    Creates PubTator 3 API query for full text data from list of PMIDs.
    :param pmids: list of PMIDs
    :return: string used to query full-text information from PubTator API
    """
    pmids_str = gen_utils.comma_sep_str_from_list(pmids)
    return f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson?pmids={pmids_str}&full=true"


def text_from_pmids(pmids: list) -> dict:
    # TODO: Fix the fact that "loading available full text data..." is printing after first tqdm bar

    """
    Fetches all text available from PubTator 3 API for a list of PMIDs. Returned text is split into sections (title,
    abstract, methods, etc.).
    :param pmids: list of PMID strings to obtain texts from PubTator 3
    :return: nested dict where PMIDs (keys) map onto a dictionary containing sections of text returned from PubTator.
        eg. {'1234':
                {'title': 'Review of Current Literature',
                 'abstract':'We present a review of current literature.'
                 'methods': 'We reviewed all the literature on PubMed.',
                 'discuss': 'There have been a lot of advancements to the field but still several limitations',
                 },
             '0111':
                {...}
            }
    """

    print('\nLoading available full text data from PubTator API...')
    time.sleep(0.1)  # For some reason print statement showing up after first tqdm loading bar

    min_request_dt = 0.3
    last_req_t = time.time() - min_request_dt*2
    max_pmids_per_call = 99

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    texts = {}

    for i_pmids in tqdm(split_pmids):
        time.sleep(max(0.3 - (time.time() - last_req_t), 0))  # Not supersede PubTator maximum calls per second
        last_req_t = time.time()  # Have to set before the request (since the request is what takes longest per iter)
        resp = requests.get(query_from_pmids(i_pmids))

        if resp.status_code == 200:  # Successful request
            articles = [json.loads(i) for i in resp.text.split('\n') if i]  # "if i" to remove falsey values (empty string)
            for i in articles:
                i['pmid'] = str(i['pmid'])  # Returned as integer

            # Check whether there were any faulty returned texts (still treated as status_code == 200, "text" attr is
            # just empty string)
            if len(articles) < len(i_pmids):  # Likely an article that has not yet been added to PubTator
                returned_pmids = [art['pmid'] for art in articles]
                texts.update({i: {} for i in i_pmids if i not in returned_pmids})  # text[pmid] = {} if not in PubTator yet

            for art in articles:
                art_text = {}  # List of sections returned
                for passage in art['passages']:
                    if passage['text']:  # Only if passage actually has text, not an empty string
                        try:
                            section = passage['infons']['section_type'].lower()
                        except KeyError:  # Probably because only title and abstract
                            section = passage['infons']['type']
                        except:
                            warnings.warn(f"PubTator return for PMID {art['pmid']} does not have 'section_type' or "
                                          f"'type' fields as expected.")
                            texts[art['pmid']] = {}
                            continue

                        if section not in art_text:  # Add section if not yet in dictionary
                            art_text[section] = ''
                        art_text[section] += passage['text'] + ' '

                for sec in art_text.keys():
                    art_text[sec] = art_text[sec][:-1]  # Delete final space

                texts[art['pmid']] = art_text

    return texts

