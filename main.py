import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import os
import time

TOKEN = os.getenv("TOKEN")  # Получаем токен из переменной окружения
bot = telebot.TeleBot(TOKEN)

# Хранилище данных пользователей
user_records = {}  # Хранит записи пользователей
user_last_message = {}  # Хранит ID последнего сообщения бота
user_last_voice = {}  # Хранит ID последних голосовых сообщений
user_current_task = {}  # Хранит текущее задание пользователя
user_waiting_for_action = {}  # Флаг, указывающий, ожидает ли бот выбора действия

# Главное меню с кнопкой "Начать"
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Начать"))

SAVE_PATH = "/Users/elizavetapuzyreva/Desktop/bot/voice_records"

# Меню действий с записью
action_menu = InlineKeyboardMarkup()
action_menu.add(InlineKeyboardButton("🔄 Перезаписать", callback_data="re_record"))
action_menu.add(InlineKeyboardButton("➡️ Перейти к следующему заданию", callback_data="next_task"))
action_menu.add(InlineKeyboardButton("📤 Отправить всё и закончить", callback_data="send"))
action_menu.add(InlineKeyboardButton("🔄 Сброс", callback_data="reset"))  # Новая кнопка "Сброс"

import random


# Функция для загрузки предложений из файла task.txt
def load_sentences_from_file(filename="task.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            sentences = file.readlines()
        return [s.strip() for s in sentences if s.strip()]
    except FileNotFoundError:
        return ["Ошибка: файл task.txt не найден."]


# Основная функция для выбора задания
def get_text_for_user(task_number):
    if task_number == 1:
        sentences = [
            "1) На кухне холодильник.\n",
            "2) Кате купили хомяка.\n",
            "3) Машинист сошёл с подножки.\n",
            "4) Яша ел сладкие яблоки.\n",
            "5) Ёжик у ёлки наколол гриб на иголки.\n",
            "6) Дети слепили снеговика.\n",
            "7) Повар печёт блины на сковороде.\n",
            "8) В аквариуме плавают золотые рыбки.\n",
            "9) Волосы подстригают в парикмахерской.\n",
            "10) Милиционер ездит на мотоцикле.\n"
        ]
        #return "Повторите 5 предложений на выбор. Выполните задание одной записью:\n\n" + "\n".join(sentences)
        return "Повторите 5 предложений на выбор. Выполните задание одной записью:\n\n" + "\n".join(sentences)


    elif task_number == 2:
        words = [
            "Часы", "Собака", "Мяч", "Утюг", "Санки", "Книга", "Чайник", "Арбуз", "Самолёт", "Конфета",
            "Цыплёнок", "Картошка", "Стол", "Платье", "Телевизор\n\n"
            "или\n\n"
            "Лыжи", "Кубики", "Ёж", "Петух", "Юбка", "Груша", "Портфель", "Львёнок", "Молоток", "Тарелка",
            "Карандаш", "Скамейка", "Волк", "Клюшка", "Сковорода\n"
        ]
        return "Перечислите набор слов  на выбор:\n\n" + ", ".join(words)


    elif task_number == 3:

        sentences = load_sentences_from_file()
        if sentences:
            selected_sentence = random.choice(sentences)
            selected_sentence = " ".join(selected_sentence.split(" ")[1:])
            return f"Прочитайте вслух предложенный отрывок текста:\n\n{selected_sentence}"


    elif task_number == 4:
        questions = [
            "Где вам нравится проводить время?",
            "Какая сейчас погода за окном?",
            "Как вы думаете, почему важно сохранять природу?",
            "Любите ли вы животных и почему?"
        ]
        return "Ответьте на один вопрос на выбор. Старайтесь сделать это подробно:\n\n" + "\n".join(questions)


    elif task_number == 5:
        return "Опишите картину, которую видите. Можете сосредоточиться как на деталях, так и на картине в целом."

    elif task_number == 6:
        actions = [
            "Как приготовить чай",
            "Как добраться до ближайшей станции метро",
            "Как почистить зубы",
            "Как приготовить бутерброд"
        ]
        return "Опишите, как выполнить одно из следующих действий по шагам:\n\n" + "\n".join(actions)

    return "Задание завершено!"

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    text = (
        "Привет! 👋\n\n"
        "Мы разрабатываем технологию, которая поможет людям с нарушениями речи."
        " Для этого нам нужны голосовые записи, чтобы обучать системы "
        "распознавания речи и голосовых помощников.\n\n"
        "Как участвовать? Вы будете получать текстовые задания (всего их 6), которые нужно записать голосом. "
        "После записи файл можно перезаписать, отправить или перейти к следующему заданию.\n"
        "Спасибо за ваш вклад! 😊️\n\n"
        "ℹ️ Для получения дополнительной информации используйте команду /info\n"
        "🔄 Чтобы сбросить прогресс начать заново отправьте команду /reset\n"
        "❓ Если у вас возникли вопросы о том, как записать голосовое сообщение, используйте команду /help"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu)
    """Обработчик команды /start с анкетированием"""
    user_id = message.chat.id

    # Добавляем кнопки "Да" и "Нет"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))

    bot.send_message(user_id, "Хотите заполнить анкету перед началом? Она необязательная, но Вы очень поможете исследованию ❤️" + "\nОтветьте Да или Нет", reply_markup=markup)
    bot.register_next_step_handler(message, process_survey_choice)

def process_survey_choice(message):
    user_id = message.chat.id
    text = message.text.lower()

    if text == "/info":
        txt1 = (
            "Мы Lab260 - лаборатория искусственного интеллекта, разрабатывающая технологии машинного обучения.\n\n"
            "Сейчас мы работаем над проектом, который поможет людям с нарушениями речи. "
            "Чтобы создать полезные голосовые помощники и системы распознавания, нам нужен разнообразный датасет записей.\n\n"
            "Каждый голос уникален, и ваша помощь позволит нам адаптировать технологии под любые особенности речи.\n\n"
            "Мы гарантируем конфиденциальность — все записи используются только в исследовательских целях.\n\n"
            "По вопросам: plisssa2002@yandex.ru\n\n"
            "Давайте вместе сделаем технологии доступными для всех! 🚀\n\n"
            "С уважением,\n"
            "Команда Lab260 ❤️"
        )
        bot.send_message(user_id, txt1)
        bot.register_next_step_handler(message, process_survey_choice)  # Ждем следующий ответ
        return

    if text == "/help":
        txt2 = (
            "Чтобы записать голосовое сообщение в Telegram:\n"
            "1️⃣ Нажмите и удерживайте кнопку микрофона возле строки ввода (справа снизу).\n"
            "2️⃣ Произнесите текст, затем отпустите кнопку, чтобы отправить запись.\n"
            "3️⃣ Если запись успешно отправилась, то вы увидите ее в чате с ботом.\n\n"
            "Если возникли проблемы, проверьте настройки микрофона или напишите нам..️"
        )

        bot.send_message(user_id, txt2)
        bot.register_next_step_handler(message, process_survey_choice)  # Ждем следующий ответ
        return

    if text == "да" or text == "Да":
        bot.send_message(user_id, "Какой у вас возраст?", reply_markup=ReplyKeyboardRemove())  # Убираем кнопки
        bot.register_next_step_handler(message, process_age)
    if text == "нет" or text == "Нет":
        bot.send_message(user_id, "Хорошо, переходим к заданиям!", reply_markup=ReplyKeyboardRemove())  # Убираем кнопки
        start_recording(message)
    else:
        print("Выберете Да или Нет.")



user_survey = {}  # Словарь для хранения анкетных данных

@bot.message_handler(commands=['help'])
async def send_help(message):
    help_text = (
        "Чтобы записать голосовое сообщение в Telegram:\n"
        "1️⃣ Нажмите и удерживайте кнопку микрофона возле строки ввода (справа снизу).\n"
        "2️⃣ Произнесите текст, затем отпустите кнопку, чтобы отправить запись.\n"
        "3️⃣ Если запись успешно отправилась, то вы увидите ее в чате с ботом.\n\n"
        "Если возникли проблемы, проверьте настройки микрофона или напишите нам..️"
    )
    await message.answer(help_text)

@bot.message_handler(commands=['пропустить'])
def skip_question(message):
    user_id = message.chat.id

    if user_id in user_survey:
        if "Возраст" not in user_survey[user_id]:
            user_survey[user_id]["Возраст"] = "-"
            bot.send_message(user_id, "Какой у вас пол? (М/Ж)",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/пропустить")))
            bot.register_next_step_handler(message, process_gender)
            return

        if "Пол" not in user_survey[user_id]:
            user_survey[user_id]["Пол"] = "-"
            bot.send_message(user_id, "Какой у вас родной язык?",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/пропустить")))
            bot.register_next_step_handler(message, process_language)
            return

        if "Родной язык" not in user_survey[user_id]:
            user_survey[user_id]["Родной язык"] = "-"
            bot.send_message(user_id, "Есть ли у вас нарушения речи? (например: дислалия, заикание, афазия, дизартрия и т. д.)",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/пропустить")))
            bot.register_next_step_handler(message, process_speech_disorder)
            return

        if "Тип нарушения" not in user_survey[user_id]:
            user_survey[user_id]["Тип нарушения"] = "-"
            bot.send_message(user_id, "Какова причина нарушения? (врождённое, приобретённое, травма, заболевание и т. д.)",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/пропустить")))
            bot.register_next_step_handler(message, process_cause)
            return

        if "Причина нарушения" not in user_survey[user_id]:
            user_survey[user_id]["Причина нарушения"] = "-"
            bot.send_message(user_id, "Проходите ли лечение? (логопед, невролог и т. д.)",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/пропустить")))
            bot.register_next_step_handler(message, process_treatment)
            return

        if "Проходит ли лечение" not in user_survey[user_id]:
            user_survey[user_id]["Проходит ли лечение"] = "-"
            filename = save_survey_to_file(user_id)
            bot.send_message(user_id, "Спасибо! Теперь можете приступить к заданиям.",
                             reply_markup=ReplyKeyboardRemove())
            start_recording(message)
            return


def process_age(message):
    user_id = message.chat.id
    user_survey[user_id] = {"Возраст": message.text}

    # Создаем клавиатуру с кнопкой "Пропустить"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/пропустить"))

    bot.send_message(user_id, "Какой у вас пол? (М/Ж)", reply_markup=markup)
    bot.register_next_step_handler(message, process_gender)

def process_gender(message):
    user_id = message.chat.id
    user_survey[user_id]["Пол"] = message.text
    # Создаем клавиатуру с кнопкой "Пропустить"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/пропустить"))


    bot.send_message(user_id, "Какой у вас родной язык?", reply_markup=markup)
    bot.register_next_step_handler(message, process_language)


def process_language(message):
    user_id = message.chat.id
    user_survey[user_id]["Родной язык"] = message.text
    # Создаем клавиатуру с кнопкой "Пропустить"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/пропустить"))

    bot.send_message(user_id, "Есть ли у вас нарушения речи? (например: дислалия, заикание, афазия, дизартрия и т. д.)", reply_markup=markup)
    bot.register_next_step_handler(message, process_speech_disorder)


def process_speech_disorder(message):
    user_id = message.chat.id
    user_survey[user_id]["Тип нарушения"] = message.text
    # Создаем клавиатуру с кнопкой "Пропустить"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/пропустить"))

    bot.send_message(user_id, "Какова причина нарушения? (врождённое, приобретённое, травма, заболевание и т. д.)", reply_markup=markup)
    bot.register_next_step_handler(message, process_cause)


def process_cause(message):
    user_id = message.chat.id
    user_survey[user_id]["Причина нарушения"] = message.text
    # Создаем клавиатуру с кнопкой "Пропустить"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/пропустить"))

    bot.send_message(user_id, "Проходите ли лечение? (логопед, невролог и т. д.)", reply_markup=markup)
    bot.register_next_step_handler(message, process_treatment)

def process_treatment(message):
    user_id = message.chat.id
    user_survey[user_id]["Проходит ли лечение"] = message.text

    # Формируем текст анкеты
    survey_text = f"📝 Новая анкета {user_id}\n\n"
    for key, value in user_survey[user_id].items():
        survey_text += f"{key}: {value}\n"

    # ID Telegram-канала (замени на свой)
    CHANNEL_ID = "@bot_260"

    # Отправляем анкету в канал
    bot.send_message(CHANNEL_ID, survey_text)

    bot.send_message(user_id, "Спасибо! Теперь можете приступить к заданиям.", reply_markup=ReplyKeyboardRemove())
    start_recording(message)



def save_survey_to_file(user_id):
    directory = "/Users/elizavetapuzyreva/Desktop/bot/voice_form"
    if not os.path.exists(directory):
        os.makedirs(directory)  # Создаём папку, если её нет

    filename = os.path.join(directory, f"{user_id}_survey.txt")
    version = 1
    while os.path.exists(filename):
        version += 1
        filename = os.path.join(directory, f"{user_id}_survey_v{version}.txt")

    with open(filename, "w", encoding="utf-8") as file:
        for key, value in user_survey[user_id].items():
            file.write(f"{key}: {value}\n")

    return filename  # Возвращаем путь к файлу

@bot.message_handler(commands=['info'])
def info(message):
    """Обработчик команды /info"""
    text = (
        "Мы Lab260 - лаборатория искусственного интеллекта, разрабатывающая технологии машинного обучения.\n\n"
        "Сейчас мы работаем над проектом, который поможет людям с нарушениями речи. "
        "Чтобы создать полезные голосовые помощники и системы распознавания, нам нужен разнообразный датасет записей.\n\n"
        "Каждый голос уникален, и ваша помощь позволит нам адаптировать технологии под любые особенности речи.\n\n"
        "Мы гарантируем конфиденциальность — все записи используются только в исследовательских целях.\n\n"
        "По вопросам: plisssa2002@yandex.ru\n\n"
        "Давайте вместе сделаем технологии доступными для всех! 🚀\n\n"
        "С уважением,\n"
        "Команда Lab260 ❤️"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['reset'])
def reset_command(message):
    """Обработчик команды /reset"""
    user_id = message.chat.id

    # Очищаем все данные пользователя
    if user_id in user_records:
        user_records[user_id] = []
    if user_id in user_last_voice:
        user_last_voice[user_id] = []
    if user_id in user_current_task:
        user_current_task[user_id] = 1
    if user_id in user_waiting_for_action:
        user_waiting_for_action[user_id] = False

    # Возвращаем пользователя к началу
    bot.send_message(user_id, "🔄 Состояние сброшено. Нажмите 'Начать', чтобы начать заново.", reply_markup=main_menu)

@bot.message_handler(func=lambda message: message.text == "Начать")
def start_recording(message):
    """Начинает процесс записи"""
    user_id = message.chat.id
    user_current_task[user_id] = 1  # Начинаем с первого задания
    user_waiting_for_action[user_id] = False  # Сбрасываем флаг ожидания действия

    # Очищаем предыдущие записи
    if user_id in user_records:
        user_records[user_id] = []
    if user_id in user_last_voice:
        user_last_voice[user_id] = []

    # Отправляем первое задание
    send_task(user_id)


def send_task(user_id):
    """Отправляет задание пользователю"""
    task_number = user_current_task[user_id]

    if task_number == 5:
        image_path, image_name = get_random_image()

        if image_path:
            with open(image_path, "rb") as image_file:
                bot.send_photo(user_id, image_file,
                               caption=f"Опишите картину, которую видите. Можете сосредоточиться как на деталях, так и на картине в целом.\n\nПодсказки для описания:\nЧто изображено на переднем плане, а что на заднем?\nКакие объекты или персонажи привлекают внимание в первую очередь?\nКакой может быть предыстория этой сцены?\nКакое настроение создаёт картина?\n\nНазвание: {image_name}")
        else:
            bot.send_message(user_id, "⚠️ В папке Image нет изображений.")
        return

    text_for_recording = get_text_for_user(task_number)

    if text_for_recording == "Задание завершено!":
        bot.send_message(user_id, "✅ Все задания выполнены! Нажмите 'Начать', чтобы пройти заново.",
                         reply_markup=main_menu)
        return

    msg = bot.send_message(
        user_id,
        f"Выполните задание {task_number}. \n\n{text_for_recording}\n\n📢 Запишите голосовое сообщение и отправьте его сюда.",
        reply_markup=ReplyKeyboardRemove()
    )
    user_last_message[user_id] = msg.message_id


@bot.message_handler(content_types=['voice'])
def save_voice(message):
    """Сохраняет голосовое сообщение и предлагает выбрать действие"""
    user_id = message.chat.id
    CHANNEL_ID = "@bot_260"  # Укажите ваш Telegram-канал

    # Проверяем, выбрал ли пользователь задание
    if user_id not in user_current_task:
        bot.send_message(user_id, "⚠️ Сначала нажмите 'Начать', чтобы получить текст для записи!")
        return

    # Если бот ожидает выбора действия — сбрасываем флаг
    if user_waiting_for_action.get(user_id, False):
        user_waiting_for_action[user_id] = False  # Сброс флага ожидания

    # Сохраняем голосовое сообщение
    file_id = message.voice.file_id
    user_records.setdefault(user_id, []).append(file_id)

    # Уведомляем пользователя
    bot.send_message(user_id, "✅ Запись сохранена!")

    # Проверяем, выполнены ли все задания
    if user_current_task[user_id] >= 6:
        bot.send_message(user_id, "Вы выполнили все задания! "
                                  "Не забудьте нажать кнопку '📤 Отправить всё и закончить'.")

    # Предлагаем действия
    task_number = user_current_task[user_id]
    menu = get_action_menu(task_number)
    msg = bot.send_message(user_id, "Выберите действие:", reply_markup=menu)
    user_last_message[user_id] = msg.message_id

    # Устанавливаем флаг ожидания действия
    user_waiting_for_action[user_id] = True


@bot.callback_query_handler(func=lambda call: call.data == "next_task")
def next_task(call):
    """Отправляет все голосовые сообщения в канал перед следующим заданием"""
    user_id = call.message.chat.id
    chat_id = "@bot_260"

    # Если у пользователя есть сохранённые аудио — отправляем
    if user_id in user_records and user_records[user_id]:
        bot.send_message(user_id, "📤 Подождите ...")

        for file_id in user_records[user_id]:
            bot.send_voice(chat_id, file_id, caption=f"🆔 Пользователь: {user_id}")

        # Очищаем список записей после отправки
        user_records[user_id] = []

    # Удаляем предыдущее меню
    try:
        bot.delete_message(user_id, call.message.message_id)
    except Exception:
        pass

    # Переходим к следующему заданию
    user_current_task[user_id] += 1
    send_task(user_id)


@bot.callback_query_handler(func=lambda call: call.data == "re_record")
def re_record(call):
    """Перезапись текущего задания"""
    user_id = call.message.chat.id

    # Удаляем последнюю запись
    if user_id in user_records and user_records[user_id]:
        user_records[user_id].pop()

    # Удаляем последнее голосовое сообщение
    if user_id in user_last_voice and user_last_voice[user_id]:
        last_voice_id = user_last_voice[user_id].pop()
        try:
            bot.delete_message(user_id, last_voice_id)
        except Exception:
            pass

    # Удаляем предыдущее меню
    try:
        bot.delete_message(user_id, call.message.message_id)
    except Exception:
        pass

    # Повторно отправляем текущее задание
    user_waiting_for_action[user_id] = False
    send_task(user_id)

@bot.callback_query_handler(func=lambda call: call.data == "send")
def send_recording(call):
    """Отправка всех записей"""
    user_id = call.message.chat.id

    if user_id in user_records and user_records[user_id]:
        bot.send_message(user_id, "⏳ Сохраняем ваши записи...")

        bot.send_message(user_id, f"✅ Все записи сохранены!")

        # Очищаем записи
        user_records[user_id] = []
        user_last_voice[user_id] = []
        user_current_task[user_id] = 1
        user_waiting_for_action[user_id] = False

    else:
        bot.send_message(user_id, "⚠️ У вас пока нет записей для отправки.")

    # Возвращаем кнопку "Начать"
    bot.send_message(user_id, "Нажмите /start, чтобы записать новый текст.")

@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset(call):
    """Сброс состояния пользователя"""
    user_id = call.message.chat.id

    # Очищаем все данные пользователя
    if user_id in user_records:
        user_records[user_id] = []
    if user_id in user_last_voice:
        user_last_voice[user_id] = []
    if user_id in user_current_task:
        user_current_task[user_id] = 1
    if user_id in user_waiting_for_action:
        user_waiting_for_action[user_id] = False

    # Удаляем предыдущее меню
    try:
        bot.delete_message(user_id, call.message.message_id)
    except Exception:
        pass

    # Возвращаем пользователя к началу
    bot.send_message(user_id, "🔄 Состояние сброшено. Нажмите 'Начать', чтобы начать заново.", reply_markup=main_menu)

def get_action_menu(task_number):
    """Создает меню действий с учетом номера задания"""
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton("🔄 Перезаписать", callback_data="re_record"))

    if get_text_for_user(task_number + 1) != "Задание завершено!":
        menu.add(InlineKeyboardButton("➡️ Перейти к следующему заданию", callback_data="next_task"))

    menu.add(InlineKeyboardButton("📤 Отправить всё и закончить", callback_data="send"))
    menu.add(InlineKeyboardButton("🔄 Сброс", callback_data="reset"))  # Добавляем кнопку "Сброс"
    return menu

def get_unique_filename(user_id, index):
    """Генерирует уникальное имя файла"""
    version = 1
    file_path = os.path.join(SAVE_PATH, f"voice_{user_id}_{index}.ogg")

    while os.path.exists(file_path):
        version += 1
        file_path = os.path.join(SAVE_PATH, f"voice_{user_id}_{index}_{version}.ogg")

    return file_path


def get_random_image():
    """Выбирает случайное изображение из папки Image и возвращает путь и название файла без расширения"""
    image_folder = "Image"
    images = [f for f in os.listdir(image_folder) if f.endswith(".jpg")]

    if not images:
        return None, None

    random_image = random.choice(images)
    image_path = os.path.join(image_folder, random_image)
    image_name = os.path.splitext(random_image)[0]  # Убираем расширение

    return image_path, image_name

@bot.message_handler(func=lambda message: message.text in ["Да", "Нет"])
def handle_survey_choice(message):
    """Обрабатываем выбор пользователя"""
    user_id = message.chat.id

    if message.text == "Да":
        bot.send_message(user_id, "Отлично! Давайте начнем.")
        ask_next_question(user_id, 0)  # Начинаем с первого вопроса
    else:
        bot.send_message(user_id, "Хорошо, переходим к заданиям.", reply_markup=ReplyKeyboardRemove())
        send_task(user_id)  # Переход к заданиям

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)  # Пауза перед перезапуском
