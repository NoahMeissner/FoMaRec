# 11.06.2025 @Noah Meissner

"""
This functions clean the ingredients before sending them to the api
"""

import re

def clean_ingredient(text):
    text = re.sub(r'\d+\s*%', '', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'tl', '', text)
    text = re.sub(r'tk', '', text)
    text = re.sub(r'[^a-zA-ZäöüÄÖÜß\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def split_multiple_ingredients(item):
    stopwords = ['und', 'oder', 'als',',', 'für', 'bzw','ohne','frische','frisch','kräftiger']
    pattern = r'(?:(?<=\s)(' + '|'.join(stopwords) + r')(?=\s)|(?<=\s)(' + '|'.join(stopwords) + r')|(' + '|'.join(stopwords) + r')(?=\s)|,)'

    parts = re.split(pattern, item)
    buffer = []
    for part in parts:
        if part is None:
            continue
        p = part.strip()
        if p.lower() == 'und':
            buffer.append('&')
        elif p.lower() == 'oder':
            buffer.append('|')
        elif p.lower() == 'ohne':
            buffer.append('(WITHOUT)')
        elif p.lower() in stopwords or p == ',':
            continue
        elif p:
            buffer.append(p)
    return (' '.join(buffer))

def find_obvious_spices(item):
    spices = ['salz', 'pfeffer', 'zucker', 'zimt', 'majoran']
    pattern = r'(' + '|'.join(spices) + r')'
    found = re.findall(pattern, item, re.IGNORECASE)
    cleaned = re.sub(pattern, '', item, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return {
        'original': item,
        'cleaned': cleaned,
        'spices': list({f.lower() for f in found})
    }

def clean(item):
    cleaned_ing = clean_ingredient(item)
    multiple_ing = split_multiple_ingredients(cleaned_ing)
    return find_obvious_spices(multiple_ing)