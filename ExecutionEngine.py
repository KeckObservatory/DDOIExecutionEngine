"""
Execution Engine Base Script. Key components are:

    - The three queues:
        - Observing Queue (contains OBs)
        - Sequence Queue (contains sequences)
        - Event Queue (contains individual events)
    - To go along with each queue, a "transfer function" that takes something
      from a given queue, and transfers it to something that the next queue/step
      can understand:
        - OB_to_sequences() takes an OB, and outputs a list of sequences
        - sequence_to_events() takes a single sequence, and outputs a list of
          events
        - dispatch_event() takes an event, and sends it to an EventExecutor for
          execution
"""

from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from typing import Tuple

from EventExecutor import EventExecutor
from Queues.BaseQueue import DDOIBaseQueue
from Queues.ObservingBlockItem import ObservingBlockItem
from Queues.SequenceItem import SequenceItem
from Queues.EventItem import EventItem

# Create the three queues:
observing_queue = DDOIBaseQueue(ObservingBlockItem)
sequence_queue = DDOIBaseQueue(SequenceItem)
event_queue = DDOIBaseQueue(EventItem)

def OB_to_sequence() -> None:
    OB = observing_queue.get()
    sequence_queue.put_many(OB_to_sequence(OB))

def OB_to_sequences(OB) -> list:
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

    output = []
    for seq in OB.sequences:
        output.append(SequenceItem.from_sequence(seq))
    return output



def sequence_to_events(sequence, script) -> list:
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

def event_dispatcher(event_item) -> Tuple[Process, Connection]:
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
    def process_task(args) -> None:
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