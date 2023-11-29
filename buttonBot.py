import telebot
import requests
import subprocess

BOT_TOKEN = '6965114657:AAEg9K0K2xYrrz_M3y4P3TXktaPRcLyTGO0'  
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        
        telebot.types.InlineKeyboardButton('Abrir cerradura', callback_data='open_lock'),
        telebot.types.InlineKeyboardButton('Cerrar cerradura', callback_data='close_lock'),
        telebot.types.InlineKeyboardButton('Tomar foto', callback_data='photo')
        
    )
    bot.send_message(message.chat.id, 'Por favor elige:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'open_lock':
        response = requests.get('http://localhost:5000/open_lock')
        bot.answer_callback_query(call.id, 'La cerradura se ha abierto')
    elif call.data == 'close_lock':
        response = requests.get('http://localhost:5000/close_lock')
        bot.answer_callback_query(call.id, 'La cerradura se ha cerrado')
    elif call.data == 'photo':
        #print(call.message.chat.id)
        #return
        subprocess.run(["termux-camera-photo","-c", "1","foto.jpg"])
        subprocess.run(["mogrify" ,"-quality" ,"60","foto.jpg"])
        bot.send_photo(call.message.chat.id, photo=open('foto.jpg', 'rb'))
        bot.answer_callback_query(call.id, 'Se ha enviado la foto')
        #return "enviado"
        #response = requests.get('http://localhost:5000/photo')
        #bot.answer_callback_query(call.id, 'Foto tomada')

bot.polling()
