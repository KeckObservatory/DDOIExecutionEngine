import json
import pdb
from ..QueueItem import QueueItem

class ObservingBlockItem(QueueItem):

    def __init__(self, ob_id) -> None:
        super().__init__()
        self.ob_id = ob_id

    def as_dict(self):
        return {
            "id" : self.id,
            "ob_id" : self.ob_id
        }
