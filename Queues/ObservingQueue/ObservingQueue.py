from Queues.BaseQueue import DDOIBaseQueue
from Queues.ObservingQueue.ObservingBlockItem import ObservingBlockItem
class ObservingQueue(DDOIBaseQueue):

    def __init__(self, logger=None, name=None) -> None:
        item_type = ObservingBlockItem
        super().__init__(item_type, logger=logger, name=name)

    def load_OBs(self):
        pass