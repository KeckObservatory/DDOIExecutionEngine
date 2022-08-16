import socketio
from ExecutionEngine import *

def main():
    
    host = '0.0.0.0'
    port = '50007'
    url = 'http://' + host + ':' + port

    observing_queue = BaseQueue(ObservingBlockItem)
    sequence_queue = BaseQueue(SequenceItem)
    event_queue = BaseQueue(EventItem)

    @sio.event
    def connect():
        print('connection established')

    @sio.event
    def sequence_queue_to_xcute(data):
        print('sequence_queue_to_xcute recieved', data)
        newSequenceQueue = data.get('sequence_queue')
        sequence_queue.set_queue(newSequenceQueue)

    @sio.event
    def event_queue_to_xcute(data):
        print('event_queue_to_xcute recieved', data)
        newEventQueue = data.get('event_queue')
        event_queue.set_queue(newEventQueue)
        print('\nevent_queue.get_queue_as_json()\n')
        print(event_queue.get_queue_as_json())

    @sio.event
    def ob_to_xcute(data):
        print('ob_to_excute recieved', data)
        newOB = data.get("ob")
        observing_queue.seq_queue(newOB)

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