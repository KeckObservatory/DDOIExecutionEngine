from Queues.BaseQueue import DDOIBaseQueue
from Queues.ObservingQueue.ObservingBlockItem import ObservingBlockItem
from Queues.SequenceQueue import SequenceQueue


class ObservingQueue(DDOIBaseQueue):

    def __init__(self, logger=None, interface=None, name=None) -> None:
        item_type = ObservingBlockItem
        self.odb_interface = interface
        super().__init__(item_type, logger=logger, name=name)

    def load_OB(self, id):
        OB = self.odb_interface.get_ob_from_id(id)
        self.put_one(ObservingBlockItem(OB=OB))

    def select_OB(self, sequence_queue):
        """Select the top OB of this queue for observation. The OB is popped
        from the queue, decomposed into a list of sequences, and put into the
        sequence queue

        Parameters
        ----------
        sequence_queue : SequenceQueue
            Sequence queue to insert OB components into
        """

        if not isinstance(sequence_queue, SequenceQueue):
            self.logger.error("Object passed into select_OB is not a sequence queue!")
            raise Exception("ADD MORE HERE")

        OB = self.get()
        sequences = sequence_queue.load_sequences_from_OB(OB)
        self.logger.debug(f"Adding {len(sequences)} elements to the sequence queue")
        sequence_queue.put_many(sequences)

