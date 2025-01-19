import importlib
import pkgutil

from aiogram import Router


routers = []

for module_info in pkgutil.iter_modules(__path__):
    module_name = module_info.name
    module = importlib.import_module(f"{__name__}.{module_name}")

    if hasattr(module, "router") and isinstance(getattr(module, "router"), Router):
        routers.append(module.router)
