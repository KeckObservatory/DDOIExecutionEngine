class QueueItem:

    def __init__(self, content):
        self.id = "UID"
        self.content = content
        
    def __str__(self) -> str:
        return self.id + str(self.content)