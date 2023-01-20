from Queues.BaseQueue import DDOIBaseQueue
from Queues.ObservingQueue.ObservingBlockItem import ObservingBlockItem
class ObservingQueue(DDOIBaseQueue):

    def __init__(self, name=None) -> None:
        item_type = ObservingBlockItem
        super().__init__(item_type, name)

    def load_OBs(self):
        pass