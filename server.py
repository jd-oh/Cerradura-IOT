# Importar las bibliotecas necesarias
from threading import Thread
from time import sleep
from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
import time
import requests

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Crear una lista para guardar los mensajes de alerta
alertas_log = []

# Variables globales para el estado de la cerradura y los tiempos de alerta
lock_open = False
lock_open_time = None
last_alert_time = None
alert_delay = 30
alert_interval = 20

# Función que se ejecuta en un hilo separado para comprobar el estado de la cerradura
def check_lock_status():
    global lock_open
    global lock_open_time
    global last_alert_time
    global alert_interval
    while True:
        if lock_open and time.time() - lock_open_time > alert_delay:
            if last_alert_time is None or time.time() - last_alert_time > alert_interval:
                tiempo_abierta = int(time.time() - lock_open_time)
                alerta = "La cerradura ha estado abierta por más de {} segundos: ".format(tiempo_abierta) + time.strftime("%d/%m/%y") + " a las " + time.strftime("%H:%M:%S")
                alertas_log.append(alerta)
                cliente.publish(topic_alertas, alerta)
                last_alert_time = time.time()
        sleep(1)

# Callback para cuando se publica un mensaje MQTT
def on_publish(client,userdata,result):
    print("conexión exitosa")
    print("Client {}\n UserData {}\n Result".format(client,userdata,result))

# Callback para cuando se recibe un mensaje MQTT
def on_message(client, userdata, message):
    key, value = message.payload.decode().split(':')
    if key == 'Tiempo de alerta de cerradura abierta ha cambiado a':
        global alert_delay
        alert_delay = int(value)
    elif key == 'Tiempo entre alertas de cerradura abierta ha cambiado a':
        global alert_interval
        alert_interval = int(value)

# Ruta para abrir la cerradura
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

# Ruta para cerrar la cerradura
@app.route('/close_lock', methods=['GET'])
def close_lock():
    global lock_open
    lock_open = False
    alerta = "La cerradura se ha cerrado en la fecha: "+time.strftime("%d/%m/%y")+" a las "+time.strftime("%H:%M:%S")
    alertas_log.append(alerta)
    cliente.publish(topic, alerta)
    return jsonify(message="La cerradura se ha cerrado")

# Ruta para obtener el estado de la cerradura
@app.route('/lock_status', methods=['GET'])
def lock_status():
    global lock_open
    return jsonify(is_open=lock_open)

# Punto de entrada principal del programa
if __name__ == '__main__':
    # Iniciar el hilo que verifica el estado de la cerradura
    Thread(target=check_lock_status).start()

    # Configuración del cliente MQTT
    #broker = "91.121.93.94"
    broker = "192.168.43.252"
    port = 1883
    topic = "CERRADURAIOT"
    topic_alertas = "CERRADURAIOT/ALERTAS"

    # Crear un cliente MQTT
    cliente = mqtt.Client()
    username="JuanDavid"
    password="prueba"

    cliente.username_pw_set(username, password)
    # Configurar las funciones de callback
    cliente.onpublish = on_publish
    cliente.on_message = on_message

    # Conectar al broker y suscribirse al topic
    cliente.connect(broker,port,keepalive=60)
    cliente.subscribe('CERRADURAIOT/CONFIG')

    # Iniciar el loop del cliente MQTT
    cliente.loop_start()

    # Iniciar la aplicación Flask
    app.run(debug=True)
