import QueueItem

class ObservingBlockItem(QueueItem):

    def __init__(self, ob_dict) -> None:
        self.ob = ob_dict
        self._parse_ob()

    def _parse_ob(self) -> None:
        """Init helper function
        """
        self.metadata = self.ob.get('metadata', None)
        self.acquisition = self.ob.get('acquisition', None)
        self.sequences = self.ob.get('sequences', None)
        self.target = self.ob.get('target', None)
        self.COMPONENTS = ['metadata', 'sequences', 'science', 'target']