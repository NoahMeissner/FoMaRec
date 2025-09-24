# Noah Meissner 11.06.2025

import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from transformers import AutoTokenizer, AutoModel
import re
import numpy as np
import torch
import gc

'''
    This class is responsible to translate ingredient_strings in embeddings, as part of the ingredient_normalization process
'''


def init_lemmatizer():
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    return WordNetLemmatizer()

class Embedder:

    def __init__(self):                
        try:            
            self.lemmatizer = init_lemmatizer()
            
            gc.collect()
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    def advanced_normalize(self, text):
        """Advanced normalization with better compound word handling"""
        try:
            text = text.lower()
            
            text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
            
            text = re.sub(r'([a-z])(sauce|cream|oil|salt|paste|syrup|juice|milk|herb|nut|cheese|meat|fish|spice)', r'\1 \2', text)
            text = re.sub(r'(sauce|cream|oil|salt|paste|syrup|juice|milk|herb|nut|cheese|meat|fish|spice)([a-z])', r'\1 \2', text)
            
            # Replace common separators with spaces
            text = re.sub(r'[_\-\.]+', ' ', text)
            
            # Remove special characters but keep spaces
            text = re.sub(r'[^a-z\s]', '', text)
            
            # Normalize whitespace
            text = ' '.join(text.split())
            
            # Lemmatize words
            words = text.split()
            lemmatized_words = []
            for word in words:
                if len(word) > 2:
                    lemmatized_words.append(self.lemmatizer.lemmatize(word))
                else:
                    lemmatized_words.append(word)
            
            return ' '.join(lemmatized_words)
            
        except Exception as e:
            print(f"Error in advanced_normalize: {e}")
            return text