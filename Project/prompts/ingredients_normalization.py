prompt_ingredients_normalization = '''
    You are a normalization system, to classify Ingredients to their normal ingredients
    you should classify following ingredients
    Ingredients = {$DATA$}
    Here are a few examples:
    Example 1
    haselnusskrokant -> ('haselnusskrokant':'haselnuss'),
    Example 2
    tk-pizza -> ('tk-pizza':'pizza'),
    Example 3
    rot-schwarzesjohannisbeergelee - > ('rot-schwarzesjohannisbeergelee':'johannisbeergelee')
    Example 4
    schweinesteks -> ('schweinesteks':'schweinesteks')
    Example 5
    oliveöl -> ('oliveöl','olivenöl')
    OutputFormat:
    [
    {'LINEOFText':'Normalization'},
    {'LINEOFText':'Normalization'},
    ]
    PLEASE RESPOND ONLY IN THE OUPTPUTFORMAT!
    NORMALIZE TO THE BASE INGREDIENT,
    DO NOT RETURN THE EXAMPLES
    DO NOT USE ACCENTS IN THE NORMALIZATION
    USE STRICT THE RULES ABOVE!
'''