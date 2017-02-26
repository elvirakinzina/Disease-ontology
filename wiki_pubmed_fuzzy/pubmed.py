from Bio import Entrez

def search(query, topK):
    Entrez.email = 'polinashichkova@gmail.com'
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax=str(topK),
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'polinashichkova@gmail.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results


def get(query, topK=1):
    '''Get by query'''
    
    result = search(query, topK)
    
    id_list = result['IdList']
    if len(id_list) == 0:
        return None
        
    pages = fetch_details(id_list)
    
    return [paper['MedlineCitation']['Article']['ArticleTitle'] 
            for paper in pages['PubmedArticle']]
    

