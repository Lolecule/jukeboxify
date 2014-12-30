import zmq

socket = None

def send(json_dict):
    socket = _get_socket()
    socket.send_json(json_dict)
    return socket.recv_json()

def _get_socket():
    global socket
    if socket is None:
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://127.0.0.1:7890')
    return socket
