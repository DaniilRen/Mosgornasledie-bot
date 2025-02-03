import os

""" Подключение среды для VDS """
activate_this = '/home/Mosgornasledie-bot/.venv/bin/activate_this.py'
with open(activate_this) as f:
	exec(f.read(), {'__file__': activate_this})


from dotenv import load_dotenv
from telebot import telebot
from telebot import types
import db

""" 
Подключаемся к боту по токену,
токен берется из окружения
"""
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
print("< STARTING A BOT >")


""" Inline Клавитура со списком проектов"""
def create_start_markup():
	markup = types.InlineKeyboardMarkup()
	for pr in db.get_all_projects():
		btn = types.InlineKeyboardButton(pr.name, callback_data=str(pr.id))
		markup.add(btn)
	return markup


""" Приветственное сообщение """
@bot.message_handler(commands=['start'])
def send_welcome(message):
	markup = create_start_markup()
	bot.send_message(message.chat.id, "Вас приветствует Департамент культурного наследия города Москвы! Здесь мы рассказываем о реализуемых нами проектах  в сфере сохранения и популяризации объектов культурного наследия, расположенных на территории города Москвы. Присоединяйтесь и узнаете много нового об истории и архитектуре столицы!", reply_markup=markup)


""" Обработка иных текстовых сообещний """
@bot.message_handler(func=lambda message: True)
def send_message(message):
	bot.send_message(message.chat.id, "Я не знаю как ответить на такое сообщение 😅")


""" Callback для клавиатуры, отправка информации о проекте """
@bot.callback_query_handler(func=lambda call: True)
def send_project_details(call):
	try:
		pr_id = call.data
		pr_data = db.get_project_by_id(pr_id)
		""" ссылки и фотографии проекта """
		links = list(db.get_project_links(pr_id))
		photos = list(db.get_project_photos(pr_id))
		""" добавление заголовка и описания """
		msg = f"*{pr_data.name}*\n"
		if pr_data.desc != "":
			msg += f"\n{pr_data.desc}\n\n"

		""" обрабатываем варианты компановок фото """
		if len(photos) == 1:
			for link in links:
				if link.url[:5] != "https":
					msg += f"{link.name}: {link.url}\n"
				else:
					msg += f"[{link.name}]({link.url})\n"
			bot.send_message(call.message.chat.id, msg, parse_mode= 'Markdown')
			with open(photos[0].name, "rb") as photo:
				bot.send_photo(call.message.chat.id, photo, caption=photos[0].text, parse_mode= 'Markdown')

		else:
			bot.send_message(call.message.chat.id, msg, parse_mode= 'Markdown')
			link_idx = 0 # индекс прикрепляемой к фото ссылки
			for i in range(len(photos)):
				with open(photos[i].name, "rb") as photo:
					photo_msg = photos[i].text+"\n"
					if photos[i].position == 1:
						if links[link_idx].url[:5] != "https":
							photo_msg += f"{links[link_idx].name}: {links[link_idx].url}\n"
						else:
							photo_msg += f"[{links[link_idx].name}]({links[link_idx].url})\n"
					else:
						link_idx -= 1
					link_idx += 1
					bot.send_photo(call.message.chat.id, photo, caption=photo_msg, parse_mode= 'Markdown')

	except Exception as e:
		print(e)


bot.polling(none_stop=True, interval=0)