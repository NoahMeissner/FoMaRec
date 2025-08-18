# Noah Meissner 14.08.2025

def calc_keto_ratio(protein_g, carbs_g, fat_g):            
    # Ketogenic ratio (classic formula)
    return fat_g / (protein_g + carbs_g) if (protein_g + carbs_g) > 0 else float('inf')



def is_ketogenic(protein_g, carbs_g, fat_g, calories, keto_ratio_index = 0.8):
    """
    Determine if a recipe is ketogenic.
    """
    # Convert macros to kcal
    keto_ratio = calc_keto_ratio(protein_g, carbs_g, fat_g)
    # Criteria:
    if keto_ratio >= keto_ratio_index: # (carb_pct <= 10 or carbs_g <= 20) and fat_pct >= 70 and 
        return True
    else:
        return False

def explain_ketogenic(protein_g, carbs_g, fat_g, calories, keto_ratio_index= 0.8):
    """
    Print nutrition breakdown and ketogenic evaluation details.
    """
    # Convert macros to kcal
    protein_kcal = protein_g * 4
    carbs_kcal = carbs_g * 4
    fat_kcal = fat_g * 9
    
    # Safety check: recalc calories if <= 0
    if calories <= 0:
        calories = protein_kcal + carbs_kcal + fat_kcal
    
    if calories == 0:
        print("⚠️ Keine Kalorien vorhanden – keine Auswertung möglich.")
        return
    
    # Percentages
    fat_pct = (fat_kcal / calories) * 100
    protein_pct = (protein_kcal / calories) * 100
    carb_pct = (carbs_kcal / calories) * 100
    
    # Ratio
    keto_ratio = calc_keto_ratio(protein_g, carbs_g, fat_g)

    
    # Print breakdown
    print("===== Rezept-Analyse =====")
    print(f"Protein: {protein_g:.1f} g  ({protein_kcal:.1f} kcal, {protein_pct:.1f}%)")
    print(f"Fett:    {fat_g:.1f} g  ({fat_kcal:.1f} kcal, {fat_pct:.1f}%)")
    print(f"Kohlenh.: {carbs_g:.1f} g  ({carbs_kcal:.1f} kcal, {carb_pct:.1f}%)")
    print(f"Kalorien gesamt: {calories:.1f} kcal")
    print(f"Ketogenic Ratio (Fett : Protein+Carbs) = {keto_ratio:.2f} : 1")
    
    # Kriterien prüfen
    ketogenic = keto_ratio >= keto_ratio_index
    
    print("Ergebnis:", "✅ Ketogen" if ketogenic else "❌ Nicht ketogen")
    print("==========================\n")
