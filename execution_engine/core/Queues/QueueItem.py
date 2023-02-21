import uuid

class QueueItem:

    def __init__(self):
        self.id = uuid.uuid4().hex

    def as_dict(self):
        raise NotImplementedError
        