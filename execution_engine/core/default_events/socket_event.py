from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
import time
import datetime
import os


class socket_event(TranslatorModuleFunction):
    """Waiting event. This event will wait until it recieves a kill message over
    a provided connection.

    Args
    ----
    connection : multiprocessing.Connection
        Multiprocessing connection object to read from
    timeout : int
        How long this event should wait before automatically returning. If negative,
        infinite timeout
    kill_message : str
        String that should kill this event
    """

    @classmethod
    def pre_condition (cls, args, logger, cfg):
        return True

    @classmethod
    def perform (cls, args, logger, cfg):
        connection = args.get('connection', None)
        timeout = args.get('timeout')
        if connection:
            start_time = datetime.datetime.utcnow()
            # Listen on that port until we get the message we expect, with a timeout
            while True:
                time.sleep(.5)
                if timeout > 0 and datetime.datetime.utcnow() - start_time > timeout:
                    raise TimeoutError(f"Exceeded {timeout} s timeout set for event")
                
                if connection.poll():
                    message = connection.read()
                    logger.debug(f"Read message {message} at {os.getpid()}")

                    if message and message == args.get('kill_message'):
                        logger.info(f"Message recieved matches {os.getpid()}'s kill code. Breaking...")
                        break
        else:
            if connection is None:
                raise KeyError("No connection object in args.")
            else:
                raise ConnectionError("Failed to connect to event server")
               

    @classmethod
    def post_condition (cls, args, logger, cfg):
        return True