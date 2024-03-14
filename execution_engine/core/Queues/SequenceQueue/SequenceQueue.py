class SequenceQueue():
    def __init__(self, logger=None, name=None) -> None:
        self.selectedSequenceNumber = 0
        self.sequences = []
        self.boneyard = []
