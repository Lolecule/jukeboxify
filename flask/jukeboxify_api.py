from flask import Flask, jsonify, request, make_response
import jukeboxify_socket

app = Flask(__name__)

@app.route("/queue", methods=["POST"])
def add_to_queue():
    json = request.get_json()
    response = jukeboxify_socket.send({
        "opcode": "add_to_queue",
        "args": json["tracks"]
    })
    return jsonify(response)

@app.route("/queue", methods=["GET"])
def get_queue():
    response = jukeboxify_socket.send({
        "opcode": "get_queue",
        "args": []
    })
    return jsonify(response)

@app.route("/actions/play", methods=["PUT"])
def play():
    response = jukeboxify_socket.send({
        "opcode": "play",
        "args": []
    })
    return make_response('', 204)

@app.route("/actions/pause", methods=["PUT"])
def pause():
    response = jukeboxify_socket.send({
        "opcode": "pause",
        "args": []
    })
    return make_response('', 204)

@app.route("/actions/next", methods=["POST"])
def next():
    jukeboxify_socket.send({
        "opcode": "next",
        "args": []
    })
    return make_response('', 204)

@app.route("/actions/prev", methods=["POST"])
def prev():
    jukeboxify_socket.send({
        "opcode": "prev",
        "args": []
    })
    return make_response('', 204)

if __name__ == "__main__":
    app.debug = True
    app.run()
