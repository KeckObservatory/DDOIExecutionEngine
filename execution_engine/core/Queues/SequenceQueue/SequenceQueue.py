from execution_engine.core.Queues.BaseQueue import DDOIBaseQueue
from execution_engine.core.Queues.SequenceQueue.SequenceItem import SequenceItem
from execution_engine.core.Queues.EventQueue.EventQueue import EventQueue


class SequenceQueue(DDOIBaseQueue):

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
        sequences = [seq for seq in OB.OB['observations']]
        for sequence in sequences:
            self.put_one(SequenceItem(sequence, OB))

    def select_sequence(self, event_queue):
        """Pops the first sequence from this queue and adds the corresponding events
        to the event queue.

        Parameters
        ----------
        event_queue : EventQueue
            EventQueue object to insert the events into
        """

        if not isinstance(event_queue, EventQueue):
            self.logger.error("Object passed into select_sequence is not a sequence queue!")

        sequence = self.get()

        events = event_queue.load_events_from_sequence(sequence)

        event_queue.put_many(events)
