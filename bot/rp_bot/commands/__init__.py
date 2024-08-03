import os
import importlib

handlers = []

directory = os.path.dirname(__file__)

for filename in os.listdir(directory):
    if filename.endswith("handler.py"):
        module_name = filename[:-3]
        module_path = f".{module_name}"
        module = importlib.import_module(module_path, package="bot.rp_bot.commands")

        handler_class = getattr(module, "CommandHandler", None)
        if handler_class:
            handlers.append(handler_class)
