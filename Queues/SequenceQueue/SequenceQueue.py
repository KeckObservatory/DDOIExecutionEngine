from Queues.BaseQueue import DDOIBaseQueue
from Queues.SequenceQueue.SequenceItem import SequenceItem
class ObservingQueue(DDOIBaseQueue):

    def __init__(self, logger=None, name=None) -> None:
        item_type = SequenceItem
        super().__init__(item_type, logger=logger, name=name)

    def load_sequences_from_OB(self, OB):
        """Takes an OB and loads its sequences into this queue

        Parameters
        ----------
        OB : ObervingBlockDataModel
            Observing Block to decompose into sequences

        """
        sequences = [SequenceItem.from_sequence(seq) for seq in OB.sequences]
        self.put_many(sequences)