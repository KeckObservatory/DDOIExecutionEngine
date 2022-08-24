import json
from .QueueItem import QueueItem

class ObservingBlockItem(QueueItem):

    def __init__(self) -> None:
        super().__init__()
        self.metadata = None
        self.acquisition = None
        self.sequences = None
        self.target = None
        self.COMPONENTS = None

    @classmethod
    def from_JSON(cls, filename):
        ob = json.loads(json)
        ret = ObservingBlockItem()
        ret.metadata = ob.get('metadata', None)
        ret.acquisition = ob.get('acquisition', None)
        ret.sequences = ob.get('observations', None)
        ret.target = ob.get('target', None)
        ret.COMPONENTS = ['metadata', 'sequences', 'science', 'target']

        return ret
