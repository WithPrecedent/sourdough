settings = {
    'general': {
        'verbose': True,
        'seed': 43,
        'settings_priority': True,
        'early_validation': False,
        'conserve_memery': False,
        'parallelize': True},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'cool_project': {
        'cool_project_creators': ['parser', 'munger'],
        'cool_project_structure': 'graph'},
    'parser': {
        'parser_design': 'contest',
        'parser_steps': ['divide', 'extract'],
        'divide_techniques': ['slice', 'dice'],
        'extract_techniques': ['harvest', 'process', 'something'],
        'random_thing': True},
    'munger': {
        'munger_design': 'survey',
        'munger_steps': ['search', 'destroy'],
        'search_techniques': ['find', 'locate'],
        'destroy_techniques': ['explode', 'annihilate']},
    'divide_parameters': {'replace_strings': True}}
