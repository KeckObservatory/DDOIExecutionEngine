import importlib
import multiprocessing
import time

from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.Queues.EventQueue.EventItem import EventItem

# This variable dictates whether events are allowed to be dispatched. For
# deployment, set this to True. Otherwise, leave it as False.
enable_dispatching = False

class EventQueue(DDOIBaseQueue):

    def __init__(self, logger=None, ddoi_cfg=None, interface=None, name=None) -> None:
        item_type = EventItem
        super().__init__(item_type, logger=logger, name=name)

        
        self.ODB_interface = interface
        self.logger = logger
        self.ddoi_config = ddoi_cfg
        self.lock = multiprocessing.Lock()

        if not enable_dispatching:
            self.logger.warning("Set up event queue in simulate only mode")
        
        
        # Event Dispatching Bookkeeping
        self.processes = []
        self.multi_queue = multiprocessing.Queue()
        num_workers = int(self.ddoi_config['event_config']['num_processes'])
        self.logger.info(f"Spawning {num_workers} event execution processes")
        for i in range(num_workers):
            p = multiprocessing.Process(target=self.run, args=(self.multi_queue, f"worker_{i}", self.logger))
            p.start()
            self.logger.debug(f"Event Queue started worker_{i}")

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
                
                #TODO: include lock boolean 
                block = True 
                event = EventItem(args=sequence.as_dict(),
                                  func=func, 
                                  func_name=el.lower(), 
                                  ddoi_config=self.ddoi_config,
                                  block=block)
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

        isBlocked = not self.lock.acquire(block=False) # blocks
        self.lock.release() # need to release lock
        if isBlocked and not force:
            self.logger.error("Tried to fetch an event while blocked!")
            raise SystemError("Event Queue is blocked, but an event dispatch was requested")
        
        event = self.get()

        if event.block:
            self.logger.debug(f"Event ID {event.id} acquiring blocking lock.")
            self.lock.acquire(block=True)
            self.logger.debug(f"Event ID {event.id} acquired lock.")
        else: 
            if isBlocked: self.lock.release()

        
        if enable_dispatching:
            self.logger.info(f"Submitting event {event.id} to the queue")
            self.multi_queue.put({
                "id" : event.id,
                "event_item" : event,
                "lock" : self.lock
            })
        else:
            self.logger.info(f"Queue in simulate only mode. Would have sent {event.id} for dispatching")
            if isBlocked: self.lock.release()

    @staticmethod
    def run(mqueue, name, logger, lock=None):

        while(True):
            if mqueue.empty():
                continue
            
            # Pull from the queue
            event = mqueue.get()

            logger.info(f"{name} accepted event {event.id}")

            if event.get('kill', None):
                logger.info(f"{name} exiting by request")
                break

            logger.info(f"Executing event {event.script_name}")
            try:
                # event.func(event.args)
                if lock is not None:
                    logger.debug(f"{name} attempting to release the blocking lock")
                    try:
                        lock.release()
                    except ValueError as e:
                        logger.error(f"{name} attempted to release the blocking lock, but it was already unlocked!")
            except Exception as e:
                logger.error(f"Exception while trying to execute {name}!")
                logger.error(e)
                return
            
            time.sleep(1)

    def kill_workers(self, block=True, nicely=True):
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
        
        def all_procs_dead(processes):
            for proc in processes:
                if proc.is_alive():
                    return False
            return True  
        
        if block:
            self.logger.info("Waiting for event queue workers to self destruct")
            while (not all_procs_dead(self.processes)):
                continue
        
            
        if all_procs_dead(self.processes):
            self.logger.info("All workers are dead, as expected")
