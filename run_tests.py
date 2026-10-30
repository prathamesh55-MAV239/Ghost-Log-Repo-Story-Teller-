import traceback, sys

# Import the test module (it resides in the same directory)
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('test_ghost_story', r'C:\Users\Prathamesh\Downloads\ghostlog\test_ghost_story.py')
test_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_module)

# Gather all callables that start with 'test_'
functions = [getattr(test_module, name) for name in dir(test_module) if name.startswith('test_')]

failed = 0
for func in functions:
    try:
        func()
        print(f"PASS {func.__name__}")
    except Exception as e:
        failed += 1
        print(f"FAIL {func.__name__}: {e}")
        traceback.print_exc()

if failed:
    sys.exit(1)
else:
    sys.exit(0)

