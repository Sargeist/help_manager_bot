import telebot
from telebot import types


bot = telebot.TeleBot('7116325866:AAH6j_O9of-j2bF4-sxKwBwjpTmJfslxMhU')


admin_chat_id = '825590210'


questions_file = 'help_bot/user_questions.txt'
city_info_file = 'help_bot/city_info.txt'
# Хранилище для временного хранения вопросов
user_questions = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Продолжить")
    markup.add(item)
    bot.send_message(message.chat.id, "Добро пожаловать! Выбере то, чем мы бы могли вам помочь.", reply_markup=markup)




@bot.message_handler(func=lambda message: message.text == "Продолжить" or message.text == "Вернуться в начало")
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Связаться с Менеджером")
    item2 = types.KeyboardButton("Информация о городе")
    markup.add(item, item2)
    bot.send_message(message.chat.id, "Выберите то, чем мы бы могли вам помочь.", reply_markup=markup)
#######

#Обратная свзяь

#######
@bot.message_handler(func=lambda message: message.text == "Связаться с Менеджером")
def ask_question(message):
    msg = bot.send_message(message.chat.id, "Пожалуйста, напишите ваш вопрос.")
    bot.register_next_step_handler(msg, save_question)

def save_question(message):
    user_id = message.from_user.id
    user_question = message.text
    
    # Сохранение вопроса в словаре
    user_questions[user_id] = user_question
    
    # Запись вопроса пользователя в текстовый файл
    with open(questions_file, 'a', encoding='utf-8') as file:
        file.write(f"{user_id}: {user_question}\n")
    
    # Отправка вопроса администраторам с кнопкой "Дать ответ"
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Дать ответ", callback_data=f"answer_{user_id}")
    markup.add(button)
    bot.send_message(admin_chat_id, f"Вопрос от пользователя {user_id}: {user_question}", reply_markup=markup)

    bot.send_message(message.chat.id, "Ваш вопрос отправлен менеджеру, ожидайте.")

# Обработчик для кнопки "Дать ответ"
@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def handle_answer_button(call):
    user_id = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, "Пожалуйста, напишите ваш ответ.")
    bot.register_next_step_handler(msg, send_answer, user_id)

def send_answer(message, user_id):
    admin_response = message.text
    user_id = int(user_id)
    
    # Проверка наличия ID пользователя в словаре
    if user_id in user_questions:
        # Отправка ответа пользователю
        bot.send_message(user_id, f"Ответ от техподдержки: {admin_response}")

        # Удаление вопроса и ID пользователя из текстового файла
        remove_question_from_file(user_id)
        
        bot.send_message(admin_chat_id, "Ответ отправлен пользователю.")
    else:
        bot.send_message(admin_chat_id, "Не удалось найти пользователя для ответа.")

def remove_question_from_file(user_id):
    lines = []
    
    # Чтение всех строк из файла
    with open(questions_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Перезапись файла только с теми строками, которые не содержат удаляемый user_id
    with open(questions_file, 'w', encoding='utf-8') as file:
        for line in lines:
            if not line.startswith(f"{user_id}:"):
                file.write(line)



#############

#City info

#############


def get_city_info(city_name):
    with open(city_info_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        city_info = ""
        is_city_found = False
        
        for line in lines:
            if line.strip() == "":
                continue
            
            if line.strip().lower() == city_name.lower():
                is_city_found = True
                continue
            
            if is_city_found:
                if not line.strip().isalpha():
                    city_info += line.strip() + "\n"
                else:
                    break
        
        if city_info:
            return city_info.strip()
        else:
            return "Информация о данном городе не найдена."

@bot.message_handler(func=lambda message: message.text == "Информация о городе" or message.text == "Вернуться назад")
def send_city_selection_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Кошице")
    item2 = types.KeyboardButton("Братислава")
    item3 = types.KeyboardButton("Прешов")
    item4 = types.KeyboardButton("Нитра")
    markup.add(item, item2, item3, item4)
    bot.send_message(message.chat.id, "Пожалуйста, выберите название нужного города.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Кошице", "Братислава", "Прешов", "Нитра"])
def send_city_info(message):
    city_name = message.text
    city_info = get_city_info(city_name)
    bot.send_message(message.chat.id, city_info)
    
    # Отправляем сообщение о возможности выбора другого города с помощью InlineKeyboardMarkup
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("Вернуться в начало", callback_data="main_menu"))

    bot.send_message(message.chat.id, "Также, вы можете выбрать информацию о другом городе, либо вернуться в начало.", reply_markup=inline_markup)

# Обработчик для Inline кнопки "Вернуться в начало"
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def return_to_main_menu(call):
    main_menu(call.message)



bot.polling(non_stop= True, interval=0)