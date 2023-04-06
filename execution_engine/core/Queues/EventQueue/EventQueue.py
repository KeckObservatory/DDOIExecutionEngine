import importlib
import multiprocessing
import time

from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.Queues.EventQueue.EventItem import EventItem

# This variable dictates whether events are allowed to be dispatched. For
# deployment, set this to True. Otherwise, leave it as False.
enable_dispatching = True

class EventQueue(DDOIBaseQueue):

    def __init__(self, logger=None, ddoi_cfg=None, interface=None, name=None) -> None:
        item_type = EventItem
        super().__init__(item_type, logger=logger, name=name)

        
        self.ODB_interface = interface
        self.logger = logger
        self.ddoi_config = ddoi_cfg

        if not enable_dispatching:
            self.logger.warning("Set up event queue in simulate only mode")
        
        
        # Event Dispatching Bookkeeping
        self.processes = []
        num_workers = int(self.ddoi_config['event_config']['num_processes'])

        self.manager = multiprocessing.Manager()
        self.logger.info(f"Multiprocessing manager started @ {self.manager.address}")
        self.logger.info(f"Authkey: {multiprocessing.current_process().authkey}")
        self.block_event = self.manager.Event()
        self.multi_queue = self.manager.Queue()

        self.logger.info(f"Spawning {num_workers} event execution processes")
        for i in range(num_workers):
            p = multiprocessing.Process(target=self.run, args=(self.multi_queue, f"worker_{i}", self.logger))
            p.start()
            self.logger.debug(f"Event Queue started worker_{i}")

    #######################
    # Queue-related stuff #
    #######################

    def get_script(self, instrument, script_name):
        """Fetch a DDOI script for this sequence

        Parameters
        ----------
        sequence : SequenceItem
            Sequence that this function should find a script for
        """
        # Get the script        
        script = self.ODB_interface.get_script(instrument, script_name)
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
        """

        instrument = sequence.sequence['metadata']['instrument']
        script_name = sequence.sequence['metadata']['script']
        script = self.get_script(instrument, script_name)
        print(script)
        instrument = sequence.sequence['metadata']['instrument']
        for el in script:
            self._add_event_item(el, sequence.as_dict(), instrument)

    def load_events_from_acquisition_and_target(self, acquisition, target):
        """Takes an acquisition and target and breaks it down into executable events this queue

        Parameters
        ----------
        acquisition: dict
            Acquisition component that should be decomposed function args 
        target : dict 
            Target that should be decomposed into function args
        """

        instrument = acquisition['metadata']['instrument']
        script_name = acquisition['metadata']['script']
        script = self.get_script(instrument, script_name)
        print(script)
        args = { 'acquisition': acquisition, 'target': target}
        for el in script:
            self._add_event_item(el, args, instrument)
    
    def _add_event_item(self, el, args, instrument):
        if not el in self.ddoi_config['keywords'].keys():
            self.logger.error(f"Invalid script option encountered: {el}")
            raise NotImplementedError(f"Script element does not exist: {el}")
        
        try:
            func = self._get_translator_function(el, instrument)
            block = True # TODO: This shouldn't always be blocking!
            event = EventItem(args=args,
                                func=func, 
                                func_name=el.lower(), 
                                ddoi_config=self.ddoi_config,
                                block=block)
            self.put_one(event)

        except ImportError as e:
            self.logger.error(f"Error while importing!")
            self.logger.error(e)
            raise e

    def _get_translator_function(self, el, instrument):

        # Import the right translator module
        if self.ddoi_config['keywords'][el]['translator'] == "INSTRUMENT":
            tm_name = self.ddoi_config['translator_import_names'][instrument]
        elif self.ddoi_config['keywords'][el]['translator'] == "ACQUISITION":
            tm_name = self.ddoi_config['translator_import_names']["ACQUISITION"]
        elif self.ddoi_config['keywords'][el]['translator'] == "TELESCOPE":
            tm_name = self.ddoi_config['translator_import_names']["TELESCOPE"]

        full_function_name = f"{tm_name}.ddoi_script_functions.{el.lower()}"

        module = importlib.import_module(full_function_name)

        try:
            func = getattr(module, el.lower())
            return func
        except AttributeError as e:
            self.logger.error(f"Failed to find {el.lower()} within the {full_function_name} module")
            raise NotImplementedError(f"Failed to find {el} within the {full_function_name} module")

    def dispatch_event(self, force=False):
        """Pull the top element of this queue and put it into the executing
        area, after checking for the appropriate flags
        """
        isBlocked = self.block_event.is_set()
        if isBlocked and not force:
            self.logger.error("Tried to fetch an event while blocked!")
            raise SystemError("Event Queue is blocked, but an event dispatch was requested")
        
        event = self.get()

        if event.block:
            self.logger.debug(f"Event ID {event.id} setting blocked.")
            if self.block_event.is_set():
                raise RuntimeError("Race condition encountered! Another processes interupted me")
            self.block_event.set()
            self.logger.debug(f"Event ID {event.id} set blocked.")

        self.logger.info(f"attempting to dispatch event {event.script_name}") 
        if enable_dispatching:
            self.logger.info(f"Submitting event {event.id} to the queue")
            self.multi_queue.put({
                "id" : event.id,
                "event_item" : event,
                "block_event" : self.block_event
            })
        else:
            self.logger.info(f"Queue in simulate only mode. Would have sent {event.id} for dispatching")
            # We are in simulate mode, so blocking events will never release!
            # We have to do it manually, after an arbitrary sleep
            if event.block:
                time.sleep(1)
                self.block_event.clear()
           
    ###########################
    # Event dispatching stuff #
    ###########################

    @staticmethod
    def run(mqueue, name, logger, block_event=None):
        """Run method for event workers

        Parameters
        ----------
        mqueue : mutliprocessing.Queue
            Queue to pull events from
        name : str
            Name of this process, for logging purposes
        logger : logging.Logger
            Logger to write messages to
        lock : multiprocessing.Lock, optional
            Lock used to enable blocking/non-blocking functions, by default None
        """

        while(True):

            time.sleep(1)
            if mqueue.empty():
                continue
            
            # Pull from the queue
            event = mqueue.get()

            logger.info(f"{name} accepted event {event['id']}")

            if event.get('kill', None):
                logger.info(f"{name} exiting by request")
                break

            logger.info(f"Executing event {event['event_item'].script_name}")
            logger.info(f"Translator is {str(event['event_item'].func)}")
            try:
                event['event_item'].func.execute(event['event_item'].args)
                if event['event_item'].block:
                    event['block_event'].clear()
                # if lock is not None:
                #     logger.debug(f"{name} attempting to release the blocking lock")
                #     try:
                #         lock.release()
                #     except ValueError as e:
                #         logger.error(f"{name} attempted to release the blocking lock, but it was already unlocked!")
            except Exception as e:
                logger.error(f"Exception while trying to execute {name}!")
                logger.error(e.with_traceback())
                return
            

    def kill_workers(self, block=True, nicely=True):
        """Kills all workers in self.processes, with varying levels of severity

        Parameters
        ----------
        block : bool, optional
            If True, hang until all processes are dead. If False, return
            immediately, by default True
        nicely : bool, optional
            If True, send a message to each process requesting that it exit when
            possible . If False, forcibly kill each process, regardless of 
            whether it is busy, by default True
        """
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
