import QueueItem

class ObservingBlockItem(QueueItem):

    def __init__(self, ob_dict) -> None:
        super().__init__()
        self.ob = ob_dict
        self._parse_ob()

    def _parse_ob(self) -> None:
        self.metadata = self.ob.get('metadata', None)
        self.acquisition = self.ob.get('acquisition', None)
        self.sequences = self.ob.get('observations', None)
        self.target = self.ob.get('target', None)
        self.COMPONENTS = ['metadata', 'sequences', 'science', 'target']