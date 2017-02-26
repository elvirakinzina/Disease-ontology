import numpy as np
import re
import urllib2

import wikipedia

def get_links_from_ontology(ontology):
    '''Given ontology, extract all wikipedia links from terms descriptions'''
    
    lst = [[m.start() for m in re.finditer(r'http\\://en.wikipedia', term.definition)] 
           for term in ontology.get_terms()]
    req = re.compile(r',|]')
    lst = [[term.definition[pos:pos+req.search(term.definition[pos:]).start()] 
            for pos in lst[i] if 'wikipedia' in term.definition[pos:]] 
           for i, term in enumerate(ontology.get_terms())]
    lst = [l for sublist in lst for l in sublist if len(l) > 0]
    lst = ['http://en.wikipedia.' + l[len('http\\://en.wikipedia')+1:] for l in lst]
    lst = np.unique(lst)
    
    return list(lst)

def get_html(addr):
    '''Get html page by address'''
    
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    
    infile = opener.open(addr)
    page = infile.read()
    
    return page

def get_top_headers(query, topK=1):
    '''Get top wikipedia headers by query'''
    
    top = wikipedia.search(query, results=topK,suggestion=True)
    if len(top[0]) == 0:
        if top[1] is not None:
            top = wikipedia.search(top[1], results=topK)
        else:
            # nothing was found
            return None
    else:
        top = top[0]
    
    return top



