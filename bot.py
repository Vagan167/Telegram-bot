from telebot import *
import json
import sqlite3 as sq
import requests

bot = telebot.TeleBot('token')


open_weather_token = 'token'


#страрт
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/reg')
    markup.row(btn1)

    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}!Пропишите команду /reg чтобы зарегистрироваться', reply_markup=markup)

#регистрация пользователя
@bot.message_handler(commands=['reg'])
def reg(message: types.Message):
    con = sq.connect('user.db')
    cur = con.cursor()


    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        name TEXT,
        last_name TEXT
        )""")

    con.commit()
    people_id = message.chat.id
    cur.execute(f"SELECT id FROM users  WHERE id = {people_id}")
    data = cur.fetchone()

    if data is None:
        user_id = [message.chat.id,message.from_user.first_name, message.from_user.last_name]
        cur.execute("INSERT INTO users  VALUES (?,?,?);", user_id)
        con.commit()
        bot.register_next_step_handler(message, main)
        markup_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Привет')
        btn2 = types.KeyboardButton('Кто ты воин?')
        btn3 = types.KeyboardButton('Команды')
        btn4 = types.KeyboardButton('Узнать погоду')
        markup_two.row(btn1, btn2)
        markup_two.row(btn4, btn3)
        bot.send_message(message.chat.id, 'Вы зарегистрированы', reply_markup=markup_two)
    else:
        markup_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Привет')
        btn2 = types.KeyboardButton('Кто ты воин?')
        btn3 = types.KeyboardButton('Команды')
        btn4 = types.KeyboardButton('Узнать погоду')
        markup_two.row(btn1, btn2)
        markup_two.row(btn4, btn3)
        bot.send_message(message.chat.id, 'Такой пользователь существует', reply_markup=markup_two)


def city_wather(message: types.Message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        bot.send_message(message.chat.id, f'Сейчас погода: {temp}')
    else:
        bot.send_message(message.chat.id, 'Вы неправильно написали название города')

@bot.message_handler(commands=['admin'])
def admin_table(message: types.Message):
    con = sq.connect('admin.db')
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS admin (
    id INT,
    name TEXT,
    last_name TEXT
    )""")


    con = sq.connect('user.db')
    cur = con.cursor()

    people_id = message.chat.id
    cur.execute(f"SELECT id FROM users  WHERE id = {people_id}")
    data = cur.fetchone()
    if data is None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('/reg')
        markup.row(btn1)
        bot.send_message(message.chat.id, 'Вы не зарегистрированы.Чтобы зарегистрироваться напишите команду /reg',reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Введите общий пароль админов чтобы продолжить !\n Если вы уже зарегистрированы, то напишите что угодно чтобы продолжить!')
        bot.register_next_step_handler(message, admin)


def admin(message: types.Message):
    con = sq.connect('admin.db')
    cur = con.cursor()

    people_id = message.chat.id
    cur.execute(f"SELECT id FROM admin  WHERE id = {people_id}")
    data = cur.fetchone()

    if data is None:
        if message.text == '123':
            user_id = [message.chat.id, message.from_user.first_name, message.from_user.last_name]
            cur.execute("INSERT INTO admin VALUES (?,?,?);", user_id)


            markup_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Список всех пользователей')
            btn2 = types.KeyboardButton("Создатель бота")
            btn3 = types.KeyboardButton('Вернуться назад')
            markup_two.add(btn1, btn2)
            markup_two.add(btn3)

            bot.send_message(message.chat.id, 'Вы ввели правильный пароль!', reply_markup=markup_two)
            bot.register_next_step_handler(message, admin_panel)
            con.commit()
            if message.text == 'Вернуться назад':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton('/help')
                btn2 = types.KeyboardButton('/reg')
                btn3 = types.KeyboardButton('/remove')
                btn4 = types.KeyboardButton('/admin')
                back = types.KeyboardButton('Назад')
                markup.row(btn1, btn4, btn2)
                markup.row(btn3, back)
                bot.send_message(message.chat.id, 'Вернулись назад', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Неправильный пароль')
    else:
        markup_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Список всех пользователей')
        btn2 = types.KeyboardButton("Создатель бота")
        btn3 = types.KeyboardButton('Вернуться назад')
        markup_two.add(btn1, btn2)
        markup_two.add(btn3)

        bot.send_message(message.chat.id, 'Вы вошли!', reply_markup=markup_two)
        bot.register_next_step_handler(message, admin_panel)
        if message.text == 'Вернуться назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('/help')
            btn2 = types.KeyboardButton('/reg')
            btn3 = types.KeyboardButton('/remove')
            btn4 = types.KeyboardButton('/admin')
            back = types.KeyboardButton('Назад')
            markup.row(btn1, btn4, btn2)
            markup.row(btn3, back)
            bot.send_message(message.chat.id, 'Вернулись назад', reply_markup=markup)


def admin_panel(message: types.Message):
    con = sq.connect('admin.db')
    cur = con.cursor()

    if message.text == 'Создатель бота':
        cur.execute("SELECT id, name FROM admin WHERE id = 698255154 ")
        result = cur.fetchone()
        bot.send_message(message.chat.id, f'{result}')
        bot.register_next_step_handler(message, admin_panel)
    elif message.text == 'Вернуться назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('/help')
        btn2 = types.KeyboardButton('/reg')
        btn3 = types.KeyboardButton('/remove')
        btn4 = types.KeyboardButton('/admin')
        back = types.KeyboardButton('Назад')
        markup.row(btn1,btn4, btn2)
        markup.row(btn3, back)
        bot.send_message(message.chat.id, 'Основные команды', reply_markup=markup)
    elif message.text == 'Список всех пользователей':
        conn_two = sq.connect('user.db')
        cur_two = conn_two.cursor()

        cur_two.execute("SELECT * FROM users")
        for result_two in cur_two:
            bot.send_message(message.chat.id, f'{result_two}')
            conn_two.commit()
        bot.register_next_step_handler(message, admin_panel)
    else:
        bot.send_message(message.chat.id, 'Я вас не понял!')


#удаление пользователя
@bot.message_handler(commands=['remove'])
def delete(message: types.Message):
    con = sq.connect('user.db')
    cur = con.cursor()

    people_id = message.chat.id
    cur.execute(f"SELECT id FROM users  WHERE id = {people_id}")
    data = cur.fetchone()

    if data is None:
        bot.send_message(message.chat.id, 'Вы уже удалены')
    else:
        cur.execute(f"DELETE FROM users WHERE id = {people_id}")
        con.commit()
        bot.send_message(message.chat.id, 'Вы удалены')


#помощь
@bot.message_handler(commands=['help'])
def help(message: types.Message):
    bot.send_message(message.chat.id, 'Команды:\n/start\n/reg\n/remove')

#кнопки после регистрации
@bot.message_handler()
def main(message: types.Message):
    con = sq.connect('user.db')
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER,
            name TEXT,
            last_name TEXT
            )""")

    con.commit()
    people_id = message.chat.id
    cur.execute(f"SELECT id FROM users  WHERE id = {people_id}")
    data = cur.fetchone()
    if data is None:
        bot.send_message(message.chat.id,'Вы не зарегистрированы.Чтобы зарегистрироваться напишите команду /reg')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('/reg')
        markup.row(btn1)
    else:
        markup_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Привет')
        btn2 = types.KeyboardButton('Кто ты воин?')
        btn3 = types.KeyboardButton('Команды')
        btn4 = types.KeyboardButton('Узнать погоду')
        markup_two.row(btn1, btn2)
        markup_two.row(btn4,btn3)
        if message.text == 'Привет':
            bot.send_message(message.chat.id, 'Привет', reply_markup=markup_two)
        elif message.text == 'Кто ты воин?':
            bot.send_message(message.chat.id, 'МЫ АНТАНТА')
        elif message.text == 'Команды':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('/help')
            btn2 = types.KeyboardButton('/reg')
            btn3 = types.KeyboardButton('/remove')
            btn4 = types.KeyboardButton('/admin')
            back = types.KeyboardButton('Назад')
            markup.row(btn1,btn4,btn2)
            markup.row(btn3,back)
            bot.send_message(message.chat.id, 'Основные команды', reply_markup=markup)
        elif message.text == 'Назад':
            markup_two = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Привет')
            btn2 = types.KeyboardButton('Кто ты воин?')
            btn3 = types.KeyboardButton('Команды')
            btn4 = types.KeyboardButton('Узнать погоду')
            markup_two.row(btn1, btn2)
            markup_two.row(btn4, btn3)
            bot.send_message(message.chat.id, 'Меню', reply_markup=markup_two)
        elif message.text == 'Узнать погоду':
            msg = bot.send_message(message.chat.id, 'Напишите название города.')
            bot.register_next_step_handler(message, city_wather)
        else:
            bot.send_message(message.chat.id, 'Я вас не понял')


bot.polling(none_stop=True)