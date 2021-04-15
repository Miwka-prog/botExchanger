import random
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup as BS
import mysql.connector
bot = telebot.TeleBot(Token)
numberOfPurse = "GCZ456AYVGZKKUXZXICMT3PZ25SGPK3GK4QA2XEB3NTZHYS3N47NKN5Q"


mydb =mysql.connector.connect(
    user="root",
    passwd="21112002",
    port="30434",
    host="84.38.189.95",
    database="exchangeBot"
)
cursor = mydb.cursor()
cursor.execute("SELECT * FROM users ")
myresult = cursor.fetchall()
for x in myresult:
    print(x)

def  parsUAN():
    r1 = requests.get('https://ru.ratesviewer.com/chart/xlm-uah/year/')
    html1 = BS(r1.content, 'html.parser')
    tag1 = (html1.find("span", "rate-d"))
    UAN = float(tag1.text)
    return UAN+1.2


def  parsRUB():
    r = requests.get('https://ru.ratesviewer.com/chart/xlm-rub/year/')
    html = BS(r.content, 'html.parser')
    tag = (html.find("span", "rate-d"))
    RUB = float(tag.text)
    return RUB+3


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton("Обмен XLM")
    item2 = types.KeyboardButton("Проверить статус заявки")
    item3 = types.KeyboardButton("Служба поддержки")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите действие:".format(message.from_user, bot.get_me()), parse_mode = 'html', reply_markup = markup)


@bot.message_handler(content_types=['text'])
def buttons(message):
    if message.chat.type == 'private':
        if message.text == 'Обмен XLM':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("XLM > UAH Visa/Mastercard", callback_data='1')
            item2 = types.InlineKeyboardButton("XLM > RUB Visa/Mastercard", callback_data='2')
            item3 = types.InlineKeyboardButton("Назад", callback_data='3')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, '{0.first_name}, выбери действие.'.format(message.from_user), reply_markup=markup)
        elif message.text == 'Проверить статус заявки':
            forRequest(message)
        elif message.text == 'Служба поддержки':
            bot.send_message(message.chat.id, 'Служба технической поддержки работает круглосуточно, семь дней в неделю!\nДля обратной связи обращайтесь в поддержку - @xlm_support_619'.format(message.from_user))
        elif message.text != 'Служба поддержки' and message.text != 'Проверить статус заявки' and message.text != 'Обмен XLM':
            bot.send_message(message.chat.id, "{0.first_name}, нажми на кнопку.".format(message.from_user))
            welcome(message)


@bot.message_handler(func=lambda message: True)
def send_message(message, definition):
    bot.send_message(message.chat.id, definition.format(message.from_user))


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == '1':
        send_message(call.message,  "Курс на данный момент:\n"
                                    "1 XLM ->" + str(parsUAN()) + " UAN\n"
                                    "Введите сумму для обмена:")
        bot.register_next_step_handler(call.message, exchangeUAN)
    if call.data == '2':
        send_message(call.message,  "Курс на данный момент:\n"
                                    "1 XLM ->" + str(parsRUB()) + " RUB\n"
                                    "Введите сумму для обмена:")
        bot.register_next_step_handler(call.message, exchangeRUB)
    if call.data == '3':
        welcome(call.message)


def exchangeUAN(message):
   try:
        sumMoney = message.text
        resultExchangeUAN = round(parsUAN() * int(sumMoney))
        msg = send_message(message, "Отдав " + sumMoney + ", вы получите " + str(resultExchangeUAN) + "  UAN" + "\nВведите номер карты для получения средств: ")
        bot.register_next_step_handler(message, getNumberOfCard, sumMoney, str(resultExchangeUAN), "UAN")
   except Exception as e:
        bot.reply_to(message, 'oooops')
        welcome(message)


def exchangeRUB(message):
   try:
        sumMoney = message.text
        resultExchangeRUB = round(parsRUB() * int(sumMoney))
        msg = send_message(message, "Отдав " + sumMoney + ", вы получите " + str(resultExchangeRUB) + "  RUB" + "\nВведите номер карты для получения средств: ")
        bot.register_next_step_handler(message, getNumberOfCard, sumMoney, str(resultExchangeRUB), "RUB")
   except Exception as e:
        bot.reply_to(message, 'oooops')
        welcome(message)


def getNumberOfCard(message, sumMoney, resultChange, currency):
   try:
        numberOfCard = message.text
        x = len([i for i in numberOfCard if i.isdigit()])
        if x == 16:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Подтверждаю обмен")
            item2 = types.KeyboardButton("Назад")
            markup.add(item1, item2)
            bot.send_message(message.chat.id, 'Проверьте правильность данных:\nНомер карты: ' + numberOfCard + '\nОтдаёте: ' + sumMoney + " XLM\nПолучаете:"  + resultChange + " " + currency.format(message.from_user), reply_markup=markup)
            bot.register_next_step_handler(message, confirmExchange, str(sumMoney), numberOfCard, resultChange , currency)
        else:
            bot.send_message(message.chat.id, 'Неверный номер карты!')
            welcome(message)
   except Exception as e:
        bot.reply_to(message, 'oooops')
        welcome(message)


def confirmExchange(message, sumXML, numberOfCard, sumToGet, currency):
   #try:
        result = message.text
        if result == 'Подтверждаю обмен':
            #random_value = random.randint(1, 1000)
            user_name = message.from_user.username
            user_id = message.from_user.id #+ random_value
            bot.send_message(message.chat.id, "Ваша заявка принята!\nДля завершения вывода переведите точную сумму " + sumXML + " на кошелек:")
            bot.send_message(message.chat.id, numberOfPurse)
            bot.send_message(message.chat.id, "В поле memo укажите номер заявки!\n№Вашей заявки: "+ str(user_id) +"\nВаша заявка будет обработана в автоматическом режими в течении 20 минут.")
            sql = "REPLACE INTO users (name, user_id, sumXML, sumGet, numberOfCard, currency) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (user_name, str(user_id), sumXML, sumToGet, numberOfCard, currency)
            cursor.execute(sql, val)
            mydb.commit()
            welcome(message)
        if result == 'Назад':
            welcome(message)
   #except Exception as e:
        #bot.reply_to(message, 'oooops')
        #welcome(message)


def forRequest(message):
    index = 0
    cursor.execute("SELECT * FROM users WHERE user_id ='" + str(message.from_user.id) + "'")
    result = cursor.fetchall()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for x in result:
        print(x)
        index += 1
    if index > 0:
        item1 = types.KeyboardButton("Заявка: " + str(message.from_user.id))
        item2 = types.KeyboardButton("Назад")
        markup.add(item1, item2)
    else:
        item1 = types.KeyboardButton("Назад")
        markup.add(item1)
    bot.send_message(message.chat.id, "Выберите действие:".format(message.from_user, bot.get_me()), parse_mode = 'html', reply_markup = markup)
    bot.register_next_step_handler(message, statusRequest)


def statusRequest(message):
    #try:
        cursor.execute("SELECT * FROM users WHERE user_id ='"+str(message.from_user.id)+"'")
        myresult = cursor.fetchall()
        text = 'Заявка: ' + str(message.from_user.id)
        for x in myresult:
            print(x)
        print(message.text)
        if message.text == text:
            bot.send_message(message.chat.id, "Заявка: " + str(x[6])+"\nСтатус: Ожидание перевода на наш кошелек..."+"\nСумма обмена: " + str(x[2])+"\nСумма к получению: " + str(x[3]) + str(x[5])+"\nРеквизиты получателя: " + str(x[4]))
        if message.text == "Назад":
            welcome(message)
    #except Exception as e:
       # bot.reply_to(message, 'oooops')
        #welcome(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)
