import importlib
import multiprocessing

from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.Queues.EventQueue.EventItem import EventItem

class EventQueue(DDOIBaseQueue):

    def __init__(self, logger=None, ddoi_cfg=None, interface=None, name=None) -> None:
        item_type = EventItem
        super().__init__(item_type, logger=logger, name=name)

        self.flags = {
            "block" : True,
            "wait_for_config" : True
        }
        self.ODB_interface = interface
        self.logger = logger
        self.ddoi_config = ddoi_cfg
        self.blocked = False

        # Event Dispatching Bookkeeping
        self.processes = []
        self.queue = multiprocessing.Queue()
        num_workers = int(self.ddoi_config['event_config']['num_processes'])
        for i in range(num_workers):
            p = multiprocessing.Process(target=self.run, args=(self.queue, f"worker_{i}", self.logger))
            p.start()

    def get_script(self, sequence):
        """Fetch a DDOI script for this sequence

        Parameters
        ----------
        sequence : SequenceItem
            Sequence that this function should find a script for
        """
        # Get the script        
        instrument = sequence.sequence['metadata']['instrument']
        script_name = sequence.sequence['metadata']['name']
        script_version = sequence.sequence['metadata']['version']
        script = self.ODB_interface.get_script(instrument, script_name, script_version)
        output = []
        for el in script:
            output.append(el[0])
        return output

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
        print(script)
        instrument = sequence.sequence['metadata']['instrument']

        for el in script:
            if not el in self.ddoi_config['keywords'].keys():
                self.logger.error(f"Invalid script option encountered: {el}")
                raise NotImplementedError(f"Script element does not exist: {el}")
            
            try:
                tm_name = f"{self.ddoi_config['translators'][instrument]}.ddoi_script_functions.{el.lower()}"
                module = importlib.import_module(tm_name)

                try:
                    func = getattr(module, el.lower())
                except AttributeError as e:
                    self.logger.error(f"Failed to find {el.lower()} within the {tm_name} module")
                    raise NotImplementedError(f"Failed to find {el} within the {tm_name} module")
                
                
                event = EventItem(args=sequence, func=func, func_name=el.lower(), ddoi_config=self.ddoi_config)
                self.put_one(event)

            except ImportError as e:
                self.logger.error(f"Error while importing!")
                self.logger.error(e)
                raise e

#############
## Fix Me! ##
#############

    def dispatch_event(self, force=False):
        """Pull the top element of this queue and put it into the executing
        area, after checking for the appropriate flags
        """

        if self.blocked and not force:
            raise SystemError("Event Queue is blocked, but an event dispatch was requested")
        
        event = self.get()

        if event.block:
            self.blocked = True

        self.queue.put({
            "id" : event.id,
            "event_item" : event
        })

    @staticmethod
    def run(queue, name, logger):
        # queue = args[0]
        # name = args[1]
        # logger = args[2]

        while(True):
            if queue.empty():
                continue
            
            # Pull from the queue
            event = queue.get()

            logger.info(f"{name} accepted event {event['id']}")

            if event['kill']:
                logger.info(f"{name} exiting by request")
                break

            # Do it, while communicating with a Pipe?
            # pipe = event['pipe']

            event_item = event['event_item']
            logger.info(f"Executing event")
            event_item.execute()
            

    def kill_workers(self, nicely=True):
        if nicely:
            self.logger.info(f"Requesting that {len(self.processes)} workers exit")
            for proc in self.processes:
                self.queue.put({
                    "kill" : True,
                })
        else:
            self.logger.info(f"Terminating {len(self.processes)} workers")
            for proc in self.processes:
                proc.kill()
