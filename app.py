from flask import Flask, request, jsonify, url_for

app = Flask(__name__)

@app.route('/canchas', methods=['GET'])
def index():
    return "Hola mundo"

if __name__ == "__main__":
    app.run(port=8080, debug=True)