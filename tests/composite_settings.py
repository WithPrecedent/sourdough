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
        'cool_project_role': 'obey'},
    'parser': {
        'parser_role': 'study',
        'parser_tasks': ['divide'],
        'divide_techniques': ['slice', 'dice']},
    'munger': {
        'munger_tasks': ['search', 'destroy'],
        'search_techniques': ['find', 'locate'],
        'destroy_techniques': ['explode', 'annihilate']},
    'divide_parameters': {'replace_strings': True}}