"""
Provides utility functions for setting up a shared socket server for all events.
Could just as easily use Pipes, or RPC, or any other IPC standard, but sockets
are nice since the code is easily understood by anyone with web socket experience
"""

from multiprocessing import Pipe
import socket
from _thread import start_new_thread

class PipeServer:

    def __init__(self, pipe, logger):

        # pipe_out is what we use, pipe_in is what we give to someone else to use
        self.pipe = pipe
        self.logger = logger

        # put the external pipe in the client list so things get broadcasted
        self.clients = [self.pipe]


    def start(self):
        # Start the event loop
        while True:
            
            # what messages need to be sent out
            to_send = []
            
            # Handle messages from outside the EE
            try:
                if self.pipe.poll():
                    incoming_message = self.pipe.recv()
                    to_send.append((incoming_message, 0))

            except Exception as e:
                self.logger.error(e.with_traceback())

            # Handle messages from the events
            for i, client in enumerate(self.clients):
                # This is not optimal. We could use `select` to do this at the OS 
                # level, but for our uses this should be sufficient.

                try:

                    if client.poll():
                        message = client.recv()
                        to_send.append((message, i))

                except Exception as e:
                    self.logger.error(e.with_traceback())

            # Send out the queued messages
            # It's a for loop in a for loop. I know it isn't efficient.
            # But, there shouldn't ever be more than ~10 clients, and one
            # message per, at worst. 100 is fine...
            for message in to_send:
                for i, client in enumerate(self.clients):
                    # Make sure we don't broadcast to ourselves
                    if i != message[1]:
                        client.send(message)