# Importar las bibliotecas necesarias
import telebot
import requests
import subprocess
import paho.mqtt.client as mqtt

# Token del bot de Telegram
BOT_TOKEN = '6965114657:AAEg9K0K2xYrrz_M3y4P3TXktaPRcLyTGO0'  

# Crear una instancia del bot de Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Crear un cliente MQTT
cliente = mqtt.Client()

# Conectar el cliente MQTT al broker
cliente.connect('91.121.93.94', 1883, 60)

# Iniciar el loop del cliente MQTT para procesar los mensajes y mantener la conexión
cliente.loop_start()

# Definir el topic MQTT para la configuración
topic="CERRADURAIOT/CONFIG"

# Manejador para el comando /iniciar
@bot.message_handler(commands=['iniciar'])
def send_welcome(message):
    # Crear un teclado inline con botones para abrir y cerrar la cerradura, y tomar una foto
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Abrir cerradura', callback_data='open_lock'),
        telebot.types.InlineKeyboardButton('Cerrar cerradura', callback_data='close_lock'),
        telebot.types.InlineKeyboardButton('Tomar foto', callback_data='photo')
    )
    # Enviar un mensaje con el teclado inline
    bot.send_message(message.chat.id, 'Por favor elige:', reply_markup=keyboard)

# Manejador para el comando /ayuda
@bot.message_handler(commands=['ayuda'])
def send_help(message):
    # Definir el texto de ayuda
    help_text = """
    Aquí están los comandos que puedes usar:
    - /iniciar: Inicia la interacción con el bot. Te muestra un menú con las opciones disponibles.
    - /tiempoParaAlertar <segundos>: Cambia el tiempo después del cual se envían las alertas cuando la cerradura está abierta.
    - /tiempoEntreAlertas <segundos>: Cambia el intervalo de tiempo entre las alertas.
    """
    # Enviar el texto de ayuda
    bot.reply_to(message, help_text)

# Manejador para las acciones de los botones del teclado inline
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'open_lock':
        # Verificar si la cerradura ya está abierta
        lock_status = requests.get('http://localhost:5000/lock_status').json()
        if lock_status['is_open']:
            bot.answer_callback_query(call.id, 'La cerradura ya está abierta')
        else:
            response = requests.get('http://localhost:5000/open_lock')
            bot.answer_callback_query(call.id, 'La cerradura se ha abierto')
    elif call.data == 'close_lock':
        # Verificar si la cerradura ya está cerrada
        lock_status = requests.get('http://localhost:5000/lock_status').json()
        if not lock_status['is_open']:
            bot.answer_callback_query(call.id, 'La cerradura ya está cerrada')
        else:
            response = requests.get('http://localhost:5000/close_lock')
            bot.answer_callback_query(call.id, 'La cerradura se ha cerrado')
    elif call.data == 'photo':
        # Tomar una foto y enviarla
        subprocess.run(["termux-camera-photo","-c", "1","foto.jpg"])
        
        #reducir tamaño
        subprocess.run(["mogrify" ,"-quality" ,"60","foto.jpg"])
        
        bot.send_photo(call.message.chat.id, photo=open('foto.jpg', 'rb'))
        bot.answer_callback_query(call.id, 'Se ha enviado la foto')

# Manejador para el comando /tiempoParaAlertar
@bot.message_handler(commands=['tiempoParaAlertar'])
def set_alert_delay(message):
    # El primer argumento del mensaje es el comando, el segundo es el valor
    _, value = message.text.split()
    # Publicar el nuevo valor en el topic de configuración 
    cliente.publish(topic, 'Tiempo de alerta de cerradura abierta ha cambiado a:{}'.format(value))
    # Confirmar al usuario que el valor ha sido cambiado en el chat
    bot.reply_to(message, 'Se ha configurado el retraso de la alerta a {} segundos'.format(value))

# Manejador para el comando /tiempoEntreAlertas
@bot.message_handler(commands=['tiempoEntreAlertas'])
def set_alert_interval(message):
    # El primer argumento del mensaje es el comando, el segundo es el valor
    _, value = message.text.split()
    # Publicar el nuevo valor en el topic de configuración
    cliente.publish(topic, 'Tiempo entre alertas de cerradura abierta ha cambiado a:{}'.format(value))
    # Confirmar al usuario que el valor ha sido cambiado en el chat
    bot.reply_to(message, 'Se ha configurado el intervalo de la alerta a {} segundos'.format(value))

# Iniciar el bot
bot.polling()
