import telebot
from telebot import types
from datetime import date

from CON_BD import give_groups, join_to_group, give_week, give_day, give_faculties, delete
from parse_file import refresh

bot = telebot.TeleBot('5011301483:AAECz1AsPnB7aePB8ICPMct0q3AQ-VhmItI')

main_Markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

week_button = types.KeyboardButton(text="Расписание на неделю")
today_button = types.KeyboardButton(text="Расписание на сегодня")
tomorrow_button = types.KeyboardButton(text="Расписание на завтра")

main_Markup.row(week_button, today_button, tomorrow_button)


@bot.message_handler(commands=["refresh"])
def refresh(message):
    if message.chat.id == 394796650:
        refresh()\


@bot.message_handler(commands=["imposter"])
def imposter(message):
    if message.chat.id == 763283309:
        delete()


@bot.message_handler(commands=["start"])
def start(message):
    choice_markup = types.InlineKeyboardMarkup()
    groups_button = types.InlineKeyboardButton(text="Выбрать группу кнопками", callback_data="choice_with_buttons")
    choice_markup.add(groups_button)
    bot.send_message(message.chat.id, f'Здравствуйте, <b>{message.from_user.first_name}</b>!'
                                      f'\nВ какой группе Вы учитесь?', parse_mode="html")
    bot.send_message(message.chat.id, f'Вы можете отправить номер ссообщением '
                                      f'\n(<i>Пример</i>: ПМ-Б18-2-3) или выбрать кнопками',
                     parse_mode="html", reply_markup=choice_markup)


@bot.message_handler(commands=["id"])
def id(message):
    bot.send_message(chat_id="763283309", text=message.chat.id)


@bot.message_handler()
def main_handler(message):
    if message.text == "Расписание на неделю":
        for elem in give_week(message.chat.id):
            bot.send_message(chat_id=message.chat.id, text=elem, parse_mode="html")

    elif message.text == "Расписание на сегодня":
        current_date = date.today()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        dayNumber = current_date.weekday()
        if days[dayNumber] == "sunday":
            bot.send_message(message.chat.id,
                             text="🎉Сегодня воскресенье. Отдыхаем!🎉",
                             parse_mode="html")
        else:
            bot.send_message(message.chat.id,
                             text="Расписание на сегодня\n" + give_day(message.chat.id, days[dayNumber]),
                             parse_mode="html")

    elif message.text == "Расписание на завтра":
        current_date = date.today()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        dayNumber = current_date.weekday()
        if days[dayNumber + 1] == "sunday":
            bot.send_message(message.chat.id,
                             text="Завтра воскресенье. Отдыхаем!",
                             parse_mode="html")
        else:
            bot.send_message(message.chat.id, text="Расписание на завтра\n" + give_day(message.chat.id,
                                                                                       days[dayNumber + 1]),
                             parse_mode="html")
    else:
        in_group = False
        group = None
        faculty = None
        for elem in give_faculties():
            groups = give_groups(elem)
            for el in groups:
                if el.lower() == message.text.lower().strip():
                    group = el
                    in_group = True
                    faculty = elem
        if in_group:
            bot.send_message(message.chat.id, text=join_to_group(message.chat.id, group, faculty), parse_mode="html",
                             reply_markup=main_Markup)
        else:
            bot.send_message(message.chat.id, text="Я не знаю такой группы")


@bot.callback_query_handler(func=lambda call: True)
def inline(call):
    global main_Markup
    if call.data == "choice_with_buttons":
        faculties_markup = types.InlineKeyboardMarkup()
        faculties = []
        for elem in give_faculties():
            faculties.append(types.InlineKeyboardButton(text=elem, callback_data="group" + elem))
        faculties_markup.add(*faculties)

        bot.edit_message_text(chat_id=call.message.chat.id, text="На каком факультете Вы учитесь?",
                              message_id=call.message.id, parse_mode="html", reply_markup=faculties_markup)
    elif call.data[:5] == "group":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=f"Вы выбрали факультет: <b><u>{call.data[5:]}</u></b>", parse_mode="html")

        groups_markup = types.InlineKeyboardMarkup()
        sp = []
        for elem in give_groups(call.data[5:]):
            sp.append(types.InlineKeyboardButton(text=elem, callback_data="join" + call.data[5:] + " | " + elem))
        groups_markup.add(*sp)
        bot.send_message(chat_id=call.message.chat.id, text="В какой группе Вы учитесь?",
                         reply_markup=groups_markup)
    elif call.data[:4] == "join":
        group = call.data[4:].split(" | ")[1]
        faculty = call.data[4:].split(" | ")[0]

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=join_to_group(call.message.chat.id, group, faculty), parse_mode="html")
        bot.send_message(call.message.chat.id, text="Какое расписание Вы хотите узнать?", parse_mode="html",
                         reply_markup=main_Markup)

    bot.answer_callback_query(callback_query_id=call.id)


bot.polling(none_stop=True)
