import json
import pdb
from ..QueueItem import QueueItem

class ObservingBlockItem(QueueItem):

    def __init__(self, ob_info) -> None:
        super().__init__()
        self.ob_info = ob_info

    def as_dict(self):
        return {
            "id" : self.id,
            "ob_info" : self.ob_info
        }
