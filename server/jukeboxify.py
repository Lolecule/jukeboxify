import threading
import Queue
import spotify
import zmq
import constants
import os.path
import json
import time

class Player:

    def __init__(self, session):
        self.queue = []
        self.cursor = None
        self.session = session
        self.midtrack = False
        self.playing = False
        self.audio = spotify.AlsaSink(self.session)
        self.event_loop = spotify.EventLoop(self.session)
        self.event_loop.start()

    def add_to_queue(self, *track_ids):
        for track_id in track_ids:
            self.queue.append(self.session.get_track(track_id).load())
        return self._as_json()

    def get_queue(self):
        return self._as_json()

    def play(self):
        self._load_next_track()
        self._play_track()
        return {}

    def pause(self):
        self.session.player.pause()
        self.playing = False
        return {}

    def next(self):
        self._load_next_track(ignore_if_midtrack=False)
        self._play_track()
        return {}

    def prev(self):
        self._load_next_track(ignore_if_midtrack=False, forwards=False)
        self._play_track()
        return {}

    def end_of_track_callback(self, session):
        self.next()

    def _play_track(self):
        self.session.player.play()
        self.midtrack = True
        self.playing = True

    def _load_next_track(self, ignore_if_midtrack=True, forwards=True):
        if ignore_if_midtrack and self.midtrack:
            return
        else:
            if forwards:
                self._increment_cursor()
            else:
                self._decrement_cursor()
            if self.midtrack:
                self.session.player.pause()
                self.session.player.unload()
            track = self.queue[self.cursor]
            self.session.player.load(track)

    def _increment_cursor(self):
        if self.cursor is None:
            self.cursor = 0
        else:
            self.cursor += 1
            if self.cursor >= len(self.queue):
                self.cursor = 0

    def _decrement_cursor(self):
        if self.cursor is None:
            self.cursor = 0
        else:
            self.cursor -= 1
            if self.cursor < 0:
                self.cursor = len(self.queue) - 1
                
    def _as_json(self):
        tracklist = [self._human_readable_track_name(track) for track in self.queue]
        queue_as_json = {
            'current_track': self.cursor,
            'queue': tracklist
        }
        return queue_as_json

    def _human_readable_track_name(self, track):
        artists = track.artists
        artist_names = [artist.load().name for artist in artists]
        return track.name + " - " + ", ".join(artist_names)

class Controller:

    def __init__(self):
        self.listening = True
        self.active = True
        self.playing = False
        self.midtrack = False
        self.cursor = 0
        self.session = spotify.Session()
        self.player = Player(self.session)
        self.register_callbacks()

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
        local_opcodes = ('login')
        player_opcodes = ('add_to_queue', 'get_queue', 'play', 'pause', 'next', 'prev')
        try:
            command = self.listen()
            if command["opcode"] in local_opcodes:
                response = getattr(self, command["opcode"])(*command["args"])
            elif command["opcode"] in player_opcodes:
                response = getattr(self.player, command["opcode"])(*command["args"])
            else:
                response = constants.INVALID_COMMAND
            self.reply(response)
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
            'CREDENTIALS_BLOB_UPDATED': self.credentials_blob_callback,
            'END_OF_TRACK': self.player.end_of_track_callback
        }
        for name in callbacks:
            self.session.on(getattr(spotify.SessionEvent, name),
                    callbacks[name])

if __name__ == '__main__':
    Controller().run()
