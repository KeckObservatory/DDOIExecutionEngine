from ..QueueItem import QueueItem

class EventItem(QueueItem):
    
    def __init__(self, args, subsystem, semid, func, func_name, ddoi_config, block) -> None:
        super().__init__()
        self.args = args
        self.subsystem = subsystem
        self.semid = semid 
        self.func = func
        self.script_name = func_name
        self.ddoi_config = ddoi_config
        self.block = block

    def as_dict(self):
        return {
            "id" : self.id,
            "subsystem": self.subsystem,
            "semid": self.semid,
            "args" : self.args,
            "script_name" : self.script_name, 
            "block" : self.block
        }