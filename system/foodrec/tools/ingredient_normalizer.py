# Noah Meißner 11.06.2025

"""
    This script is responsible for the comparison of the different ingredient_embeddings
"""
import random
from difflib import SequenceMatcher
from collections import defaultdict
from foodrec.utils.data_preperation.embedder import Embedder
from foodrec.data.all_recipe import AllRecipeLoader


def calculate_edit_distance_normalized(s1, s2):
    """Calculate normalized edit distance using basic implementation"""
    if not s1 or not s2:
        return 0.0
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1.0 - (levenshtein_distance(s1, s2) / max_len)

def calc_scores(s1, s2):
    """Enhanced fuzzy matching with multiple metrics"""
    if not s1 or not s2:
        return 0.0
    sequence_match = SequenceMatcher(None, s1, s2).ratio()
    edit_distance = calculate_edit_distance_normalized(s1, s2)
    return [sequence_match, edit_distance]

def create_ngram_index(terms, n=3):
    """Create n-gram index for fast fuzzy matching"""
    ngram_index = defaultdict(set)
    
    for i, term in enumerate(terms):
        # Character n-grams
        for j in range(len(term) - n + 1):
            ngram = term[j:j+n]
            ngram_index[ngram].add(i)
    
    return ngram_index


def get_ngram_candidates(query, ngram_index, terms, n=3, top_k=50):
    """Get candidate terms using n-gram matching"""
    if len(query) < n:
        return list(range(len(terms)))
    
    candidate_scores = defaultdict(int)
    
    # Get n-grams from query
    query_ngrams = [query[i:i+n] for i in range(len(query) - n + 1)]
    
    for ngram in query_ngrams:
        if ngram in ngram_index:
            for term_idx in ngram_index[ngram]:
                candidate_scores[term_idx] += 1
    
    # Sort by n-gram overlap
    sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top candidates plus some random ones for diversity
    top_candidates = [idx for idx, _ in sorted_candidates[:top_k]]
    
    # Add some random candidates if we don't have enough
    if len(top_candidates) < top_k:
        remaining = set(range(len(terms))) - set(top_candidates)
        additional = random.sample(list(remaining), min(top_k - len(top_candidates), len(remaining)))
        top_candidates.extend(additional)
    return top_candidates

def get_all_recipe_dataset():
    AL = AllRecipeLoader()
    dataset = AL.load_training_set()
    return dataset

def get_embeddings():
        dataset = get_all_recipe_dataset()
        english_terms = dataset
        ls = []
        for index in range(0, len(english_terms)):
            ls.append([english_terms[index], english_terms[index]])  
        return ls

class IngredientNormalisation:

    def __init__(self):
        self.dataset = get_embeddings()
        self.embedder = Embedder()
        self.english_terms = [value[0] for value in self.dataset]   
        self.ngram_index = create_ngram_index(self.english_terms)


    def normalize(self, query, more_information = False):
        """Advanced hybrid search with multiple strategies"""
        query_normalized = self.embedder.advanced_normalize(query)
        english_terms =self.english_terms
        ngram_index = self.ngram_index
        if query_normalized in english_terms:
            exact_idx = english_terms.index(query_normalized)
            return [english_terms[exact_idx], 1.0, 1.0, 1.0, 1.0]
        candidates = get_ngram_candidates(query_normalized, ngram_index, english_terms)
        results = []
        ngram_truth = english_terms[candidates[0]]
        for idx in candidates:
                term = english_terms[idx]
                sequence_matcher, edit_distance  = calc_scores(query_normalized, term)     
                results.append([term, sequence_matcher, ngram_truth, edit_distance])
        if more_information:
            return results        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[0]

  


