from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
import time
import datetime
import os


class SocketEvent(TranslatorModuleFunction):

    @classmethod
    def pre_condition (cls, args, logger, cfg):
        return True

    @classmethod
    def perform (cls, args, logger, cfg):
        connection = args.get('port', None)
        timeout = args.get('timeout')
        if connection:
            start_time = datetime.datetime.utcnow()
            # Listen on that port until we get the message we expect, with a timeout
            while True:
                time.sleep(.5)
                if datetime.datetime.utcnow() - start_time > timeout:
                    raise TimeoutError(f"Exceeded {timeout} s timeout set for event")
                
                if connection.poll():
                    message = connection.read()
                    logger.debug(f"Read message {message} at {os.getpid()}")

                    if message and message == args.get('message'):
                        logger.info(f"Message recieved matches {os.getpid()}'s kill code. Breaking...")
                        break
        else:
            raise ConnectionError("Failed to connect to event server")
               

    @classmethod
    def post_condition (cls, args, logger, cfg):
        return True