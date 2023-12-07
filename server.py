from threading import Thread
from time import sleep
from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import time
import requests

app = Flask(__name__)

# Crear una lista para guardar los mensajes de alerta
alertas_log = []


lock_open = False
lock_open_time = None
last_alert_time = None
alert_delay = 30
alert_interval = 20

def check_lock_status():
    global lock_open
    global lock_open_time
    global last_alert_time
    global alert_interval  # Asegúrate de tener esta variable global
    while True:
        if lock_open and time.time() - lock_open_time > alert_delay:
            if last_alert_time is None or time.time() - last_alert_time > alert_interval:
                tiempo_abierta = int(time.time() - lock_open_time)
                alerta = "La cerradura ha estado abierta por más de {} segundos: ".format(tiempo_abierta) + time.strftime("%d/%m/%y") + " a las " + time.strftime("%H:%M:%S")
                alertas_log.append(alerta)
                cliente.publish(topic_alertas, alerta)
                last_alert_time = time.time()
        sleep(1)


def on_publish(client,userdata,result):
    print("conexión exitosa")
    print("Client {}\n UserData {}\n Result".format(client,userdata,result))

def on_message(client, userdata, message):
    key, value = message.payload.decode().split(':')
    if key == 'Tiempo de alerta de cerradura abierta ha cambiado a':
        global alert_delay
        alert_delay = int(value)
    elif key == 'Tiempo entre alertas de cerradura abierta ha cambiado a':
        global alert_interval
        alert_interval = int(value)



@app.route('/open_lock', methods=['GET'])
def open_lock():
    global lock_open
    global lock_open_time
    lock_open = True
    lock_open_time = time.time()
    alerta = "La cerradura se ha abierto en la fecha: "+time.strftime("%d/%m/%y")+" a las "+time.strftime("%H:%M:%S")
    alertas_log.append(alerta)
    cliente.publish(topic, alerta)
    return jsonify(message="La cerradura se ha abierto")

@app.route('/close_lock', methods=['GET'])
def close_lock():
    global lock_open
    lock_open = False
    alerta = "La cerradura se ha cerrado en la fecha: "+time.strftime("%d/%m/%y")+" a las "+time.strftime("%H:%M:%S")
    alertas_log.append(alerta)
    cliente.publish(topic, alerta)
    return jsonify(message="La cerradura se ha cerrado")

@app.route('/lock_status', methods=['GET'])
def lock_status():
    global lock_open
    return jsonify(is_open=lock_open)


if __name__ == '__main__':
    # Iniciar el hilo que verifica el estado de la cerradura
    Thread(target=check_lock_status).start()

    broker = "91.121.93.94"
    port = 1883
    topic = "CERRADURAIOT"
    topic_alertas = "CERRADURAIOT/ALERTAS"

    cliente = mqtt.Client()
    cliente.onpublish = on_publish
    cliente.connect(broker,port,keepalive=60)

    cliente.on_message = on_message
    cliente.subscribe('CERRADURAIOT/CONFIG')


    cliente.loop_start()

    app.run(debug=True)
