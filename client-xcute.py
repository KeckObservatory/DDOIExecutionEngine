import socketio
from ExecutionEngine import *

from Queues.BaseQueue import DDOIBaseQueue
from Queues.ObservingBlockItem import ObservingBlockItem
from Queues.SequenceItem import SequenceItem
from Queues.EventItem import EventItem

def main():
    
    host = '0.0.0.0'
    port = '50007'
    url = 'http://' + host + ':' + port

    observing_queue = DDOIBaseQueue(ObservingBlockItem)
    sequence_queue = DDOIBaseQueue(SequenceItem)
    event_queue = DDOIBaseQueue(EventItem)

    @sio.event
    def connect():
        print('connection established')

    @sio.event
    def sequence_queue_to_xcute(data):
        print('sequence_queue_to_xcute recieved', data)
        seqDict= data.get('sequence_queue')
        newSequenceQueue = [ SequenceItem.from_sequence(x) for x in seqDict ]
        sequence_queue.set_queue(newSequenceQueue)

    @sio.event
    def event_queue_to_xcute(data):
        print('event_queue_to_xcute recieved', data)
        eventDict = data.get('event_queue')
        newEventQueue = [ EventItem.from_sequence(x) for x in eventDict ]
        event_queue.set_queue(newEventQueue)
        print('\nevent_queue.get_queue_as_json()\n')
        print(event_queue.get_queue_as_json())

    @sio.event
    def ob_to_xcute(data):
        print('ob_to_excute recieved', data)
        newOB = data.get("ob")
        obItem = ObservingBlockItem.from_JSON(newOB)
        observing_queue.seq_queue(obItem)

    @sio.event
    def task_to_xcute(data):
        print('task_to_excute recieved', data)

    @sio.event
    def disconnect():
        print('disconnected from server')

    #sio = socketio.Client(logger=True, engineio_logger=True)
    sio = socketio.Client()
    sio.connect(url)
    sio.wait()

if __name__ == "__main__":
    main()