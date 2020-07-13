settings = {
    'general': {'verbose': True, 'seed': 43},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'project': {
        'project_steps': ['parser', 'munger'],
        'project_design': 'chainer'},
    'parser': {
        'parser_steps': ['divider'],
        'parser_design': 'comparative',
        'divider_techniques': ['slice', 'dice']},
    'munger': {
        'munger_steps': ['searcher', 'destroyer'],
        'searcher_techniques': ['find', 'locate'],
        'destroyer_techniques': ['explode', 'annihilate']},
    'divider_parameters': {'replace_strings': True}}