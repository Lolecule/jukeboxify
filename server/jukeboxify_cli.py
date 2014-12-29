import zmq
from getpass import getpass

def jsonify(text_command):
    tokens = text_command.split()
    args = []
    if len(tokens) > 1:
      args = tokens[1:]
    json = { "opcode": tokens[0], "args": args }
    return json

def login_prompt():
    login_payload = {
        "opcode": "login",
        "args": [
            raw_input("Username: "),
            getpass()
        ]
    }
    return login_payload

def enter_repl(socket):
    print("Jukeboxify CLI - Developed by Steve Parrington")
    try:
        while True:
            text_command = raw_input("> ")
            json = jsonify(text_command)
            if json['opcode'] == 'exit':
                raise KeyboardInterrupt
            elif json['opcode'] == 'login':
                json = login_prompt()
            socket.send_json(json)
            print(socket.recv_json()["message"])
    except KeyboardInterrupt:
        print("Exiting Jukeboxify CLI...")
        socket.disconnect('tcp://127.0.0.1:7890')

def main():
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:7890')
    enter_repl(socket)

if __name__ == '__main__':
    main()
