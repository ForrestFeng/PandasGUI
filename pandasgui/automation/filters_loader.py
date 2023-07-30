import os
import importlib.util
import inspect
import pandas as pd
import types

SCRIPT_PRE_FIX = 'pgdf_filter_'

# DataFrame Filter plugin requirements
# 1. Script name must be started with "pgdf_filter"
#   e.g.  pgdf_filter_xxxxxx.py (xxxxx can be anything python file name allowed)
# 2. Script class names must be class XXXFilter()
#   e.g.   class XrsLogFilter()
# 3. Static method defined in XXXFilter class name can be anything, but must accept one arg of type pd.DataFrame
#   e.g.         def ErrorLog(umdf: pd.DataFrame)
# Please check the pgdf_filter_for_xrs_log.py
# 4. Name convention in pgdf_filter file, recommend to use ThisCase


def load_module_from_file(module_path):
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(module_path))[0], module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def find_pgdf_files(directory):
    pgdf_files = []
    for filename in os.listdir(directory):
        if filename.startswith(SCRIPT_PRE_FIX) and filename.endswith('.py'):
            pgdf_files.append(os.path.join(directory, filename))
    return pgdf_files

def find_static_methods_with_fixed_signature(module):
    methods = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            for method_name, method in inspect.getmembers(obj):
                if inspect.isfunction(method) and method.__name__ != "__init__" and len(inspect.signature(method).parameters) == 1:
                    methods.append((obj.__name__, method_name))
    return methods

def run_static_methods(module: types.ModuleType, class_name:str, method_name:str, dataframe: pd.DataFrame):
    method = getattr(getattr(module, class_name), method_name)
    result = method(dataframe)
    print(f"Module:{module.__name__} Class: {class_name}, Method: {method_name}, Result: {result}")
    return result


def find_module_methods(directory):
    pgdf_files = find_pgdf_files(directory)
    module_methods = {}
    for file in pgdf_files:
        module = load_module_from_file(file)
        methods = find_static_methods_with_fixed_signature(module)
        module_methods[module] = methods
    return module_methods

if __name__ == "__main__":
    directory = r"C:\Users\Forrest\Code\py311_pandasgui\PandasGUI\pandasgui\plugins\titanic"  # Replace with the directory containing your pgdf*.py files
    from pandasgui.datasets import titanic

    module_methods = find_module_methods(directory)
    for module, methods in module_methods.items():
        for class_name, method_name in methods:
            run_static_methods(module, class_name, method_name, titanic)
