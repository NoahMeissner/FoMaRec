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


def init_model():
    device = torch.device('cpu')
    model = AutoModel.from_pretrained(
        "answerdotai/ModernBERT-base",
        torch_dtype=torch.float32,  
        trust_remote_code=False,
        local_files_only=False
    )
    model.to(device)
    model.eval()  
    return model

def init_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(
        "answerdotai/ModernBERT-base",
        trust_remote_code=False,
        local_files_only=False
    )
    return tokenizer


class Embedder:

    def __init__(self):
        
        torch.set_num_threads(1)
        
        if torch.backends.mps.is_available():
            torch.backends.mps.is_built = lambda: False
        
        try:
            self.tokenizer = init_tokenizer()
            
            self.model = init_model()
            
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

    def create_embedding(self, text):
        """Get embeddings with better handling"""
        try:
            if not text or len(text.strip()) < 2:
                return np.zeros(768)
            
            # Tokenizer Parallelisierung deaktivieren
            inputs = self.tokenizer(
                text, 
                return_tensors='pt', 
                truncation=True, 
                padding=True, 
                max_length=512,
                add_special_tokens=True
            )
            
            # Explizit auf CPU setzen
            inputs = {k: v.to('cpu') for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Use mean pooling
            attention_mask = inputs['attention_mask']
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            mean_embeddings = sum_embeddings / sum_mask
            
            result = mean_embeddings.squeeze().numpy()
            
            # Speicher freigeben
            del inputs, outputs, token_embeddings, input_mask_expanded, sum_embeddings, sum_mask, mean_embeddings
            gc.collect()
            
            return result
            
        except Exception as e:
            print(f"Error in create_embedding: {e}")
            return np.zeros(768)

    def get_embedding(self, text):
        try:
            normalized_text = self.advanced_normalize(text)
            return self.create_embedding(normalized_text)
        except Exception as e:
            print(f"Error in get_embedding: {e}")
            return np.zeros(768)


