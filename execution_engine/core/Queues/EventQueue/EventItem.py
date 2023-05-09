from ..QueueItem import QueueItem

class EventItem(QueueItem):
    
    def __init__(self, args, subsystem, sem_id, event_type, func, func_name, ddoi_config, block) -> None:
        super().__init__()
        self.args = args
        self.subsystem = subsystem
        self.sem_id = sem_id 
        self.event_type = event_type
        self.func = func
        self.script_name = func_name
        self.ddoi_config = ddoi_config
        self.block = block

    def as_dict(self):
        return {
            "id" : self.id,
            "subsystem": self.subsystem,
            "sem_id": self.sem_id,
            "event_type": self.event_type,
            "args" : self.args,
            "script_name" : self.script_name, 
            "block" : self.block
        }