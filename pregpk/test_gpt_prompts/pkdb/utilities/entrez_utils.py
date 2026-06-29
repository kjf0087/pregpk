import time
from Bio import Entrez
from tqdm import tqdm
from . import gen_utils

def text_from_pmids(pmids: list, email: str, api_key: str=None) -> dict:
    """
    Fetches all text available from Entrez API for a list of PMIDs. Returned text is split into sections (title,
    abstract, methods, etc.), although usually Entrez only returns article titles and abstracts.
    :param pmids: list of PMID strings to obtain texts from Entrez
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :return: nested dict where PMIDs (keys) map onto a dictionary containing sections of text returned from Entrez.
        eg. {'1234': {'title': 'Review of Current Literature', 'abstract':'We present a review of current literature.'},
             '0111': {'title': 'Effects of chemotherapy'}}
    """

    print('\nLoading abstracts for all articles using Entrez API...')
    time.sleep(0.1)

    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key
    max_pmids_per_call = 9999

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    texts = {}

    for i_pmids in tqdm(split_pmids):
        i_handle = Entrez.efetch(db="pubmed", id=gen_utils.comma_sep_str_from_list(i_pmids),
                               rettype="xml", retmode="text")
        i_responses = Entrez.read(i_handle)
        i_responses = gen_utils.convert_to_python_obj(i_responses)
        i_handle.close()

        for article in i_responses['PubmedArticle']:
            try:
                abstract = article['MedlineCitation']['Article']['Abstract']['AbstractText']
                abstract = " ".join(abstract)
                art_text = {'abstract': abstract}
            except KeyError:
                art_text = {}

            texts[article['MedlineCitation']['PMID']] = art_text

    return texts


def pmids_from_pubmed_query(query: str, email: str, api_key: str=None, free_articles_only: bool=False) -> list:
    """
    Fetches all PMIDs returned by a PubMed search query.
    :param query: string with PubMed query
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :param free_articles_only: boolean, whether to return only PMIDs containing free full texts
    :return: list containing PMIDs returned by PubMed search of inputted query
    """

    print('\nGetting PMIDs returned by query through Entrez API...')

    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key

    if free_articles_only:
        query = query + ' AND "freetext"[filter]'
        # query = query + ' AND "free only pmc"[filter]'

    handle = Entrez.esearch(db='pubmed', term=query, retmax=10000, sort='pub_date', datetype='pdat')
    response = Entrez.read(handle)
    response = gen_utils.convert_to_python_obj(response)
    handle.close()

    total = int(response['Count'])
    pmids = response['IdList']  # Convert to python native list and string

    if total < 10000:
        return pmids

    while len(pmids) < total:
        last_date = Entrez.read(Entrez.esummary(db='pubmed', id=pmids[-1], retmode='text'))[0]['PubDate'][:4]  # String with YYYY

        i_handle = Entrez.esearch(db='pubmed', term=query, retmax=10000, sort='pub_date', datetype='pdat',
                                        mindate=0000, maxdate=last_date)
        i_response = Entrez.read(i_handle)
        i_response = gen_utils.convert_to_python_obj(i_response)
        i_handle.close()

        i_pmids = i_response['IdList']
        pmids += i_pmids[i_pmids.index(pmids[-1])+1:]

    print(f"{total} PMIDs returned from PubMed query.")

    return pmids


def summaries_from_pmids(pmids: list, email: str, api_key: str=None) -> dict:
    """
    Returns Entrez esummaries for a list of PMIDs as a nested dict.
    :param pmids: list of PMIDs
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :return: nested dict with Entrez summaries for each of the queries PMIDs
        eg. {'1234': returned Entrez esummary json/dict,
             '0111': returned Entrez esummary json/dict}
    """
    Entrez.email = email
    if api_key is not None:
        Entrez.api_key = api_key
    max_pmids_per_call = 9999

    split_pmids = gen_utils.split_list(pmids, max_pmids_per_call)
    summaries = {}

    for i_pmids in tqdm(split_pmids):
        i_handle = Entrez.esummary(db='pubmed', id=gen_utils.comma_sep_str_from_list(i_pmids))
        i_resp = Entrez.read(i_handle)
        i_resp = gen_utils.convert_to_python_obj(i_resp)
        i_handle.close()

        summaries.update({i['Id']: i for i in i_resp})

    return summaries


def metadata_from_pmids(pmids: list, email: str, api_key: str=None) -> dict:
    """
    :param pmids: list of PMIDs
    :param email: string, NCBI account email address for access to Entrez API
    :param api_key: string, NCBI API key to reduce time between multiple requests
    :return: nested dict with article metadata returned by Entrez API
        eg. {
            '1234': {'title': 'Review of Current Literature',
                      'pub_date': 'Jan 01 2024',
                      'pub_year': 2024,
                      'source': 'Journal of Reviews',
                      ...},
            '0111': {...}
             }
    """

    print('\nLoading metadata from Entrez API...')

    summaries = summaries_from_pmids(pmids, email, api_key)
    # Clean data (inc. add defaults for fields that might not exist for some articles)
    for pmid, article in summaries.items():
        if 'DOI' not in article:
            article['DOI'] = ''

    metadata = {}
    for pmid, article in summaries.items():
        metadata[pmid] = {
            'title': article['Title'],
            'pub_date': article['PubDate'],
            'pub_year': int(article['PubDate'][:4]),
            'source': article['Source'],
            'is_english': bool('English' in article['LangList']),
            'pub_types': article['PubTypeList'],
            'is_review': bool('Review' in article['PubTypeList']),
            'doi': article['DOI'],
            'has_abstract': bool(article['HasAbstract']),
            'metadata': article,
        }

    return metadata
