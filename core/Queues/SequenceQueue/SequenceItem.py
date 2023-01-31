from ..QueueItem import QueueItem

class SequenceItem(QueueItem):
    
    def __init__(self, num) -> None:
        super().__init__()
        self.sequence_number = num
        # self.metadata = None
        # self.parameters = None

    # @classmethod
    # def from_sequence(cls, sequence):
    #     ret = SequenceItem()
    #     ret.metadata = sequence['metadata']
    #     ret.parameters = sequence['parameters']
    #     return ret
