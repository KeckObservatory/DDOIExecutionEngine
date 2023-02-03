from multiprocessing import Pipe, Process
import importlib
from typing import Callable

class EventExecutor:

    def __init__(self, connection, args, execute = True) -> None:
        self.args = args

        self.pipe = connection

        self.pipe.send("event alive")

        self.TMF = self.import_translator_module_function(args.translator_module_name)


        # TODO: Send messages at each of these steps
        # TODO: figure out the logger
        # TODO: actually fill out the rest of this
        if execute:
            res = self.TMF(args.translator_arguments)
            

    # def import_translator_module_function(self, name) -> Callable:
    #     """Attempts to import the specified Translator Module function and return it

    #     Parameters
    #     ----------
    #     name : str
    #         Import path for the Translator Module function to be imported

    #     Returns
    #     -------
    #     TranslatorModuleFunction
    #         Executable python function for the given function

    #     Raises
    #     ------
    #     ModuleNotFoundError
    #         Raised if the module cannot be found
    #     """
    #     try:
    #         module importlib.import_module(name)

    #         func = getattr()
    #     except ModuleNotFoundError as e:
    #         print(f"Failed to import {name}")
        

    def execute_translator_module_function(self):
        """Executes the given function with the arguments passed into this class"""
        self.TMF.execute(self.args)

    def run(self) -> None:
        pass
