from lib2to3.pytree import Base
import socket
import selectors
import sys
import types
import BaseQueue

class ObservingBlock():

    def __init__(self, ob_dict) -> None:
        self.ob = ob_dict
        self._parse_ob()

    def _parse_ob(self) -> None:
        """Init helper function
        """
        self.metadata = self.ob.get('metadata', None)
        self.acquisition = self.ob.get('acquisition', None)
        self.sequences = self.ob.get('sequences', None)
        self.target = self.ob.get('target', None)
        self.COMPONENTS = ['metadata', 'sequences', 'science', 'target']

# Create the three queues:
observing_queue = BaseQueue()
sequence_queue = BaseQueue()
event_queue = BaseQueue()

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
    # First, load the acquisition as the first sequence
    # Then, load each sequence into the list
    # Finally, return that list
    return []

def sequence_to_events(sequence, script) -> list:
    """Takes a sequence and breaks it down into executable events for the 
    event queue

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