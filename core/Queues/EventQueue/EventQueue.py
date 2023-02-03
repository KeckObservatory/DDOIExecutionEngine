import importlib

from Queues.BaseQueue import DDOIBaseQueue
from Queues.EventQueue.EventItem import EventItem

class EventQueue(DDOIBaseQueue):

    def __init__(self, logger=None, interface=None, name=None) -> None:
        item_type = EventItem
        super().__init__(item_type, logger=logger, name=name)

        self.flags = {
            "block" : True,
            "wait_for_config" : True
        }
        self.odb_interface = interface
        self.logger = logger
        self.ddoi_config = {}

    def get_script(self, sequence):
        """Fetch a DDOI script for this sequence

        Parameters
        ----------
        sequence : SequenceItem
            Sequence that this function should find a script for
        """
        # Get the script        
        instrument = sequence['metadata']['instrument']
        script_name = sequence['metadata']['name']
        script_version = sequence['metadata']['version']
        script = self.odb_interace.get_script(instrument, script_name, script_version)

        return script

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

        script = self.get_script(sequence)
        instrument = sequence['metadata']['instrument']

        for el in script:
            if not self.ddoi_config['keywords'].has_key(el):
                self.logger.error(f"Invalid script option encountered: {el}")
                raise NotImplementedError(f"Script element does not exist: {el}")
            
            try:
                tm_name = f"{self.ddoi_cfg['translators'][sequence]}.ddoi_script_functions"
                module = importlib.import_module(tm_name)

                try:
                    func = getattr(module, el)
                except AttributeError as e:
                    self.logger.error(f"Failed to find {el} within the {tm_name} module")
                    raise NotImplementedError(f"Failed to find {el} within the {tm_name} module")
                
                
                event = EventItem(args=sequence.parameters, func=func)
                self.put_one(event)

            except ImportError as e:
                self.logger.error(f"Error while importing!")
                self.logger.error(e)

#############
## Fix Me! ##
#############

    def dispatch_event(self):
        """Pull the top element of this queue and put it into the executing
        area, after checking for the appropriate flags
        """
        event = self.get()


    def event_dispatcher(self, event_item):
        """Takes an event item and dispatches it to a process

        Parameters
        ----------
        event_item : EventItem
            EventItem that should be run

        Returns
        -------
        Tuple[Process, Connection]
            multiprocessing Process that is running the event, Pipe connection
        """
        def process_task(self, args) -> None:
            # Create an Event Executor object
            executor = EventExecutor(args["connection"], args["event_args"])
            executor.run()

        # Create a Pipe object for communication
        parent_connection, child_connection = Pipe(duplex=True)

        process_args = {
            "connection":child_connection
        }

        p = Process(target=process_task, args = process_args)

        return p, parent_connection

    def execute_event(self) -> None:
        event = self.ev_q.get()
        proc, conn = self.event_dispatcher(event)
        # Do something with the process here
        # Write a method for registering the connection with the socket somehow
        