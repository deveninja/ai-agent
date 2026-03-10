import importlib
import pkgutil
import inspect

tool_registry = {}


def load_tools():

    import tools

    for module in pkgutil.iter_modules(tools.__path__):

        module_name = module.name

        module = importlib.import_module(f"tools.{module_name}")

        for name, func in inspect.getmembers(module, inspect.isfunction):

            # ignore private helpers
            if name.startswith("_"):
                continue

            tool_registry[name] = func


# Load tools on startup
load_tools()