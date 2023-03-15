from execution_engine.core.Queues.QueueItem import QueueItem

class SequenceItem(QueueItem):
    
    def __init__(self, seq, OB) -> None:
        super().__init__()
        self.sequence = seq
        self.OB = OB

    def as_dict(self):
        return {
            "id" : self.id,
            "sequence" : self.sequence,
            "OB" : self.OB
        }
    
