import telebot
from telebot import types
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш токен бота
API_TOKEN = '8255454287:AAGROqxH1GWUiu2kL9TmQavu-Bxtb3e791M'

bot = telebot.TeleBot(API_TOKEN)

# Список праздников РФ (дата: название)
HOLIDAYS = {
    (1, 1): "Новый год",
    (1, 2): "Новый год (продолжение)",
    (1, 7): "Рождество Христово",
    (2, 23): "День защитника Отечества",
    (3, 8): "Международный женский день",
    (5, 1): "Праздник Весны и Труда",
    (5, 9): "День Победы",
    (6, 12): "День России",
    (11, 4): "День народного единства"
}

def get_day_of_year():
    """Возвращает номер дня в году"""
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    return day_of_year

def get_next_holiday():
    """Возвращает ближайший праздник и количество дней до него"""
    today = date.today()
    current_year = today.year
    
    # Создаем список всех праздников в текущем и следующем году
    all_holidays = []
    for year in [current_year, current_year + 1]:
        for (month, day), name in HOLIDAYS.items():
            holiday_date = date(year, month, day)
            all_holidays.append((holiday_date, name))
    
    # Сортируем праздники по дате
    all_holidays.sort()
    
    # Находим ближайший праздник (включая сегодняшний)
    for holiday_date, name in all_holidays:
        if holiday_date >= today:
            days_until = (holiday_date - today).days
            return name, holiday_date, days_until
    
    return "Праздники не найдены", None, 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Какой день в году")
    btn2 = types.KeyboardButton("Ближайший праздник")
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для работы с датами.\n"
        "Выберите одну из опций:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Какой день в году")
def handle_day_of_year(message):
    """Обработчик кнопки 'Какой день в году'"""
    day_of_year = get_day_of_year()
    today = date.today()
    
    response = (
        f"📅 Сегодня {today.strftime('%d.%m.%Y')}\n"
        f"📊 Это {day_of_year}-й день в году\n"
        f"🎯 До конца года осталось {365 - day_of_year} дней"
    )
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == "Ближайший праздник")
def handle_next_holiday(message):
    """Обработчик кнопки 'Ближайший праздник'"""
    name, holiday_date, days_until = get_next_holiday()
    
    if holiday_date:
        if days_until == 0:
            response = f"🎉 Сегодня праздник: {name}!"
        else:
            response = (
                f"📅 Ближайший праздник: {name}\n"
                f"🗓️ Дата: {holiday_date.strftime('%d.%m.%Y')}\n"
                f"⏳ До праздника: {days_until} дней"
            )
    else:
        response = "❌ Не удалось найти информацию о праздниках"
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработчик всех остальных сообщений"""
    bot.send_message(
        message.chat.id,
        "Пожалуйста, используйте кнопки для взаимодействия с ботом."
    )

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
