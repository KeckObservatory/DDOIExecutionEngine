from ..QueueItem import QueueItem

class EventItem(QueueItem):
    
    def __init__(self, args, func, func_name, ddoi_config) -> None:
        super().__init__()
        self.args = args
        self.func = func
        self.script_name = func_name
        self.ddoi_config = ddoi_config
