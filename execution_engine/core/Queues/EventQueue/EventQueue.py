import importlib
import multiprocessing
import time
import logging
import random
from DDOILoggerClient import DDOILogger as dl
from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.Queues.EventQueue.EventItem import EventItem

def create_logger(subsystem, author, progid, semid, loggername, configLocation=None):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    try:
        kwargs = {'subsystem':subsystem, 
                  'author':author, 
                  'progid':progid, 
                  'semid':semid, 
                  'loggername': loggername}
        zmq_log_handler = dl.ZMQHandler(configLocation, local=False, **kwargs)
        logger.addHandler(zmq_log_handler)
    except Exception as err:
        print(f'zmq log handler failed. not going to add. {err}')
    logger.setLevel(logging.INFO)
    return logger

class EventQueue(DDOIBaseQueue):

    def __init__(self, logger=None, ddoi_config=None, interface=None, name=None) -> None:
        item_type = EventItem
        super().__init__(item_type, logger=logger, name=name)

        # Interface for this queue to talk to the outside world
        self.ODB_interface = interface
        self.logger = logger
        self.ddoi_config = ddoi_config

        if not self.ddoi_config['enable_dispatching']:
            self.logger.warning("Set up event queue in simulate only mode")
        
        
        # Event Dispatching Bookkeeping
        self.processes = [] # Used to kill processes if needed
        num_workers = int(self.ddoi_config['event_config']['num_processes'])

        # a multiprocessing.Manager is used to keep events and this queue
        # thread-safe. 
        self.manager = multiprocessing.Manager()
        self.logger.info(f"Multiprocessing manager started @ {self.manager.address}")
        self.logger.info(f"Authkey: {multiprocessing.current_process().authkey}")
        # This Event is used to dictate when the Queue is blocked
        self.block_event = self.manager.Event()
        # This Queue is used to distribute tasks out to worker processes
        self.multi_queue = self.manager.Queue()

        self.logger.info(f"Spawning {num_workers} event execution processes")

        if not run_events_sequentially:
            for i in range(num_workers):
                p = multiprocessing.Process(target=self.run, args=(self.multi_queue, f"worker_{i}"))
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

    def load_events_from_sequence(self, sequence, ob):
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

        instrument = sequence['metadata']['instrument']
        script_name = sequence['metadata']['script']
        script = self.get_script(instrument, script_name)
        sem_id = ob['metadata']['sem_id']
        event_type = 'sequence'
        instrument = sequence['metadata']['instrument']
        for el in script:
            self._add_event_item(el, {'sequence': sequence, 'OB': ob} , instrument, sem_id, event_type)

    def load_events_from_acquisition_and_target(self, ob):
        """Takes an acquisition and target and breaks it down into executable events this queue

        Parameters
        ----------
        acquisition: dict
            Acquisition component that should be decomposed function args 
        target : dict 
            Target that should be decomposed into function args
        """

        instrument = ob['acquisition']['metadata']['instrument']
        script_name = ob['acquisition']['metadata']['script']
        sem_id = ob['metadata']['sem_id']
        script = self.get_script(instrument, script_name)
        event_type = 'acquisition'
        for el in script:
            self._add_event_item(el, ob, instrument, sem_id, event_type)
    
    def _add_event_item(self, el, args, instrument, sem_id, event_type):
        """Takes a script element, arguments, and an instrument, creates an
        EventItem with the appropriate values set, and adds it to this queue

        Parameters
        ----------
        el : str
            DDOI Script element
        args : dict or dictlike
            arguments to be passed into the translator function (usually an OB)
        instrument : str
            Name of the instrument to fetch a translator for
        sem_id: str
            Name of the semester id 
        eventType: str
            Either 'acquisition' or 'sequence' 

        Raises
        ------
        NotImplementedError
            Raised if there is the given script element does not match any
            entries in the ddoi.json configuration file
        ImportError
            Raised if the translator module function cannot be imported
        """

        # Check if the script element passed in exists in the config
        if not el in self.ddoi_config['keywords'].keys():
            self.logger.error(f"Invalid script option encountered: {el}")
            raise NotImplementedError(f"Script element does not exist: {el}")
        
        try:
            # Try to find the translator module function for this element and
            # instrument
            func, subsystem = self._get_translator_function_and_subsystem(el, instrument)
            
            # See if this element is supposed to block execution flow
            try:
                block = self.ddoi_config['keywords'][el.upper()]['blocks']
            except KeyError as e:
                self.logger.warn(f"KeyError while trying to see if {el} blocks! Setting block=True")
                block=True
            
            # Create an event item, and insert it into this queue
            event = EventItem(  args=args,
                                subsystem=subsystem,
                                sem_id=sem_id,
                                event_type=event_type,
                                func=func, 
                                func_name=el.lower(), 
                                ddoi_config=self.ddoi_config,
                                block=block)
            self.put_one(event)

        # If the translator module function couldn't be imported, raise an error
        except ImportError as e:
            self.logger.error(f"Error while importing!")
            self.logger.error(e)
            raise e

    def _get_translator_function_and_subsystem(self, el, instrument):
        """Imports a translator module function for a given instrument

        Parameters
        ----------
        el : str
            DDOI Script element (e.g. acquire, waitfor_configure_science, etc)
        instrument : str
            Name of the instrument to import from, in capitals

        Returns
        -------
        function
            The imported translator module function

        Raises
        ------
        NotImplementedError
            Raised if the requested translator module function cannot be found
            in the instrument module
        """

        # Import the right translator module
        is_default_event = False # Set to true if the function exists in the ExEn
        if self.ddoi_config['keywords'][el.upper()]['translator'] == "INSTRUMENT":
            tm_name = self.ddoi_config['translator_import_names'][instrument]
            subsystem = self.ddoi_config['subsystems'][instrument]
        elif self.ddoi_config['keywords'][el.upper()]['translator'] == "ACQUISITION":
            tm_name = self.ddoi_config['translator_import_names']["ACQUISITION"]
            subsystem = self.ddoi_config['subsystems']["ACQUISITION"]
        elif self.ddoi_config['keywords'][el.upper()]['translator'] == "TELESCOPE":
            tm_name = self.ddoi_config['translator_import_names']["TELESCOPE"]
            subsystem = self.ddoi_config['subsystems']["TELESCOPE"]
        elif self.ddoi_config['keywords'][el.upper()]['translator'] == "BUTTON_EVENT":
            is_default_event = True
            subsystem = "UNKNOWN"
        else: 
            self.logger.error(f"Failed to find {el.lower()} ddoi config file, or the translator type is invalid")
            raise NotImplementedError(f"Failed to find {el} within the ddoi config file, or the translator type is invalid")

        # Import only the function we want, from the `ddoi_script_functions`
        # directory in the module
        if is_default_event:
            # Right now this only supports socket_event
            full_function_name = f"execution_engine.core.default_events.socket_event"
        else:
            full_function_name = f"{tm_name}.ddoi_script_functions.{el.lower()}"

        # Import the module
        module = importlib.import_module(full_function_name)

        try:
            # Get the specific function requested
            if is_default_event:
                func = getattr(module, 'socket_event')
            else:
                func = getattr(module, el.lower())
            return func, subsystem
        except AttributeError as e:
            # If the requested function doesn't exist in the module, raise an error
            self.logger.error(f"Failed to find {el.lower()} within the {full_function_name} module")
            raise NotImplementedError(f"Failed to find {el} within the {full_function_name} module")

    def dispatch_event(self, eventDict, force=False):
        """Pull the selected element of this queue and put it into the executing
        area, after checking for the appropriate flags

        Parameters
        ----------
        eventDict : dict
            Event dictionary type.
        force : bool, optional
            If true, ignore any blocks in the event queue, by default False

        Raises
        ------
        RuntimeError
            Raised if the queue is blocked and force=False
        """

        if self.block_event.is_set() and not force:
            # The queue is blocked, so we should reject this attempt
            self.logger.error("Attempting to dispatch event while queue is blocked")
            raise RuntimeError("Attempting to dispatch an event while blocked!")

        # Get the first event in the queue
        # event = self.get() # first event in the queue
        events = [evt for evt in list(self.queue)]
        submittedName, submittedID = eventDict['script_name'], eventDict['id']
        # Check that event matches what frontend submitted
        event, idx = next(((evt, idx) for idx, evt in enumerate(events) if evt.id == submittedID), False)
        nameMatches = event.script_name == submittedName
        if not event or not nameMatches:
            raise RuntimeError('submitted event {eventStr} does not match {event.script_name}@{event.id}')

        #bookeeping event queue
        events.pop(idx)
        boneyard = self.boneyard
        self.set_queue(events)
        boneyard.append(event)
        self.boneyard = boneyard

        # If we
        if event.block:
            self.logger.debug(f"Event ID {event.id} setting blocked.")
            if self.block_event.is_set() and not force:
                self.logger.error("Tried to fetch an event while blocked!")
                raise RuntimeError("Event Queue is blocked, but an event dispatch was requested")
            self.block_event.set()
            self.logger.debug(f"Event ID {event.id} set blocked.")

        self.logger.info(f"attempting to dispatch event {event.script_name}") 
        if self.ddoi_config['enable_dispatching']:
            if not self.ddoi_config['run_events_sequentially']:
                self.logger.info(f"Submitting event {event.id} to the queue")
                self.multi_queue.put({
                    "id" : event.id,
                    "event_item" : event,
                    "block_event" : self.block_event
                })
            else:
                subsystem = event.subsystem
                sem_id = event.sem_id
                logger = create_logger(subsystem=subsystem, author='seq-worker', sem_id=sem_id)
                logger.info(f'created logger for subsystem {subsystem}')
                self.logger.info(f"executing event {event.id} sequentially")
                event.func.execute(event.args, logger)
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
    def run(mqueue, name):
        """Run method for event workers

        Parameters
        ----------
        mqueue : mutliprocessing.Queue
            Queue to pull events from
        name : str
            Name of this process, for logging purposes
        """

        # The main event loop
        while(True):

            if mqueue.empty():
                time.sleep(1)
                continue
            
            # Pull from the queue
            event = mqueue.get()
            subsystem = event['event_item'].subsystem
            sem_id = event['event_item'].sem_id
            logger = create_logger(subsystem=subsystem, author=name, sem_id=sem_id, loggername='ddoi')
            logger.info(f'created logger for subsystem {subsystem}')

            logger.info(f"{name} accepted event {event['id']}")

            # If we got a kill message, end the event loop
            if event.get('kill', None):
                logger.info(f"{name} exiting by request")
                break
            
            logger.info(f"Executing event {event['event_item'].script_name}")
            logger.info(f"Translator is {str(event['event_item'].func)}")
            
            # Try to execute the event
            try:
                event['event_item'].func.execute(event['event_item'].args, logger)
                # If the event was blocking, release that block
                if event['event_item'].block:
                    event['block_event'].clear()

            except Exception as err:
                logger.error(f"Exception while trying to execute {name}!")
                break
            
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
