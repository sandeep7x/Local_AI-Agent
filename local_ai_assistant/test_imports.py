import importlib
import sys
try:
    import transformers
    print('transformers version:', transformers.__version__)
    print('has generation attr:', hasattr(transformers, 'generation'))
    importlib.import_module('transformers.generation')
    print('import transformers.generation: OK')
except Exception as e:
    print('IMPORT ERROR:', e, file=sys.stderr)
    raise
