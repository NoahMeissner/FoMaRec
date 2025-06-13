prompt_ingredients = '''
    You are a classification system, to classify Ingredients with following labels
    Labels = ["Number","Units","Ingredients","Type"]
    you should classify following ingredients
    Ingredients = {$DATA$}
    Here are a few examples:
    [{'2 el:petersilie gehackt, salz': {'entities': [['2', 'Number'],
    ['el', 'Units'],
    ['petersilie', 'Ingredients'],
    ['gehackt', 'Type'],
    ['salz', 'Ingredients']]}},
 {'1:knoblauchzehe -  feingewürfelt': {'entities': [['1', 'Number'],
    ['knoblauchzehe', 'Ingredients'],
    ['feingewürfelt', 'Type']]}},
 {'6 große:kartoffeln gegart': {'entities': [['6', 'Number'],
    ['große', 'Type'],
    ['kartoffeln', 'Ingredients'],
    ['gegart', 'Type']]}},
 {'500 gramm:meeresfrüchte   / tk oderfrisch)': {'entities': [['500',
     'Number'],
    ['gramm', 'Units'],
    ['meeresfrüchte', 'Ingredients'],
    ['tk', 'Type'],
    ['frisch', 'Type']]}},
 {'100 gr.:weintraube weiß frisch': {'entities': [['100', 'Number'],
    ['gr', 'Units'],
    ['weintraube', 'Ingredients'],
    ['weiß', 'Type'],
    ['frisch', 'Type']]}}]
    
    OutputFormat:
    [
        {'LINEOFText':{entities:[(SEQUENCE1,LABEL),(SEQUENCE2,LABEL)]}},
        {'LINEOFText':{entities:[(SEQUENCE1,LABEL),(SEQUENCE2,LABEL)]}},
    ]
    PLEASE RESPOND ONLY IN THE OUPTPUTFORMAT!
    USE STRICT THE RULES ABOVE!
'''


"""
1:wirsingkohlkopf -> ('1:wirsingkohlkopf',
     {'entities': [('1', 'Number'),
                   ('wirsingkohlkopf', 'type')]}),
    
    200g:honigmelone frisch,gewürfelt -> ('200g:honigmelone frisch,gewürfelt',
     {'entities': [('200', 'Number'),
                   ('g', 'Units'),
                   ('honigmelone', 'Ingredients'),
                   ('frisch,gewürfelt', 'Type')]}),
    
    250milliliter:fettarme milch -> ('250milliliter:fettarme milch',
     {'entities': [('250', 'Number'),
                   ('milliliter', 'Units'),
                   ('fettarme milch', 'Ingredients')]})
"""