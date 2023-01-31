import json
import pdb
from ..QueueItem import QueueItem

class ObservingBlockItem(QueueItem):

    def __init__(self, OB) -> None:
        super().__init__()
        self.OB = OB
    #     self.metadata = None
    #     self.acquisition = None
    #     self.sequences = None
    #     self.target = None
    #     self.COMPONENTS = None

    # @staticmethod
    # def create_observing_block_item(ob):
    #     ret = ObservingBlockItem()
    #     ret.metadata = ob.get('metadata', None)
    #     ret.acquisition = ob.get('acquisition', None)
    #     ret.sequences = ob.get('observations', None)
    #     ret.target = ob.get('target', None)
    #     ret.COMPONENTS = ['metadata', 'sequences', 'science', 'target']
    #     return ret

    # @classmethod
    # def from_DICT(cls, ob):
    #     ret = cls.create_observing_block_item(ob)
    #     return ret
       

    # @classmethod
    # def from_JSON(cls, filename):
    #     ob = json.load(filename)
    #     ret = cls.create_observing_block_item(ob)
    #     return ret
