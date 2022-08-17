import multiprocessing

class EventExecutor:

    def __init__(self, args, execute = True) -> None:
        self.args = args

        self.TMF = self.import_translator_module_function(args.translator_module_name)

        # TODO: Send messages at each of these steps
        # TODO: figure out the logger
        # TODO: actually fill out the rest of this
        if execute:
            res = self.TMF(args.translator_arguments)
            

    def import_translator_module_function(self, name) -> function:
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
        if 4 == 4:
            raise ModuleNotFoundError
        # Try to import the module given by the name
        pass

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