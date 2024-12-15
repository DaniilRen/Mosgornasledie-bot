from dotenv import load_dotenv
from telebot import telebot
from telebot import types
import db
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)


def create_start_markup():
	markup = types.InlineKeyboardMarkup()
	for pr in db.get_all_projects():
		btn = types.InlineKeyboardButton(pr.name, callback_data=str(pr.id))
		markup.add(btn)
	return markup

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
	markup = create_start_markup()

	bot.send_message(message.chat.id, "Вас приветствует Департамент культурного наследия города Москвы! Здесь мы рассказываем о реализуемых нами проектах  в сфере сохранения и популяризации объектов культурного наследия, расположенных на территории города Москвы. Присоединяйтесь и узнаете много нового об истории и архитектуре столицы!", reply_markup=markup)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def send_message(message):
	bot.send_message(message.chat.id, "Я не знаю как ответить на такое сообщение 😅")


# Handle inline kb callback with project id, send msg with project details
@bot.callback_query_handler(func=lambda call: True)
def send_project_details(call):
	try:
		pr_id = call.data
		pr_data = db.get_project_by_id(pr_id)
		msg = f"*{pr_data.name}*\n"
		if pr_data.desc != "":
			msg += f"\n{pr_data.desc}\n"
		pr_links = db.get_project_links(pr_id)
		if len(pr_links) != 0:
			msg += "\n"
			for link in pr_links:
				msg += f"[{link.name}]({link.url})\n"
		with open(pr_data.photo, "rb") as photo:
			bot.send_photo(call.message.chat.id, photo)
		bot.send_message(call.message.chat.id, msg, parse_mode= 'Markdown')
	except Exception as e:
		print(repr(e))


bot.polling(none_stop=True, interval=0)