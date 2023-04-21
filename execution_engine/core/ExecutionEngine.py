"""
Execution Engine Base Script. Key components are:

    - The three queues:
        - Observing Queue (contains OBs)
        - Sequence Queue (contains sequences)
        - Event Queue (contains individual events)
    - To go along with each queue, a "transfer function" that takes something
      from a given queue, and transfers it to something that the next queue/step
      can understand:
        - _decompose_sequence() takes an OB, and outputs a list of sequences
        - _decompose_sequence() takes a single sequence, and outputs a list of
          events
        - dispatch_event() takes an event, and sends it to an EventExecutor for
          execution
"""

from typing import Tuple
from pathlib import Path
import logging
from logging import StreamHandler, FileHandler
import pkg_resources
import json
import configparser
import multiprocessing

from execution_engine.core.MagiqInterface import MagiqInterface
from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.EventSocketServer import PipeServer
from execution_engine.core.Queues.ObservingQueue.ObservingQueue import ObservingQueue
from execution_engine.core.Queues.SequenceQueue.SequenceQueue import SequenceQueue
from execution_engine.core.Queues.EventQueue.EventQueue import EventQueue
from execution_engine.interface.ODBInterface import ODBInterface

class ExecutionEngine:
    """Class representing an instance of the Execution Engine

    Use:

    # Create the Execution Engine instance
    ExEng = ExecutionEngine()

    # Load in your OB_list
    ExEng.obs_q.put_many([ObservingBlockItem.from_json(OB) for OB in OB_list])

    # Transfer the first OB to the sequences queue
    ExEng.OB_to_sequence()

    # Transfer a sequence to the events queue
    ExEng.sequence_to_event()

    # Dispatch an event as needed until the queue is empty
    ExEng.execute_event()
    """

    def __init__(self, logger, cfg) -> None:
        self.logger = logger
        self.logger.info("Logger set in Execution Engine")

        # Handle API config
        self.cfg = configparser.ConfigParser()
        
        if not Path(cfg).exists():
            raise FileNotFoundError(f"Config file {cfg} does not exist!")

        self.logger.debug(f"Parsing config file: {cfg}")
        self.cfg.read(cfg)

        # Handle DDOI config
        pkg = "execution_engine"
        cfgpath = "configs/ddoi.json"
        self.ddoi_cfg_log_path = pkg_resources.resource_filename(pkg, cfgpath)
        ddoicfg = open(self.ddoi_cfg_log_path)
        self.ddoi_cfg = json.load(ddoicfg)

        self.logger.debug(f"Creating ODB Interface")
        self.ODBInterface = ODBInterface(self.cfg, self.logger)
        self.obs_q, self.seq_q, self.ev_q = self._create_queues()

        self.magiq_interface = MagiqInterface(self.cfg)

        self.server_connection, _internal_connection = multiprocessing.Pipe(duplex=True)

        server_proc = multiprocessing.Process(target=self.start_event_server, args=(_internal_connection, logger))
        logger.info("Starting event server process...")
        server_proc.start()
        logger.debug(f"Event server started with PID {server_proc.pid}")


    def _create_queues(self) -> Tuple[DDOIBaseQueue, DDOIBaseQueue, DDOIBaseQueue]:
        """Creates the three queues

        Returns
        -------
        Tuple[DDOIBaseQueue, DDOIBaseQueue, DDOIBaseQueue]
            Observing Queue, Sequence Queue, Event Queue
        """

        observing_queue = ObservingQueue(name="observing_queue", interface=self.ODBInterface, logger=self.logger)
        sequence_queue = SequenceQueue(name="sequence_queue", logger=self.logger)
        event_queue = EventQueue(name="event_queue", ddoi_cfg = self.ddoi_cfg, interface=self.ODBInterface, logger=self.logger)

        return observing_queue, sequence_queue, event_queue
    
    def start_event_server(self, connection, logger):
        server = PipeServer(connection, logger)
        server.start()