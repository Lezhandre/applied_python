import importlib

all_routers = [getattr(importlib.import_module(module_name, __name__), 'router')
               for module_name in ('.statistics_', '.model_', '.helper_')]
