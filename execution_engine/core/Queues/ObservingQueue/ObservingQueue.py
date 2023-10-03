class ObservingQueue():

    def __init__(self, logger=None, interface=None, name=None) -> None:
        self.submitted_ob_id = ""
        self.obIds = []
        self.boneyard = []