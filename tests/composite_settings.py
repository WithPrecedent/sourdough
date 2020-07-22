settings = {
    'general': {'verbose': True, 'seed': 43},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'cool_project': {
        'cool_project_plan': ['parser', 'munger'],
        'manager_structure': 'chained'},
    'parser': {
        'parser_tasks': ['divider'],
        'parser_structure': 'comparative',
        'divider_techniques': ['slice', 'dice']},
    'munger': {
        'munger_tasks': ['searcher', 'destroyer'],
        'searcher_techniques': ['find', 'locate'],
        'destroyer_techniques': ['explode', 'annihilate']},
    'divider_parameters': {'replace_strings': True}}