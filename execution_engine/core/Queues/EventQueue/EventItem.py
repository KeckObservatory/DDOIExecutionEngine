from ..QueueItem import QueueItem

class EventItem(QueueItem):
    
    def __init__(self, args, func, ddoi_config) -> None:
        super().__init__()
        self.args = args
        self.func = func
        self.ddoi_config = ddoi_config
