import sys
try:
    import xxhash
    print('xxhash version:', xxhash.__version__)
    print('has _xxhash module:', hasattr(xxhash, '_xxhash'))
    import importlib
    importlib.import_module('xxhash._xxhash')
    print('import xxhash._xxhash: OK')
except Exception as e:
    print('IMPORT ERROR:', e, file=sys.stderr)
    raise
