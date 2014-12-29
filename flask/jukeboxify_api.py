from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/queue", methods=["POST"])
def add_to_queue():
    json = request.get_json()
    response = JukeboxifySocket.send({
        "opcode": "add_to_queue",
        "args": json["tracks"]
    })
    return jsonify(response)

if __name__ == "__main__":
    app.run()
