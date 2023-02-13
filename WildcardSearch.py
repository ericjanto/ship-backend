import numpy as np
import json

class trieNode:
    def __init__(self):
        self.next = {}
        self.associated_word = None

    def add_term(self, dollar_term, full_term):
        for index, ch in enumerate(dollar_term):
            # if char is not in the trie, add it:
            if not ch in self.next:
                self.next[ch] = trieNode()
            
            self = self.next[ch] # move pointer

        # for last character, associate word with it:
        self.associated_word = full_term

    def is_item(self, item): 
        if self.associated_word is not None and len(item) == 0:
            return True
        first = item[0]  
        str = item[1:]  
        if first in self.next:
            return self.next[first].search(str)
        else:
            return False
    
    def dfs_traversal(self, rotated_query_term, answer):
        if self.associated_word != None:
            answer.add(self.associated_word)
        for node in self.next:
           self.next[node].dfs_traversal((rotated_query_term + node), answer)

        
    # checks if rotated query term is in the tree and finds the beginning node for dfs search 
    def search(self, rotated_query_term):
        i = 0
        checked_term = ""
        for ch in rotated_query_term:
            if ch == "*":
                break 
            if ch in self.next:
                self = self.next[ch]
            else:
                return "NOT FOUND"
            
        answer = set()    
        self.dfs_traversal(rotated_query_term[:-1], answer)
        return answer



def get_all_dollar_terms(term):
    answer = []
    length = len(term)
    for i in range(0, (length+1)):
        if i == length:
            left = ""
        else:
            left = term[i:]
        if i == 0:
            right = ""
        else:
            right = term[:i]

        dollar_term = left + "$" + right

        answer.append(dollar_term) 

    return answer

def create_permuterm_index_trie(terms):
    permuterm_index = trieNode()
    for term in terms:
        dollar_terms = get_all_dollar_terms(term)
        for dt in dollar_terms:
            permuterm_index.add_term(dt, term) 

    return permuterm_index 

def rotate_query_term(query_term):
    length = len(query_term)
    query_term_rotated = query_term + "$"
    i = 0
    while query_term_rotated[-1] != "*":
        if i == length:
            left = ""
        else:
            left = query_term[i:]
        if i == 0:
            right = ""
        else:
            right = query_term[:i]

        query_term_rotated = left + "$" + right

        i += 1

    return query_term_rotated

# leave only the first * and ignore the rest of them
def clean_wildcard_term(query_term):
    query_term = query_term.lower()
    if query_term.count("*") > 1:
        add_wildcard = True
        cleaned_term = ""
        for ch in query_term:
            if ch == "*":
                if add_wildcard:
                    cleaned_term += ch 
                add_wildcard = False
            else:
                cleaned_term += ch

        query_term = cleaned_term

    return query_term
    


