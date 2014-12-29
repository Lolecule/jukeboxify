import threading
import Queue
import spotify
import zmq
import constants
import os.path
import json
import time

class Controller:

    def __init__(self):
        self.listening = True
        self.active = True
        self.session = spotify.Session()
        self.register_callbacks()
        self.event_loop = spotify.EventLoop(self.session)
        self.event_loop.start()

        try:
            if os.path.isfile('.jukeboxify'):
                with open('.jukeboxify', 'r') as fd:
                    credentials = json.load(fd)
                self.session.login(credentials['username'],
                        blob=str(credentials['blob']))
            else:
                print "Log in failed! Set up some credentials"
        except spotify.error.LibError:
            print "Log in failed! Set up some credentials"

        print "Opening socket..."
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind('tcp://127.0.0.1:7890')
        print "Socket open on port 7890"

    def run(self):
        try:
            while self.active:
                if self.listening:
                    self.execute_command()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        print "Shutting down..."
        self.socket.unbind('tcp://127.0.0.1:7890')
        self.session.logout()
        time.sleep(5)

    def listen(self):
        json = self.socket.recv_json()
        self.listening = not self.listening
        assert self.listening == False
        return json

    def reply(self, response):
        self.socket.send_json(response)
        self.listening = not self.listening
        assert self.listening == True

    def execute_command(self):
        valid_opcodes = ('login')
        try:
            command = self.listen()
            if command["opcode"] in valid_opcodes:
                getattr(self, command["opcode"])(*command["args"])
            else:
                self.reply(constants.INVALID_COMMAND)
        except KeyError:
            self.reply(constants.INVALID_COMMAND)

    def login(self, username, password):
        self.session.login(username, password, remember_me=True)

    def login_callback(self, session, error_type):
        if self.listening:
            if error_type == spotify.ErrorType.OK:
                print "Logged in!"
            else:
                print "Log in failed!"
        else:
            if error_type == spotify.ErrorType.OK:
                self.reply(constants.LOGIN_SUCCESS)
            else:
                self.reply(constants.LOGIN_FAILED)

    def logout_callback(self, session):
        print "Logged out!"

    def credentials_blob_callback(self, session, blob):
        credentials = {
            'username': self.session.user_name,
            'blob': blob
        }
        with open('.jukeboxify', 'w') as fd:
            json.dump(credentials, fd)

    def register_callbacks(self):
        callbacks = {
            'LOGGED_IN': self.login_callback,
            'LOGGED_OUT': self.logout_callback,
            'CREDENTIALS_BLOB_UPDATED': self.credentials_blob_callback
        }
        for name in callbacks:
            self.session.on(getattr(spotify.SessionEvent, name),
                    callbacks[name])

if __name__ == '__main__':
    Controller().run()
