import telebot
import requests
from bs4 import BeautifulSoup
import random

# Ваш api бота
TOKEN = '3543:jdkgdl'

bot = telebot.TeleBot(TOKEN)

news_cache = []


def parse_news():
    url = 'https://ria.ru/location_rossiyskaya-federatsiya/'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_elements = soup.find_all('a', class_='list-item__title color-font-hover-only')

        headlines = [element.text for element in news_elements]

        return random.sample(headlines, 10)
    else:
        return None


def parse_sport_express_news():
    url = 'https://www.sport-express.ru/'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_elements = soup.find_all('h2', class_='se-material__title')

        headlines = [element.text.strip() for element in news_elements]

        return random.sample(headlines, 5)
    else:
        return None


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Я бот, который будет отправлять тебе 10 случайных актуальных новостей каждые 24 часа.")
    send_news(chat_id)


def send_news(chat_id):
    global news_cache
    if not news_cache:
        ria_news = parse_news()
        sport_express_news = parse_sport_express_news()

        if ria_news:
            news_cache.extend(ria_news)
        if sport_express_news:
            news_cache.extend(sport_express_news)

    if news_cache:
        ria_slice = news_cache[:10]
        ria_text = "\n\n".join([f"{i}. {headline}" for i, headline in enumerate(ria_slice, start=1)])
        bot.send_message(chat_id, f"Новости с RIA Novosti:\n\n{ria_text}")
        news_cache = news_cache[10:]

        sport_express_slice = news_cache[:5]
        sport_express_text = "\n\n".join([f"{i}. {headline}" for i, headline in enumerate(sport_express_slice, start=1)])
        markup = telebot.types.InlineKeyboardMarkup()
        more_news_button = telebot.types.InlineKeyboardButton("Ещё новости!", callback_data="more_news")
        markup.add(more_news_button)
        bot.send_message(chat_id, f"Новости с sport-express.ru:\n\n{sport_express_text}", reply_markup=markup)
        news_cache = news_cache[5:]

    else:
        bot.send_message(chat_id, "Не удалось получить новости с сайта.")


@bot.callback_query_handler(func=lambda call: call.data == "more_news")
def more_news_callback(call):
    chat_id = call.message.chat.id
    send_news(chat_id)


bot.polling()
