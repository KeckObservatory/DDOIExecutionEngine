from multiprocessing import Process
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

def OB_to_sequence(OB) -> list:
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

def event_dispatcher(event_item) -> Process:
    """Takes an event item and dispatches it to a process

    Parameters
    ----------
    event_item : EventItem
        EventItem that should be run

    Returns
    -------
    Process
        multiprocessing Process that is running the event
    """

    