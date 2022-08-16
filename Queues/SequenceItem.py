from QueueItem import QueueItem

class SequenceItem(QueueItem):
    
    def __init__(self) -> None:
        super().__init__()
        self.metadata = None
        self.parameters = None

    @classmethod
    def from_sequence(sequence):
        ret = SequenceItem()
        ret.metadata = sequence['metadata']
        ret.parameters = sequence['parameters']
        return ret