from asyncio import QueueEmpty
import QueueItem
import BaseQueue

class ObservingBlockItem(QueueItem):

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

class SequenceItem(QueueItem):
    pass

class EventItem(QueueItem):
    pass

# Create the three queues:
observing_queue = BaseQueue(ObservingBlockItem)
sequence_queue = BaseQueue(SequenceItem)
event_queue = BaseQueue(EventItem)

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

    output = []
    for seq in OB.sequences:
        output.append(SequenceItem.from_sequence(seq))
    return output

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