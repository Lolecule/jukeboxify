from flask import Flask, jsonify, request
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

if __name__ == "__main__":
    app.debug = True
    app.run()
