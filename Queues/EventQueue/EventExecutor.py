import multiprocessing
import importlib
from typing import Callable

class EventExecutor:

    def __init__(self, connection, args, execute = True) -> None:
        self.args = args

        self.TMF = self.import_translator_module_function(args.translator_module_name)

        self.pipe = connection

        # TODO: Send messages at each of these steps
        # TODO: figure out the logger
        # TODO: actually fill out the rest of this
        if execute:
            res = self.TMF(args.translator_arguments)
            

    def import_translator_module_function(self, name) -> Callable:
        """Attempts to import the specified Translator Module function and return it

        Parameters
        ----------
        name : str
            Import path for the Translator Module function to be imported

        Returns
        -------
        TranslatorModuleFunction
            Executable python function for the given function

        Raises
        ------
        ModuleNotFoundError
            Raised if the module cannot be found
        """
        try:
            importlib.import_module(name)
        except ModuleNotFoundError as e:
            print(f"Failed to import {name}")
        

    def execute_translator_module_function(self, function) -> bool:
        """Executes the given function with the arguments passed into this class

        Parameters
        ----------
        function : TranslatorModuleFunction
            The TranslatorModuleFunction to be invoked

        Returns
        -------
        bool
            True if the execution was successful, False otherwise
        """
        pass

    def run(self) -> None:
        pass