from ..QueueItem import QueueItem

class SequenceItem(QueueItem):
    
    def __init__(self, seq, OB) -> None:
        super().__init__()
        self.sequence = seq
        self.OB = OB
        # self.metadata = None
        # self.parameters = None

    # @classmethod
    # def from_sequence(cls, sequence):
    #     ret = SequenceItem()
    #     ret.metadata = sequence['metadata']
    #     ret.parameters = sequence['parameters']
    #     return ret
