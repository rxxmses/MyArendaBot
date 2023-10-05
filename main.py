import telebot
import re
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import time
import sqlite3

bot = telebot.TeleBot("123:AbC")

def check_ad(json_file, chat_id):
    current_datetime = datetime.now()
    current_datetime = current_datetime.replace(microsecond=0)
    two_weeks_ago = current_datetime - timedelta(days=14)
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    table_name = f"id_{chat_id}"

    for data in json_file["data"]:
        time.sleep(3)
        json_date = data["last_refresh_time"]
        json_date = datetime.fromisoformat(str(json_date[:16]))

        if json_date >= two_weeks_ago and json_date <= current_datetime:
            cursor.execute(f"SELECT * FROM {table_name} WHERE ads_id = ?", (data["id"],))
            existing_row = cursor.fetchone()

            if not existing_row:
                bot.send_message(chat_id, data["url"])
                cursor.execute(f"INSERT INTO {table_name} (ads_id) VALUES (?)", (data["id"],))
                conn.commit()

    conn.close()

def start_parser(min_price, max_price, district, message):
    district_list = {
        "Голосеевский": 1,
        "Дарницкий": 3,
        "Деснянский": 5,
        "Днепровский": 7,
        "Оболонский": 9,
        "Печерский": 11,
        "Подольский": 13,
        "Святошинский": 15,
        "Соломянский": 17,
        "Шевченковский": 19
    }
    data = {}
    offset = 0
    chat_id = message.chat.id
    while True:
        url = "https://www.olx.ua/api/v1/offers/?offset=" + str(offset) + "&limit=40&category_id=1760&region_id=25&district_id=" + str(district_list[district]) + "&city_id=268&owner_type=private&currency=UAH&sort_by=created_at%3Adesc&filter_float_price%3Afrom=" + min_price + "&filter_float_price%3Ato=" + max_price + "&filter_refiners=spell_checker&sl=1890e3f6ce2x8bf6191"
        headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        print(url)
        response = requests.get(url, headers=headers)
        data.update(response.json())

        if len(data["data"]) != 0:
            check_ad(data, chat_id)
            offset += 40
            time.sleep(5)
        else:
            offset = 0
            bot.send_message(chat_id, "Новых обьявлений нет")
            time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_message(message.chat.id, "Данный бот отображает все объявления о сдаче квартир в аренду в г. Киев. \nДля начала работы нужно выбрать название района, ввести минимальную и максимальную стоимость аренды. \nБот отобразит все доступные объявления за 14 дней, а также будет проверять новые объявления каждые 15 минут.", reply_markup=get_inline_keyboard())

        table_name = f"id_{message.chat.id}"
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()

        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}
                                  (ads_id)
                               """)
        conn.close()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
def get_inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("Голосеевский", callback_data='Голосеевский'),
        telebot.types.InlineKeyboardButton("Дарницкий", callback_data='Дарницкий')
    )
    keyboard.add(
       telebot.types.InlineKeyboardButton("Деснянский", callback_data='Деснянский'),
       telebot.types.InlineKeyboardButton("Днепровский", callback_data='Днепровский')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("Оболонский", callback_data='Оболонский'),
        telebot.types.InlineKeyboardButton("Печерский", callback_data='Печерский')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("Подольский", callback_data='Подольский'),
        telebot.types.InlineKeyboardButton("Святошинский", callback_data='Святошинский')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("Соломянский", callback_data='Соломянский'),
        telebot.types.InlineKeyboardButton("Шевченковский", callback_data='Шевченковский')
    )
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        district = str(call.data)

        if call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             f"Вы выбрали район: {call.data}. Теперь введите минимальную и максимальную сумму через тире, например 10000-20000")

        @bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            try:
                min_price = re.findall(r'(\d*)-\d*', message.text)
                min_price = str(min_price[0])
                max_price = re.findall(r'\d*-(\d*)', message.text)
                max_price = str(max_price[0])
                if message.text:
                    if int(min_price) < int(max_price):
                        bot.send_message(message.from_user.id, f"Вы выбрали цену от {min_price} грн до {max_price} грн")
                        start_parser(min_price, max_price, district, message)
                    else:
                        bot.send_message(message.from_user.id, f"Введите корректную цену")
            except:
                bot.send_message(message.from_user.id, f"Введите корректную цену")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

try:
    bot.polling(none_stop=True, interval=0)

except Exception as e:
    print(f"Произошла ошибка при запуске бота: {str(e)}")
