from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/open_lock', methods=['GET'])
def open_lock():
    
    return jsonify(message="La cerradura se ha abierto")

@app.route('/close_lock', methods=['GET'])
def close_lock():
    
    return jsonify(message="La cerradura se ha cerrado")

@app.route('/photo', methods=['GET'])
def photo():
    
    return jsonify(message="Foto tomada")

if __name__ == '__main__':
    app.run(debug=True)
