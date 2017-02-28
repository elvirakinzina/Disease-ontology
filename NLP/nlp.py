from gensim.models import word2vec, doc2vec

def query_to_words(query):
    return query.lower().split()

def synonyms(query, model_trigram):
    word = ''
    words = query_to_words(query)
    for w in words:
        word += (w+'_')
    word = word[:-1]
    try:
        syns = model_trigram.similar_by_word(word, topn=3)
    except:
        return []
    syns = [syn[0].replace('_', ' ') for syn in syns]
    return syns

def distance(query1, query2, model_doc2vec):
    
    doc1 = query_to_words(query1)
    doc2 = query_to_words(query2)
    sim = model_doc2vec.n_similarity(doc1, doc2)
    return sim

