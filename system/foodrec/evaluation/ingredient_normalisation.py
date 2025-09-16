
# Noah Meissner 11.06.2025

import pandas as pd
import numpy as np
import random
from foodrec.data.load_ingredient_embeddings import EmbeddingLoader
from typing import List, Tuple, Dict, Any
from collections import defaultdict
from foodrec.utils.data_preperation.embedder import Embedder
from foodrec.config.structure.dataset_enum import DatasetEnum

# Import the IngredientNormalisation class from the first file
from foodrec.tools.ingredient_normalizer import IngredientNormalisation



class TestCaseGenerator:
    """Generate comprehensive test cases for evaluation"""
    
    def __init__(self, english_terms: List[str], embeddings):
        self.english_terms = english_terms
        self.embeddings = embeddings
        self.test_cases = []
        
        
    def generate_test_cases_for_term(self, term: str, n_per_type: int = 2) -> List[Tuple[str, str, str]]:
        """Generate multiple test cases for a single term"""
        test_cases = []
        
        # Character swap typos
        for _ in range(n_per_type):
            variation = self.introduce_typo(term)
            if variation != term:
                test_cases.append((term, variation, "typo_swap"))
        
        # Character drop
        for _ in range(n_per_type):
            variation = self.drop_random_char(term)
            if variation != term:
                test_cases.append((term, variation, "char_drop"))
        
        # Character addition
        for _ in range(n_per_type):
            variation = self.add_random_char(term)
            if variation != term:
                test_cases.append((term, variation, "char_add"))
        
        # Character substitution
        for _ in range(n_per_type):
            variation = self.substitute_char(term)
            if variation != term:
                test_cases.append((term, variation, "char_sub"))
                        
        return test_cases
    
    def generate_comprehensive_test_set(self, n_per_type: int = 1) -> List[Tuple[str, str, str]]:
        """Generate comprehensive test set for all terms"""
        all_test_cases = []
        
        print(f"Generating test cases for {len(self.english_terms)} terms...")
        
        for i, term in enumerate(self.english_terms):
            if i % 50 == 0:
                print(f"Processing term {i+1}/{len(self.english_terms)}: {term}")
            
            term_cases = self.generate_test_cases_for_term(term, n_per_type)
            all_test_cases.extend(term_cases)
        
        print(f"Generated {len(all_test_cases)} test cases total")
        return all_test_cases
    
    def get_random_sample(self, test_cases: List[Tuple[str, str, str]], 
                         sample_size: int = None, 
                         percentage: float = None) -> List[Tuple[str, str, str]]:
        """
        Get a random sample of test cases
        
        Args:
            test_cases: List of test cases
            sample_size: Exact number of test cases to return
            percentage: Percentage of test cases to return (0.0 to 1.0)
        
        Returns:
            Random sample of test cases
        """
        if sample_size is None and percentage is None:
            raise ValueError("Either sample_size or percentage must be specified")
        
        if sample_size is not None and percentage is not None:
            raise ValueError("Specify either sample_size or percentage, not both")
        
        if percentage is not None:
            if not 0.0 <= percentage <= 1.0:
                raise ValueError("Percentage must be between 0.0 and 1.0")
            sample_size = int(len(test_cases) * percentage)
        
        if sample_size > len(test_cases):
            print(f"Warning: Sample size ({sample_size}) is larger than total test cases ({len(test_cases)})")
            return test_cases.copy()
        
        return random.sample(test_cases, sample_size)
    
    def get_stratified_sample(self, test_cases: List[Tuple[str, str, str]], 
                             sample_size: int = None, 
                             percentage: float = None) -> List[Tuple[str, str, str]]:
        """
        Get a stratified random sample that maintains the distribution of test types
        
        Args:
            test_cases: List of test cases
            sample_size: Exact number of test cases to return
            percentage: Percentage of test cases to return (0.0 to 1.0)
        
        Returns:
            Stratified random sample of test cases
        """
        if sample_size is None and percentage is None:
            raise ValueError("Either sample_size or percentage must be specified")
        
        if sample_size is not None and percentage is not None:
            raise ValueError("Specify either sample_size or percentage, not both")
        
        if percentage is not None:
            if not 0.0 <= percentage <= 1.0:
                raise ValueError("Percentage must be between 0.0 and 1.0")
            sample_size = int(len(test_cases) * percentage)
        
        # Group test cases by type
        type_groups = {}
        for case in test_cases:
            test_type = case[2]
            if test_type not in type_groups:
                type_groups[test_type] = []
            type_groups[test_type].append(case)
        
        # Calculate samples per type
        stratified_sample = []
        total_cases = len(test_cases)
        
        for test_type, cases in type_groups.items():
            # Calculate how many cases to sample from this type
            type_proportion = len(cases) / total_cases
            type_sample_size = max(1, int(sample_size * type_proportion))
            
            # Don't sample more than available
            type_sample_size = min(type_sample_size, len(cases))
            
            # Sample from this type
            type_sample = random.sample(cases, type_sample_size)
            stratified_sample.extend(type_sample)
        
        # If we have too many, randomly remove some
        if len(stratified_sample) > sample_size:
            stratified_sample = random.sample(stratified_sample, sample_size)
        
        return stratified_sample


class ComprehensiveEvaluator:
    """Comprehensive evaluation system using IngredientNormalisation"""
    
    def __init__(self, english_terms: List[str], dataset_name):
        self.english_terms_original = english_terms
        self.embedder = Embedder()
        # Initialize the IngredientNormalisation system
        self.ingredient_normalizer = IngredientNormalisation(dataset_name)
        print("IngredientNormalisation system initialized!")
    
    def evaluate_test_cases(self, test_cases: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """Evaluate all test cases using IngredientNormalisation"""
        results = {
            'total_cases': len(test_cases),
            'correct_predictions': 0,
            'detailed_results': [],
            'accuracy_by_type': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'score_statistics': {
                'all_scores': [],
                'correct_scores': [],
                'incorrect_scores': []
            }
        }
        
        print(f"Evaluating {len(test_cases)} test cases...")
        
        for i, (original, test_input, test_type) in enumerate(test_cases):
            if i % 100 == 0:
                print(f"Evaluating case {i+1}/{len(test_cases)}")
                        
            # Use IngredientNormalisation for search - this is the key change!
            search_results = self.ingredient_normalizer.advanced_hybrid_search(test_input, top_k=5)
            
            if search_results:
                best_match = ""
                best_score = 0
                try:
                    best_match = search_results[0]
                except (IndexError, TypeError):
                    best_match = ""

                try:
                    best_score = search_results[1]
                except (IndexError, TypeError):
                    best_score = 0
                is_correct = (original == best_match)
                #print(f"{best_match}: {original} : {best_score}")
                if isinstance(best_score, str):
                    try:
                        best_score = float(best_score)
                    except (ValueError, TypeError):
                        best_score = 0.0

                
                if is_correct:
                    results['correct_predictions'] += 1
                    results['score_statistics']['correct_scores'].append(best_score)
                else:
                    results['score_statistics']['incorrect_scores'].append(best_score)
                
                results['score_statistics']['all_scores'].append(best_score)
                
                # Update accuracy by type
                results['accuracy_by_type'][test_type]['total'] += 1
                if is_correct:
                    results['accuracy_by_type'][test_type]['correct'] += 1
                
                # Store detailed result
                detailed_result = {
                    'original': original,
                    'test_input': test_input,
                    'test_type': test_type,
                    'predicted': best_match,
                    'is_correct': is_correct,
                    'score': best_score,
                }
                results['detailed_results'].append(detailed_result)
        
        # Calculate overall accuracy
        results['overall_accuracy'] = results['correct_predictions'] / results['total_cases']
        
        # Calculate accuracy by type
        for test_type in results['accuracy_by_type']:
            type_stats = results['accuracy_by_type'][test_type]
            type_stats['accuracy'] = type_stats['correct'] / type_stats['total'] if type_stats['total'] > 0 else 0
        
        return results
    
    def print_evaluation_summary(self, results: Dict[str, Any]):
        """Print comprehensive evaluation summary"""
        print("\n" + "="*80)
        print("COMPREHENSIVE EVALUATION SUMMARY")
        print("="*80)
        
        print(f"Total test cases: {results['total_cases']}")
        print(f"Correct predictions: {results['correct_predictions']}")
        print(f"Overall accuracy: {results['overall_accuracy']:.2%}")
        
        print("\nACCURACY BY TEST TYPE:")
        print("-" * 40)
        for test_type, stats in results['accuracy_by_type'].items():
            print(f"{test_type:15s}: {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")
        
        print("\nSCORE STATISTICS:")
        print("-" * 40)
        all_scores = results['score_statistics']['all_scores']
        correct_scores = results['score_statistics']['correct_scores']
        incorrect_scores = results['score_statistics']['incorrect_scores']
        
        print(f"Average score (all): {np.mean(all_scores):.3f}")
        print(f"Average score (correct): {np.mean(correct_scores):.3f}")
        print(f"Average score (incorrect): {np.mean(incorrect_scores):.3f}")
        
        print("\nTOP 10 FAILED CASES:")
        print("-" * 40)
        failed_cases = [r for r in results['detailed_results'] if not r['is_correct']]
        failed_cases.sort(key=lambda x: x['score'], reverse=True)  # Sort by score (high score failures are interesting)
        
        for i, case in enumerate(failed_cases[:10]):
            print(f"{i+1:2d}. Original: {case['original']}")
            print(f"    Input: {case['test_input']} (type: {case['test_type']})")
            print(f"    Predicted: {case['predicted']} (score: {case['score']:.3f})")
            print()

    def analyze_failure_patterns(self, results: Dict[str, Any]):
        """Analyze patterns in failures"""
        print("\nFAILURE PATTERN ANALYSIS:")
        print("-" * 40)
        
        failed_cases = [r for r in results['detailed_results'] if not r['is_correct']]
        
        # Group by failure type
        failure_by_type = defaultdict(list)
        for case in failed_cases:
            failure_by_type[case['test_type']].append(case)
        
        for test_type, cases in failure_by_type.items():
            print(f"\n{test_type.upper()} failures ({len(cases)} cases):")
            
            # Show examples
            for case in cases[:3]:  # Show first 3 examples
                print(f"  {case['original']} -> {case['test_input']} predicted as {case['predicted']}")
        
        # Analyze score distribution
        print(f"\nScore distribution of failed cases:")
        scores = [case['score'] for case in failed_cases]
        if scores:
            print(f"  Min: {min(scores):.3f}, Max: {max(scores):.3f}, Mean: {np.mean(scores):.3f}")
            print(f"  High-confidence failures (>0.8): {len([s for s in scores if s > 0.8])}")


def run_comprehensive_evaluation(sample_size: int = None, 
                               sample_percentage: float = None,
                               use_stratified: bool = True, dataset_name = DatasetEnum.ALL_RECIPE):
    """
    Run the complete evaluation pipeline with sampling options
    
    Args:
        sample_size: Fixed number of test cases to use (e.g., 100)
        sample_percentage: Percentage of test cases to use (e.g., 0.1 for 10%)
        use_stratified: Whether to use stratified sampling (recommended)
    """
    print("Starting comprehensive evaluation...")
    
    # Generate test cases
    EL = EmbeddingLoader(dataset_name)
    dataset = EL.get_embeddings()
    english_terms = [value[0] for value in dataset]
    embeddings = [value[1] for value in dataset]
    generator = TestCaseGenerator(english_terms, embeddings)
    all_test_cases = generator.generate_comprehensive_test_set(n_per_type=1)
    
    # Sample test cases if requested
    if sample_size is not None or sample_percentage is not None:
        if use_stratified:
            test_cases = generator.get_stratified_sample(
                all_test_cases, 
                sample_size=sample_size, 
                percentage=sample_percentage
            )
        else:
            test_cases = generator.get_random_sample(
                all_test_cases, 
                sample_size=sample_size, 
                percentage=sample_percentage
            )
    else:
        test_cases = all_test_cases
    
    # Run evaluation using IngredientNormalisation
    evaluator = ComprehensiveEvaluator(english_terms, dataset_name=dataset_name)
    results = evaluator.evaluate_test_cases(test_cases)
    
    # Print results
    evaluator.print_evaluation_summary(results)
    evaluator.analyze_failure_patterns(results)

"""
#from foodrec.evaluation.ingredient_normalisation import run_comprehensive_evaluation

# run_comprehensive_evaluation(sample_percentage=0.2, use_stratified=False)


"""