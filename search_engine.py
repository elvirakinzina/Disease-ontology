from gensim.models import word2vec, doc2vec


from threading import Thread
from time import sleep
import numpy as np

from wiki_pubmed_fuzzy.ontology import get_ontology
import fuzzywuzzy.process as fuzzy_process
from fuzzywuzzy import fuzz
from wiki_pubmed_fuzzy import wiki
from wiki_pubmed_fuzzy import pubmed
from src_tree.best_vertex import find_best_vertex

from bot.lookup import search_doid
from NLP import nlp
#from xxx import xxx 

from bot import lookup

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

#
pubmed_results = None
def fn_get_pubmed(query, names):
    global pubmed_results
    string = pubmed.get(query, topK=1)

    if string is not None:
        string = string[0]
        pubmed_results = fuzzy_process.extractOne(string, names, scorer=fuzz.partial_ratio)
        return True
    else:
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

'''main'''
## from bot
query = 'cardiovascular disease'

def find_answer(query, model_trigram, model_doc2vec):
    query = query.lower()
    
    # load ontology
    ontology = get_ontology('data/doid.obo')
    name2doid = {term.name: term.id for term in ontology.get_terms()}
    names = name2doid.keys()
    doid2name = {term.id: term.name for term in ontology.get_terms()}
    
    ## exact match
    if query in name2doid.keys():
        doid = name2doid[query]
        confidence = 100
    else:
        # no exact match
        th_get_q = Thread(target = fn_get_q, args = (query,names,))
        th_get_wiki = Thread(target = fn_get_wiki, args = (query,names,))
        th_get_pubmed = Thread(target = fn_get_pubmed, args = (query,names,))

        th_get_q.start()
        th_get_wiki.start()
        th_get_pubmed.start()


        doids = set()
        doid_exact_results = search_doid(query, False, doids)
        doids = [d for d in doids if d in doid2name.keys()]

        synonyms_nlp = nlp.synonyms(query, model_trigram)

        th_get_nlp = Thread(target=fn_get_nlp, args=(synonyms_nlp, names,))
        th_get_nlp.start()
        

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
        

        doid = doids[prob.argmax()]
        confidence = prob.max()
        

    dot = plot(doid,ontology)
    dot.format='png'
    graph = dot.render('test-output/round-table.gv', view=False)
    
    string = ("Query: {:}\n".format(query) + 
              "Name: {:}\n".format(doid2name[doid]) + 
              "# {:}\n".format(doid) + 
              "Confidence: {:}%\n".format(confidence))
    return string, graph