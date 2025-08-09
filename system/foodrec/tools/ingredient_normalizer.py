# Noah Meißner 11.06.2025

"""
    This script is responsible for the comparison of the different ingredient_embeddings
"""

from foodrec.data.load_ingredient_embeddings import EmbeddingLoader
from foodrec.utils.data_preperation.embedder import Embedder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random
from difflib import SequenceMatcher
from collections import defaultdict


def calculate_edit_distance_normalized(s1, s2):
    """Calculate normalized edit distance using basic implementation"""
    if not s1 or not s2:
        return 0.0
    
    # Simple Levenshtein distance implementation
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


def calculate_jaro_winkler(s1, s2):
    """Simple Jaro-Winkler similarity implementation"""
    if not s1 or not s2:
        return 0.0
    return SequenceMatcher(None, s1, s2).ratio()

def fuzzy_match_score(s1, s2):
    """Enhanced fuzzy matching with multiple metrics"""
    if not s1 or not s2:
        return 0.0
    
    # Multiple similarity metrics
    sequence_match = SequenceMatcher(None, s1, s2).ratio()
    edit_distance = calculate_edit_distance_normalized(s1, s2)
    jaro_winkler = calculate_jaro_winkler(s1, s2)
    
    # Combine metrics with weights
    combined_score = (
        0.4 * sequence_match +
        0.3 * edit_distance +
        0.3 * jaro_winkler
    )
    
    return combined_score

def partial_match_score(query, term):
    """Calculate partial matching score for compound words"""
    query_words = set(query.split())
    term_words = set(term.split())
    
    if not query_words or not term_words:
        return 0.0
    
    # Check for exact word matches
    exact_matches = len(query_words & term_words)
    
    # Check for partial word matches
    partial_matches = 0
    for q_word in query_words:
        for t_word in term_words:
            if len(q_word) > 3 and len(t_word) > 3:
                if q_word in t_word or t_word in q_word:
                    partial_matches += 0.5
                elif fuzzy_match_score(q_word, t_word) > 0.8:
                    partial_matches += 0.3
    
    total_score = (exact_matches + partial_matches) / max(len(query_words), len(term_words))
    return min(total_score, 1.0)

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


class IngredientNormalisation:

    def __init__(self, dataset_name):
        EL = EmbeddingLoader(dataset_name)
        self.dataset = EL.get_embeddings()
        self.embedder = Embedder()

    def advanced_hybrid_search(self, query, top_k=5):
        """Advanced hybrid search with multiple strategies"""
        query_normalized = self.embedder.advanced_normalize(query)
        
        # Extract data from dataset first
        english_terms = [value[0] for value in self.dataset]
        embeddings = []
        for value in self.dataset:
            if isinstance(value[1], str):
                # Convert string representation back to numpy array
                embedding = np.fromstring(value[1].strip('[]'), sep=',')
            else:
                embedding = value[1]
            embeddings.append(embedding)
        
        # Now create the ngram index
        ngram_index = create_ngram_index(english_terms)
        
        # Strategy 1: Exact match
        if query_normalized in english_terms:
            exact_idx = english_terms.index(query_normalized)
            return [english_terms[exact_idx], 1.0, 1.0, 1.0, 1.0]
        
        # Strategy 2: Get candidates using n-gram index for efficiency
        candidates = get_ngram_candidates(query_normalized, ngram_index, english_terms)
        
        # Strategy 3: Semantic similarity for candidates
        query_emb = self.embedder.get_embedding(query_normalized).reshape(1, -1)
        
        results = []
        for idx in candidates:
            if idx < len(embeddings):
                term = english_terms[idx]
                
                # Calculate semantic similarity
                term_emb = embeddings[idx].reshape(1, -1)
                semantic_score = cosine_similarity(query_emb, term_emb)[0][0]
                
                # Calculate fuzzy similarity
                fuzzy_score = fuzzy_match_score(query_normalized, term)
                
                # Calculate partial match score
                partial_score = partial_match_score(query_normalized, term)
                
                # Calculate length penalty (prefer similar length terms)
                len_penalty = 1.0 - abs(len(query_normalized) - len(term)) / max(len(query_normalized), len(term), 1)
                
                # Combine scores with dynamic weights
                if partial_score > 0.5:  # Strong partial match
                    combined_score = 0.4 * semantic_score + 0.3 * fuzzy_score + 0.2 * partial_score + 0.1 * len_penalty
                else:  # Rely more on semantic and fuzzy
                    combined_score = 0.5 * semantic_score + 0.4 * fuzzy_score + 0.05 * partial_score + 0.05 * len_penalty
                
                results.append([term, combined_score, semantic_score, fuzzy_score, partial_score])
        
        # Sort by combined score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[0]


  


