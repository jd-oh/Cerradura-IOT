from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

#table ="CREATE TABLE registros(fecha varchar(255),accion varchar(255));"
#cursor.execute(table)


@app.route('/abrir', methods=['GET'])
def abrir():
    fecha = str(datetime.now())
    conn = sqlite3.connect('registros.db',check_same_thread=False) 
    cursor = conn.cursor() 

    cursor.execute("INSERT INTO registros VALUES (?,?)",(fecha,"abrir"))
    conn.commit()
    conn.close()
    return jsonify(message="abierto")
@app.route('/cerrar', methods=['GET'])
def cerrar():
    fecha = str(datetime.now())
    conn = sqlite3.connect('registros.db',check_same_thread=False) 
    cursor = conn.cursor() 

    cursor.execute("INSERT INTO registros VALUES (?,?)",(fecha,"cerrar"))
    conn.commit()
    conn.close()
    return jsonify(message="cerrado")
app.run(port=5001,host="0.0.0.0",debug=True)

