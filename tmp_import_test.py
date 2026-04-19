import sys, os, json
print('cwd:', os.getcwd())
print('sys.path first entries:', sys.path[:5])
try:
    import steps
    print('steps imported, has attr steps:', hasattr(steps, 'steps'))
except Exception as e:
    print('Import error:', e)
