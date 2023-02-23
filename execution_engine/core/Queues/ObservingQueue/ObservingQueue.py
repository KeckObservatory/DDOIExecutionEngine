from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.Queues.ObservingQueue.ObservingBlockItem import ObservingBlockItem
from execution_engine.core.Queues.SequenceQueue.SequenceQueue import SequenceQueue


class ObservingQueue(DDOIBaseQueue):

    def __init__(self, logger=None, interface=None, name=None) -> None:
        item_type = ObservingBlockItem
        self.odb_interface = interface
        super().__init__(item_type, logger=logger, name=name)

    def load_OB(self, id):
        OB = self.odb_interface.get_OB_from_id(id)
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

        OB_item = self.get()

        OB = self.odb_interface.get_OB_from_id(OB_item.ob_id)

        # self.logger.debug(f"Adding {len(OB.OBsequences)} elements to the sequence queue")
        sequence_queue.load_sequences_from_OB(OB)
        # sequence_queue.put_many(sequences)

