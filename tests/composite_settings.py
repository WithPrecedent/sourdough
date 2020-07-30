settings = {
    'general': {'verbose': True, 'seed': 43},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'cool_project': {
        'cool_project_workers': ['parser', 'munger'],
        'cool_project_structure': 'progression'},
    'parser': {
        'parser_tasks': ['divide'],
        'parser_structure': 'study',
        'divide_techniques': ['slice', 'dice']},
    'munger': {
        'munger_tasks': ['search', 'destroy'],
        'search_techniques': ['find', 'locate'],
        'destroy_techniques': ['explode', 'annihilate']},
    'divide_parameters': {'replace_strings': True}}