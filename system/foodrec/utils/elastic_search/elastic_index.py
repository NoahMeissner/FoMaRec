import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
from typing import List, Dict, Any, Tuple
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Indexer:
    """
    Indexer class for storing recipe data in Elasticsearch with validation
    """
    
    def __init__(self, ls_data: List[Dict[str, Any]], es_client: Elasticsearch = None, index_name: str = "recipes"):
        """
        Initialize the indexer
        
        Args:
            ls_data: List of recipe dictionaries
            es_client: Elasticsearch client instance
            index_name: Name of the index to write to
        """
        self.data = ls_data
        self.es = es_client
        self.index_name = index_name
    
    
    
    
    
    def _prepare_document(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a single recipe document for indexing
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            Dict: Prepared document
        """
        doc = {}
        
        # Copy all fields from the recipe
        for field in ['id', 'title', 'rating', 'views', 'rate_average', 'person_number',
                     'tutorial', 'difficulty', 'cooking_time', 'price_category',
                     'kcal', 'protein', 'carbohydrates', 'fat', 'recipe_href', 'cuisine']:
            if field in recipe and recipe[field] is not None:
                doc[field] = recipe[field]
        
        # Handle ingredients - convert list to string for text search
        if 'ingredients' in recipe and recipe['ingredients']:
            if isinstance(recipe['ingredients'], list):
                doc['ingredients'] = ' '.join(str(ing) for ing in recipe['ingredients'])
            else:
                doc['ingredients'] = str(recipe['ingredients'])
        
        # Handle embeddings
        if 'embeddings' in recipe and recipe['embeddings'] is not None:
            embeddings = recipe['embeddings']
            if isinstance(embeddings, list):
                doc['embeddings'] = embeddings
            elif isinstance(embeddings, np.ndarray):
                doc['embeddings'] = embeddings.tolist()
        
        # Generate feature embeddings from numerical features
        doc['feature_embeddings'] = self._generate_feature_embeddings(recipe)
        
        return doc
    
    def _generate_feature_embeddings(self, recipe: Dict[str, Any]) -> List[float]:
        """
        Generate feature embeddings from numerical recipe features
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            List[float]: 5-dimensional feature vector
        """
        features = []
        
        # Normalize features to 0-1 range (approximate)
        features.append(min(recipe.get('rating', 3.0) / 5.0, 1.0))  # Rating (0-5)
        features.append(min(recipe.get('cooking_time', 30) / 120.0, 1.0))  # Cooking time (0-120 min)
        features.append(min(recipe.get('kcal', 400) / 800.0, 1.0))  # Calories (0-800)
        features.append(min(recipe.get('protein', 10) / 50.0, 1.0))  # Protein (0-50g)
        features.append(min(recipe.get('person_number', 2) / 8.0, 1.0))  # Person number (0-8)
        
        return features
    
    def index_data(self, batch_size: int = 100, validate_first: bool = True, use_only_valid: bool = True) -> bool:
        """
        Index recipe data into Elasticsearch
        
        Args:
            batch_size: Number of documents to index per batch
            validate_first: Whether to validate data before indexing
            use_only_valid: Whether to use only valid data for indexing
            
        Returns:
            bool: True if indexing was successful
        """
        try:
            
            data_to_index = self.data
            
            if len(data_to_index) == 0:
                logger.error("No valid data to index")
                return False
            
            logger.info(f"Starting to index {len(data_to_index)} recipes")
            
            # Prepare documents for bulk indexing
            def generate_docs():
                for recipe in data_to_index:
                    try:
                        doc = self._prepare_document(recipe)
                        yield {
                            "_index": self.index_name,
                            "_id": recipe['id'],
                            "_source": doc
                        }
                    except Exception as e:
                        logger.error(f"Error preparing document for recipe {recipe.get('id', 'UNKNOWN')}: {str(e)}")
                        continue
            
            # Bulk index documents
            success_count = 0
            error_count = 0
            for success, info in bulk(self.es, generate_docs(), chunk_size=batch_size):
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    logger.error(f"Failed to index document: {info}")
            
            logger.info(f"Successfully indexed {success_count} recipes, {error_count} failed")
            
            # Refresh index to make documents searchable
            self.es.indices.refresh(index=self.index_name)
            
            return error_count == 0
            
        except Exception as e:
            logger.error(f"Error indexing data: {str(e)}")
            return False
    
    def index_single_recipe(self, recipe: Dict[str, Any], validate_first: bool = True) -> bool:
        """
        Index a single recipe
        
        Args:
            recipe: Recipe dictionary
            validate_first: Whether to validate the recipe first
            
        Returns:
            bool: True if indexing was successful
        """
        try:
            if validate_first:
                is_valid, errors = self._validate_recipe(recipe, 0)
                if not is_valid:
                    logger.error(f"Recipe validation failed: {'; '.join(errors)}")
                    return False
            
            doc = self._prepare_document(recipe)
            result = self.es.index(
                index=self.index_name,
                id=recipe['id'],
                body=doc
            )
            logger.info(f"Indexed recipe {recipe['id']}: {result['result']}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing single recipe: {str(e)}")
            return False