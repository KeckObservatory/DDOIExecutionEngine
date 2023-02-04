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
import os
import logging
from logging import StreamHandler, FileHandler

from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
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

    def __init__(self, cfg, ddoi_cfg) -> None:
        self.logger = self.create_logger("test.log")
        self.cfg_loc = cfg
        self.ddoi_cfg_loc = ddoi_cfg
        # cfg_loc = os.path.dirname(os.path.abspath(__file__))
        # cfg = f"{cfg_loc}/../configs/cfg.ini"
        # cfg = "/Users/mbrodheim/ddoi/ExecutionEngine/execution_engine/configs/cfg.ini"
        # ddo_cfg = "/Users/mbrodheim/ddoi/ExecutionEngine/execution_engine/configs/ddoi.json"

        self.logger.debug(f"Creating ODB Interface from config file {self.cfg_loc}")
        self.ODBInterface = ODBInterface(self.cfg_loc, self.logger)
        self.obs_q, self.seq_q, self.ev_q = self._create_queues()


    def _create_queues(self) -> Tuple[DDOIBaseQueue, DDOIBaseQueue, DDOIBaseQueue]:
        """Creates the three queues

        Returns
        -------
        Tuple[DDOIBaseQueue, DDOIBaseQueue, DDOIBaseQueue]
            Observing Queue, Sequence Queue, Event Queue
        """
        # observing_queue = DDOIBaseQueue(ObservingBlockItem)
        # sequence_queue = DDOIBaseQueue(SequenceItem)
        # event_queue = DDOIBaseQueue(EventItem)
        observing_queue = ObservingQueue(name="observing_queue", interface=self.ODBInterface, logger=self.logger)
        sequence_queue = SequenceQueue(name="sequence_queue", logger=self.logger)
        event_queue = EventQueue(name="event_queue", ddoi_cfg = self.ddoi_cfg_loc, interface=self.ODBInterface, logger=self.logger)

        return observing_queue, sequence_queue, event_queue

    def create_logger(self, fileName):
      # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      # zmq_log_handler = dl.ZMQHandler(subsystem, configLoc, author, progid, semid)
      ch = StreamHandler()
      # ch.setLevel(logging.INFO)
      # ch.setFormatter(formatter)
      fl = FileHandler(fileName)
      # fl.setLevel(logging.DEBUG)
      # fl.setFormatter(formatter)
      logger = logging.getLogger()
      # logger.addHandler(zmq_log_handler)
      logger.addHandler(ch)
      logger.addHandler(fl)
      return logger
    # def OB_to_sequence(self) -> None:
    #     """Transfers an OB from the front of the Observing Queue to the sequence
    #     queue, splitting it up as required

    #     Parameters
    #     ----------
    #     observing_queue : DDOIBaseQueue
    #         Observing queue
    #     sequence_queue : DDOIBaseQueue
    #         Sequence Queue
    #     """
    #     OB = self.obs_q.get()
    #     self.seq_q.put_many(self._decompose_OB(OB))

    # def sequence_to_event(self) -> None:
    #     """Transfers a sequence from the front of the sequence queue to the
    #     event queue, splitting it up into events as required

    #     Parameters
    #     ----------
    #     sequence_queue : DDOIBaseQueue
    #         Sequence queue
    #     event_queue : DDOIBaseQueue
    #         Event queue
    #     """
    #     sequence = self.seq_q.get()
    #     self.ev_q.put_many(self._decompose_sequence(sequence))

    # def _decompose_OB(self, OB) -> list:
    #     """Takes an OB item from a queue and converts it to a list of sequences

    #     Parameters
    #     ----------
    #     OB : ObervingBlockDataModel
    #         Observing Block to decompose into sequences

    #     Returns
    #     -------
    #     list
    #         Python list of sequences
    #     """

    #     output = [SequenceItem.from_sequence(seq) for seq in OB.sequences]
    #     return output

    # def _decompose_sequence(self, sequence, script) -> List:
    #     """Takes a sequence and breaks it down into executable events for the 
    #     event queue. This requires:
    #         - Parsing the script
    #         - Determining which Translator Modules are needed
    #         - Generating a process object that has access to:
    #             - all needed arguements
    #             - the needed Translator Module/Modules
    #             - some way to communicate its status back to this ExEn
            

    #     Parameters
    #     ----------
    #     sequence : SequenceDataModel
    #         Sequence that should be decomposed
    #     script : str
    #         Script that should be used to parse the sequence

    #     Returns
    #     -------
    #     list
    #         Python list of events
    #     """
    #     return []

    