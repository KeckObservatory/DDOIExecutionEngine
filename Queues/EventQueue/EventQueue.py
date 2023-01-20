import importlib

from Queues.BaseQueue import DDOIBaseQueue
from Queues.EventQueue.EventItem import EventItem

class ObservingQueue(DDOIBaseQueue):

    def __init__(self, logger, name=None) -> None:
        item_type = EventItem
        super().__init__(item_type, name)

        self.flags = {
            "block" : True,
            "wait_for_config" : True
        }

        self.logger = logger
        self.ddoi_config = {}

    def get_script(self, sequence):
        """Fetch a DDOI script for this sequence

        Parameters
        ----------
        sequence : SequenceItem
            Sequence that this function should find a script for
        """
        return[]

    def load_events_from_sequence(self, sequence):
        """Takes a sequence and breaks it down into executable events this queue
        
        This requires:
            - Parsing the script
            - Determining which Translator Modules are needed
            - Generating a process object that has access to:
                - all needed arguements
                - the needed Translator Module/Modules
                - some way to communicate its status back to this ExEn
            

        Parameters
        ----------
        sequence : SequenceDataModel
            Sequence that should be decomposed
        script : str
            Script that should be used to parse the sequence

        Returns
        -------
        list
            Python list of events
        """
        
        instrument = sequence['metadata']['instrument']

        # How do I get the script?
        script = []

        for el in script:
            if not self.ddoi_config['keywords'].has_key(el):
                self.logger.error(f"Invalid script option encountered: {el}")
                raise Exception() # TODO: figure out what to do with this
            
            try:
                tm_name = f"{self.ddoi_cfg['translators'][instrument]}.ddoi_script_functions"
                module = importlib.import_module(tm_name)

                try:
                    f = getattr(module, el)
                except AttributeError as e:
                    self.logger.error(f"Failed to find {el} within the {tm_name} module")
                    raise Exception() # TODO: figure out what to do with this
                
                event = EventItem(args=sequence.parameters, func=f)
                self.put_one(event)

            except ImportError as e:
                self.logger.error(f"Error while importing!")
        self.put_many([])

    def dispatch_event(self):
        """Pull the top element of this queue and put it into the executing
        area, after checking for the appropriate flags
        """
        event = self.get()

        