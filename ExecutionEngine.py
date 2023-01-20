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

from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from typing import Tuple, List

from Queues.EventQueue.EventExecutor import EventExecutor
from Queues.BaseQueue import DDOIBaseQueue
from Queues.ObservingQueue.ObservingBlockItem import ObservingBlockItem
from Queues.SequenceQueue.SequenceItem import SequenceItem
from Queues.EventQueue.EventItem import EventItem

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

    def __init__(self) -> None:
        self.obs_q, self.seq_q, self.ev_q = self._create_queues()


    def _create_queues(self) -> Tuple[DDOIBaseQueue, DDOIBaseQueue, DDOIBaseQueue]:
        """Creates the three queues

        Returns
        -------
        Tuple[DDOIBaseQueue, DDOIBaseQueue, DDOIBaseQueue]
            Observing Queue, Sequence Queue, Event Queue
        """
        observing_queue = DDOIBaseQueue(ObservingBlockItem)
        sequence_queue = DDOIBaseQueue(SequenceItem)
        event_queue = DDOIBaseQueue(EventItem)

        return observing_queue, sequence_queue, event_queue

    def OB_to_sequence(self) -> None:
        """Transfers an OB from the front of the Observing Queue to the sequence
        queue, splitting it up as required

        Parameters
        ----------
        observing_queue : DDOIBaseQueue
            Observing queue
        sequence_queue : DDOIBaseQueue
            Sequence Queue
        """
        OB = self.obs_q.get()
        self.seq_q.put_many(self._decompose_OB(OB))

    def sequence_to_event(self) -> None:
        """Transfers a sequence from the front of the sequence queue to the
        event queue, splitting it up into events as required

        Parameters
        ----------
        sequence_queue : DDOIBaseQueue
            Sequence queue
        event_queue : DDOIBaseQueue
            Event queue
        """
        sequence = self.seq_q.get()
        self.ev_q.put_many(self._decompose_sequence(sequence))

    def _decompose_OB(self, OB) -> list:
        """Takes an OB item from a queue and converts it to a list of sequences

        Parameters
        ----------
        OB : ObervingBlockDataModel
            Observing Block to decompose into sequences

        Returns
        -------
        list
            Python list of sequences
        """

        output = [SequenceItem.from_sequence(seq) for seq in OB.sequences]
        return output

    def _decompose_sequence(self, sequence, script) -> List:
        """Takes a sequence and breaks it down into executable events for the 
        event queue. This requires:
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
        return []

    def event_dispatcher(self, event_item) -> Tuple[Process, Connection]:
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
        parent_connection, child_connection = Pipe()

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
