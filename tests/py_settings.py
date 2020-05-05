settings = {
    'general': {'verbose': True, 'seed': 43},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252'},
    'project': {
        'project_workers': ['parser', 'munger']},
    'parser': {
        'parser_steps': 'divide',
        'divide_techniques': ['slice', 'dice']},
    'divide_parameters': {'replace_strings': True}}