# Noah Meissner 14.08.2025

def is_ketogenic(protein_g, carbs_g, fat_g, calories):
    """
    Determine if a recipe is ketogenic.
    
    Parameters:
        protein_g (float): grams of protein
        carbs_g (float): grams of carbohydrates
        fat_g (float): grams of fat
        calories (float): total calories of the recipe

    Returns:
        bool: True if ketogenic, False otherwise
    """
    
    # Convert macros to kcal
    protein_kcal = protein_g * 4
    carbs_kcal = carbs_g * 4
    fat_kcal = fat_g * 9
    
    # Safety check: use provided calories if not matching calculated
    if calories <= 0:
        calories = protein_kcal + carbs_kcal + fat_kcal
    
    # Percentages
    fat_pct = (fat_kcal / calories) * 100
    protein_pct = (protein_kcal / calories) * 100
    carb_pct = (carbs_kcal / calories) * 100
    
    # Ketogenic ratio (classic formula)
    keto_ratio = fat_g / (protein_g + carbs_g) if (protein_g + carbs_g) > 0 else float('inf')
    
    # Criteria:
    # - Carbs should be low: <10% of calories or <20g absolute
    # - Fat should be high: >= 70% of calories
    # - Ketogenic ratio should be >= 2:1
    if (carb_pct <= 10 or carbs_g <= 20) and fat_pct >= 70 and keto_ratio >= 2:
        return True
    else:
        return False
