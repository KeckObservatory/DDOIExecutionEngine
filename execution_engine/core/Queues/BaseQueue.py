import logging
import os
from collections import deque
import json

from .QueueItem import QueueItem

class DDOIBaseQueue():

    def __init__(self, item_type, logger, name=None) -> None:
        ## Initialize Back-End Properties
        self.pid = os.getpid()
        self.name = name if name else str(self.pid)

        if issubclass(item_type, QueueItem):
            self.item_type = item_type
        else:
            raise TypeError("item_type must be a subclass of QueueItem")

        ## Set up logger
        self.logger = logging.getLogger(self.name)

        ## Set up actual queue
        self.queue = deque()

        # List to store all items that have been pulled from the queue
        self.boneyard = list()


    def __len__(self) -> int:
        """Gets the length of the queue

        Returns
        -------
        int
            Length of the queue
        """
        return len(self.queue)

    def put_one(self, element) -> None:
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
        if isinstance(element, self.item_type):
            self.queue.append(element)
            raise TypeError(f"Expected {self.item_type} but got {type(element)}")

    def put_many(self, elements) -> None:
        """Insert more than one QueueItem into the queue

        Parameters
        ----------
        elements : list
            Python list of QueueItems

        Raises
        ------
        TypeError
            Raised if any of the input elements are not QueueItem's
        """
        for i in elements:
            if not isinstance(i, self.item_type):
                raise TypeError(f"Expected {self.item_type} but got {type(i)}")
        for i in elements:
            self.queue.append(i)


    def get(self) -> QueueItem:
        """Gets and removes the first item from the queue and returns it.

        Returns
        -------
        QueueItem
            first item in the queue
        """
        item = self.queue.popleft()
        self.boneyard.append(item)
        return item

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
            if not isinstance(i, self.item_type):
                raise TypeError(f"Expected {self.item_type}, but got {type(i)}")
        
        # Save the original length
        original_len = len(self)

        # Clear the queue
        self.queue.clear()

        # Add the new contents
        for i in new_contents:
            self.queue.append(i)
        
        return original_len - len(self)
        

    def get_queue_as_list(self):
        """Gets the contents of the queue as a list of dictionaries

        Returns
        -------
        list
            List of dictionaries created from QueueItem.as_dict() calls
        """
        l = [i.as_dict() for i in list(self.queue)]
        return l

