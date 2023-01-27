import socketio
from core.ExecutionEngine import ExecutionEngine 
import pdb
import logging
from core.Queues.BaseQueue import DDOIBaseQueue
from core.Queues.ObservingQueue.ObservingBlockItem import ObservingBlockItem
from core.Queues.SequenceQueue.SequenceItem import SequenceItem
from core.Queues.EventQueue.EventItem import EventItem

def main():

    ee = ExecutionEngine()
    host = '0.0.0.0'
    port = '50007'
    url = 'http://' + host + ':' + port

    sio = socketio.Client()

    @sio.event
    def connect():
        logging.info('connection established')

    @sio.event
    def sequence_queue_to_xcute(data):
        logging.info('sequence_queue_to_xcute recieved', data)
        seqDict = data.get('sequence_queue')
        newSequenceQueue = [ SequenceItem.from_sequence(x) for x in seqDict ]
        ee.seq_q.set_queue(newSequenceQueue)

    @sio.event
    def event_queue_to_xcute(data):
        logging.info('event_queue_to_xcute recieved', data)
        eventDict = data.get('event_queue')
        #TODO: straighten out event item (does not use from_sequence)
        newEventQueue = [ EventItem.from_sequence(x) for x in eventDict ]
        ee.ev_q.set_queue(newEventQueue)
        logging.info('event_queue.get_queue_as_json()')
        logging.info(ee.ev_q.get_queue_as_json())

    @sio.event
    def ob_to_xcute(data):
        newOB = data.get("ob")
        if bool(newOB):
            obItem = ObservingBlockItem.from_DICT(newOB)
            ee.obs_q.set_queue([obItem])

    @sio.event
    def task_to_xcute(data):
        logging.info('task_to_excute recieved', data)

    @sio.event
    def disconnect():
        logging.info('disconnected from server')

    sio.connect(url)
    sio.wait()

if __name__ == "__main__":
    main()
