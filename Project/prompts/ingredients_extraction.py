prompt_ingredients = '''
    You are a classification system, to classify Ingredients with following labels
    Labels = ["Number","Units","Ingredients","Type"]
    you should classify following ingredients
    Ingredients = {$DATA$}
    Here are a few examples:
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
    OutputFormat:
    [
        {'LINEOFText':{entities:[(SEQUENCE1,LABEL),(SEQUENCE2,LABEL)]}},
        {'LINEOFText':{entities:[(SEQUENCE1,LABEL),(SEQUENCE2,LABEL)]}},
    ]
    PLEASE RESPOND ONLY IN THE OUPTPUTFORMAT!
    USE STRICT THE RULES ABOVE!
'''