import multiprocessing
import requests
import json
from wiki_pubmed_fuzzy.ontology import get_ontology
from gensim.models import word2vec, doc2vec

# TREE = get_ontology("../data/doid.obo")
model_trigram = word2vec.Word2Vec.load('models/trigram_100features_10minwords_5context')
model_doc2vec = doc2vec.Doc2Vec.load('models/doc2vec')
ontology = get_ontology('data/doid.obo')

def request_synonyms(oid, iri):
    j = requests.get('http://www.ebi.ac.uk/ols/api/ontologies/' + oid + '/terms?iri=' + iri).json()
    return j["_embedded"]["terms"][0]["synonyms"] if "_embedded" in j else []


def search_others(query, doids):
    j = requests.get('http://www.ebi.ac.uk/ols/api/search?q=' + query + '&ontology=efo, hp, ogms, ordo').json()

    results = []
    syns = set()
    for item in j['response']['docs']:
        if 'iri' in item:
            ss = request_synonyms(item['ontology_name'], item['iri'])
            if ss:
                for s in ss:
                    syns.add(s.lower().strip())

    for syn in syns:
        r = search_doid(syn, True, doids)
        if len(r) > 0:
            results.append(r)

    return results


def search_doid(query, exact, doids):
    try:
        matches = []
        j = requests.get('http://www.ebi.ac.uk/ols/api/search?q=' + query + '&ontology=doid&exact=' + str(exact).lower()).json()

        for item in j['response']['docs']:
            if 'obo_id' in item and item['obo_id'] not in doids:
                matches.append({
                                 'id':item['obo_id'],
                                 'desc':next(iter(item['description'])) if 'description' in item else '',
                                 'label':item['label'],
                                })
                doids.add(item['obo_id'])
        return matches
    except:
        return []

def search(query):
    # TODO: check res format
    flag, res, _ = find_answer(query, ontology, model_trigram, model_doc2vec)
    
    if flag:
        return {'query': query, 'exact_matches': res}
    else:
        return {'query': query, 'text': res}

def parse(text):
    lines = list(l.strip() for l in text.split('\n') if len(l.strip()) > 0)

    if len(lines) == 4 and all(l.startswith('#') for l in lines):
        # test data format
        def getTerms(line):
            return list(map(lambda s: s.strip(), line.split(':')[1].split(',')))
        reason = getTerms(lines[0])
        additional = getTerms(lines[3])
    else:
        reason = [text]
        additional = []
    return {'reason': reason, 'additional': additional}


def format_response(r):
    s = ""

    if 'exact_matches' in r:
        s += (
             "Exact match\n" +
             "Query: " + r['query'] + '\n'  +
             "Name: {0}\n"
             "# {1}").format(r['exact_matches'][0], r['exact_matches'][1])
    else:
        s += "Best fuzzy match\n" + r['text']

    return s


def lookup(text):
    #try:

    parsed = parse(text)
    strings = parsed['reason'] + parsed['additional']

    results = map(search, strings)

    for i in range(len(results)):
        yield format_response(results[i])
    #except:
    #    yield "Not found"

    
from gensim.models import word2vec, doc2vec


from threading import Thread
from time import sleep
import numpy as np

import fuzzywuzzy.process as fuzzy_process
from fuzzywuzzy import fuzz
from wiki_pubmed_fuzzy import wiki
from wiki_pubmed_fuzzy import pubmed
from src_tree.best_vertex import find_best_vertex

from NLP import nlp

#query_results = None
def fn_get_q(query, names, mode='W'):
    if mode == 'W':
        scorer=fuzz.WRatio
    else:
        scorer=fuzz.ratio
        
    try:
        global query_results
        query_results = fuzzy_process.extractOne(query, names, scorer=scorer)
        return True
    except:
        return False

def fn_get_nlp(syns, names):
    try:
        global nlp_results
        nlp_results=[fuzzy_process.extractOne(syn, names, scorer=fuzz.ratio) for syn in syns]
        return True
    except:
        return False
    
#wiki_results = None
def fn_get_wiki(query, names):
    try:
        global wiki_results
        header = wiki.get_top_headers(query, 1)[0]
        wiki_results = fuzzy_process.extractOne(header, names, scorer=fuzz.ratio)
        #sleep(0.1)
        return True
    except:
        return False

#pubmed_results = None
def fn_get_pubmed(query, names):
    try:
        global pubmed_results
        string = pubmed.get(query, topK=1)

        if string is not None:
            string = string[0]
            pubmed_results = fuzzy_process.extractOne(string, names, scorer=fuzz.partial_ratio)
            return True
        else:
            return False
    except:
        return False

from graphviz import Digraph
from src_tree.best_vertex import check_parent
def plot(doid,ontology):
    dot = Digraph(comment='Neighborhood')
    term_doid = ontology.get_term(doid)
    label_doid = term_doid.name
    dot.node('A', label_doid)
    letter = 'A'
    if check_parent(doid,ontology) > 0:
        dict = {term.name: term.id for term in ontology.get_terms()}
        father = dict[term_doid.relationships[0][2]]
        term_father = ontology.get_term(father)
        label_father = term_father.name
        letter = 'B'
        dot.node(letter, label_father)
        dot.edges([''.join(['B','A'])])
    children = [term.id for term in ontology.get_terms() if len(term.relationships) > 0 and term.relationships[0][1] == doid]
    #print children
    if len(children) > 0:
        for child in children:
            term_child = ontology.get_term(child)
            label_child = term_child.name
            
            letter = chr(ord(letter) + 1)
            dot.node(letter, label_child)
            dot.edges([''.join(['A',letter])])
    return dot

def find_answer(query, ontology, model_trigram, model_doc2vec):
    '''
    OUTPUTS:
        flag -- bool, exact match or not
        res -- list of [name, doid], if flag==True
            -- string if flag == False
        graph
    '''
    
    query = query.lower()
    
    # ontology dictionaries
    name2doid = {term.name: term.id for term in ontology.get_terms()}
    names = name2doid.keys()
    doid2name = {term.id: term.name for term in ontology.get_terms()}
    
    ## exact match
    if query in name2doid.keys():
        doid = name2doid[query]
        flag = True
    else:
        flag = False # no exact match
        
        th_get_q = Thread(target = fn_get_q, args = (query,names,))
        th_get_wiki = Thread(target = fn_get_wiki, args = (query,names,))
        th_get_pubmed = Thread(target = fn_get_pubmed, args = (query,names,))

        th_get_q.start()
        th_get_wiki.start()
        th_get_pubmed.start()

        # TODO: 
        doids = set()
        doid_exact_results = search_doid(query, False, doids)
        doids = [d for d in doids if d in doid2name.keys()]
        
        # Thread for NLP
        synonyms_nlp = nlp.synonyms(query, model_trigram)
        th_get_nlp = Thread(target=fn_get_nlp, args=(synonyms_nlp, names,))
        th_get_nlp.start()
        
        # TODO: find_best_vertex
        # Tree search
        best_vertex = find_best_vertex(doids,ontology)
        doid = best_vertex
        confidence = None
        
        th_get_q.join()
        th_get_wiki.join()
        th_get_pubmed.join()
        th_get_nlp.join()

        
        results = [query_results] + [wiki_results] + [pubmed_results] + nlp_results

        d_len = len(doids)
        doids = doids + [name2doid[tup[0]] for tup in results]
        prob = np.array([tup[1] for tup in results])
        prob = np.concatenate((np.ones(d_len)*prob.mean(), prob))
        
        # TODO: tree search
        doid = doids[prob.argmax()]
        confidence = prob.max()
        

    dot = plot(doid,ontology)
    print dot
    dot.format='png'
    graph = dot.render('test-output/round-table.gv', view=False)
    
    if flag:
        res = [doid2name[doid], doid]
    else:
        res = ("Query: {:}\n".format(query) + 
               "Name: {:}\n".format(doid2name[doid]) + 
               "# {:}\n".format(doid) + 
               "Confidence: {:}%\n".format(confidence))
    return flag, res, graph

