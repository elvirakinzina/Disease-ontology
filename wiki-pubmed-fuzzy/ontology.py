from dependencies.scripts.oboparser import parse

def get_ontology(filename):
    '''Load ontology, lower-case name and rename single non-ascii disease'''
    
    ontology = parse(filename, typedefs=['is_a'])
    
    for key in ontology.terms.keys():
        ontology.terms[key].name = ontology.terms[key].name.lower()
        if ontology.terms[key].name.startswith('weissenbacher-zw'):
            ontology.terms[key].name = 'weissenbacher-zweymuller syndrome'
    
    return ontology
