"""
This class provides a central place to store OBs for the Execution Engine.
Since the Execution Engine uses one instance of this vault in all locations and
at all levels, if an OB is changed here, those changes will propogate out to all
queues and QueueItems automatically. 
"""

import OBDM

class Vault():     

    def __init__(self):

        self.OBs = {}

    def add_ob(self, json):
        id = json['_ob_id']
        if id in self.OBs.keys():
            raise KeyError(f"Entry with id {id} already exists in vault!")
        
        self.OBs.update({
            id : OBDM(json)
        })

    def remove_ob(self, ob_id):
        self.OBs.pop(ob_id)

    def update_ob(self, json):
        id = json['_ob_id']
        if not id in self.OBs.keys():
            raise KeyError(f"No OB with ob_id = {id} found to update!")
        self.OBs.update({
            id : OBDM(json)
        })

    def contains_ob_id(self, ob_id):
        return ob_id in self.OBs.keys()