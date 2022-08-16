import socketio

def define_routes(sio):
    @sio.event
    def connect():
        print('connection established')

    @sio.event
    def sequence_queue_to_xcute(data):
        print('sequence_queue_to_xcute recieved', data)

    @sio.event
    def event_queue_to_xcute(data):
        print('event_queue_to_xcute recieved', data)

    @sio.event
    def ob_to_xcute(data):
        print('ob_to_excute recieved', data)

    @sio.event
    def task_to_xcute(data):
        print('task_to_excute recieved', data)

    @sio.event
    def disconnect():
        print('disconnected from server')

def main():
    
    host = '0.0.0.0'
    port = '50007'
    url = 'http://' + host + ':' + port
    sio = socketio.Client(logger=True, engineio_logger=True)
    define_routes(sio)
    sio.connect(url)
    sio.wait()

if __name__ == "__main__":
    main()