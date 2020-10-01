settings = {
    'general': {
        'verbose': True,
        'seed': 43,
        'settings_priority': True,
        'early_validation': False,
        'conserve_memery': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'cool_project': {
        'cool_project_workers': ['parser', 'munger'],
        'cool_project_design': 'pipeline',
        'workflow': 'editor'},
    'parser': {
        'parser_design': 'compare',
        'parser_steps': ['divide'],
        'divide_techniques': ['slice', 'dice'],
        'random_attribute': True},
    'munger': {
        'munger_steps': ['search', 'destroy'],
        'search_techniques': ['find', 'locate'],
        'destroy_techniques': ['explode', 'annihilate']},
    'divide_parameters': {'replace_strings': True}}