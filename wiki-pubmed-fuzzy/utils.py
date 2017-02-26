import re
import numpy as np

def find_synonym(s_ref, s):
    s_ref, s = s_ref.lower(), s.lower()
    last = s_ref.find('(' + s + ')')
    if last == -1:
        return None
    
    regex = re.compile('[^a-zA-Z]')
    s = regex.sub('', s)
    n_letters = len(s)
    regex = re.compile('[^a-zA-Z- ]')
    words = re.split(' |-|', regex.sub('', s_ref[:last]))
    
    res = ''
    i = 0
    for word in words[::-1]:
        if len(word) > 0 and word[0] == s[-i-1]: 
            res = word + ' ' + res
            i = i + 1
            if i == n_letters:
                break
    return res

def assym_dist(a, b):
    "Calculates assymetric editor distance between a and b"
    
    n, m = len(a), len(b)

    current_row = range(n+1) 
    zeros = [0]*(n+1)
    res = np.inf
    for i in range(1, m+1):
        previous_row, current_row = current_row, zeros
        for j in range(1,n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
        if current_row[n] < res:
            res = current_row[n]

    return res
