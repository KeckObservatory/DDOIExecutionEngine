from asyncio import QueueEmpty
import logging
import os
import queue
import json

import QueueItem

class DDOIBaseQueue():

    # class ExternalInterface():

    #     def __init__(self, QM_IP, QM_PORT) -> None:
    #         self.server_ip = QM_IP
    #         self.server_port = QM_PORT
        

    #     def send_data(data) -> None:
    #         """Sends arbitrary string data over the connection

    #         Parameters
    #         ----------
    #         data : str
    #             Data to be sent over the connection
    #         """
    #         pass

    #     def read_data() -> str:
    #         """Reads data from the connection

    #         Returns
    #         -------
    #         str
    #             Data read over the connection
    #         """
    #         return "data"

    def __init__(self, name = None) -> None:
        ## Initialize Back-End Properties
        self.pid = os.getpgid()
        self.name = name if name else str(self.pid)

        # # Set up the multiprocess (or socket) listener here
        # self.connection = self.ExternalInterface(QM_IP, QM_PORT)

        ## Set up logger
        self.logger = logging.getLogger(self.name)

        ## Set up actual queue
        self.queue = queue.Queue()

    def __len__(self) -> int:
        """Gets the length of the queue

        Returns
        -------
        int
            Length of the queue
        """
        return len(self.queue)

    def put(self, element) -> None:
        """Adds a QueueItem element to the queue

        Parameters
        ----------
        element : QueueItem
            Element to be added to the queue

        Raises
        ------
        TypeError
            Raised if element is not a QueueItem
        """
        if isinstance(element, QueueItem):
            self.queue.put(element)
        else:
            raise TypeError(f"Expected a QueueItem but got {type(element)}")

    def get(self) -> QueueItem:
        """Pulls the first item from the queue and returns it

        Returns
        -------
        QueueItem
            first item in the queue
        """
        return self.queue.get()

    def set_queue(self, new_contents) -> int:
        """Irreversibly empties the queue and refills it with the contents of
        list, and returns difference in the number of elements in the queue. For
        example:

        contents = [item1, item2, item3, item4]

        q = BaseQueue()
        for i in contents:
            q.put(i)
        
        q.as_list()
        # [item1, item2, item3, item4]

        q.set_queue([item2, item3, item4])
        # -1

        q.as_list()
        # [item2, item3, item4]

        Parameters
        ----------
        new_contents : list of QueueItem
            QueueItem's to populate this queue with

        Returns
        -------
        int
            Difference in the number of elements in the original and updated 
            queue
        """
        
        # Check that all inputs are QueueItems
        for i in new_contents:
            if not isinstance(i, QueueItem):
                raise TypeError(f"Expected QueueItem, but got {type(i)}")
        
        # Save the original length
        original_len = len(self)

        # Clear the queue
        self.queue.clear()

        # Add the new contents
        for i in new_contents:
            self.put(i)
        
        return original_len - len(self)
        

    def get_queue_as_json(self) -> str:
        """Gets the contents of the queue as a json list. Each QueueItem is 
        converted into a string for serialization

        Returns
        -------
        str
            JSON list containing the contents of the queue
        """
        l = [str(i) for i in list(self.queue)]
        return json.dumps(l)

    # def send_queue(self) -> None:
    #     """Sends a JSONified version of the queue over the ExternalInterface
    #     """
    #     self.connection.send_data(self._encode_queue_as_json())
