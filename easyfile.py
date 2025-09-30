import telebot
from telebot import types
import os
from PIL import Image
import io

# Токен бота (получи у @BotFather)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем папку для временных файлов
if not os.path.exists('temp'):
    os.makedirs('temp')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    welcome_text = """
🤖 Привет! Я бот для конвертации изображений.

Отправь мне фото, и я преобразую его в нужный формат файла.

📁 Поддерживаемые форматы:
• PNG
• JPEG/JPG
• BMP
• TIFF
• WEBP

Просто отправь мне изображение!
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Обработчик команды /help"""
    help_text = """
📖 Помощь по использованию бота:

1. Отправь мне любое изображение
2. Я автоматически определю его формат
3. Получи преобразованное изображение в нужном формате

💡 Бот поддерживает конвертацию между всеми популярными форматами изображений.
    """
    bot.reply_to(message, help_text)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Обработчик получения фото"""
    try:
        # Отправляем сообщение о начале обработки
        processing_msg = bot.reply_to(message, "🔄 Обрабатываю изображение...")
        
        # Получаем файл самого высокого качества
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Создаем временное имя файла
        temp_input = f"temp/input_{message.chat.id}.jpg"
        temp_output = f"temp/output_{message.chat.id}"
        
        # Сохраняем исходное изображение
        with open(temp_input, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Открываем изображение с помощью PIL
        with Image.open(temp_input) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Создаем клавиатуру с выбором формата
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_png = types.InlineKeyboardButton('PNG', callback_data='format_png')
            btn_jpg = types.InlineKeyboardButton('JPEG', callback_data='format_jpg')
            btn_bmp = types.InlineKeyboardButton('BMP', callback_data='format_bmp')
            btn_tiff = types.InlineKeyboardButton('TIFF', callback_data='format_tiff')
            btn_webp = types.InlineKeyboardButton('WEBP', callback_data='format_webp')
            
            markup.add(btn_png, btn_jpg, btn_bmp, btn_tiff, btn_webp)
            
            # Удаляем сообщение о обработке
            bot.delete_message(message.chat.id, processing_msg.message_id)
            
            # Отправляем сообщение с выбором формата
            bot.send_message(
                message.chat.id,
                "📁 Выбери формат для конвертации:",
                reply_markup=markup
            )
            
            # Сохраняем информацию об изображении для callback
            img.save(f"{temp_output}_temp.jpg", "JPEG")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка при обработке изображения: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('format_'))
def handle_format_selection(call):
    """Обработчик выбора формата"""
    try:
        # Извлекаем выбранный формат
        format_type = call.data.split('_')[1].upper()
        
        # Обновляем сообщение
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🔄 Конвертирую в {format_type}..."
        )
        
        temp_output = f"temp/output_{call.message.chat.id}"
        
        # Открываем временное изображение
        with Image.open(f"{temp_output}_temp.jpg") as img:
            # Создаем байтовый поток для сохранения
            img_byte_arr = io.BytesIO()
            
            # Сохраняем в выбранном формате
            if format_type == 'JPG':
                format_type = 'JPEG'
                img.save(img_byte_arr, format='JPEG', quality=95)
                file_extension = 'jpg'
            elif format_type == 'PNG':
                img.save(img_byte_arr, format='PNG')
                file_extension = 'png'
            elif format_type == 'BMP':
                img.save(img_byte_arr, format='BMP')
                file_extension = 'bmp'
            elif format_type == 'TIFF':
                img.save(img_byte_arr, format='TIFF')
                file_extension = 'tiff'
            elif format_type == 'WEBP':
                img.save(img_byte_arr, format='WEBP', quality=80)
                file_extension = 'webp'
            else:
                img.save(img_byte_arr, format='JPEG')
                file_extension = 'jpg'
            
            # Перемещаем указатель в начало
            img_byte_arr.seek(0)
            
            # Отправляем файл пользователю
            bot.send_document(
                call.message.chat.id,
                img_byte_arr,
                caption=f"✅ Изображение успешно конвертировано в {format_type}",
                visible_file_name=f"converted_image.{file_extension}"
            )
        
        # Удаляем сообщение о конвертации
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"❌ Ошибка при конвертации: {str(e)}"
        )

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Обработчик документов (изображений отправленных как файл)"""
    if message.document.mime_type and message.document.mime_type.startswith('image/'):
        try:
            # Отправляем сообщение о начале обработки
            processing_msg = bot.reply_to(message, "🔄 Обрабатываю изображение...")
            
            # Получаем файл
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Создаем временное имя файла
            temp_input = f"temp/input_doc_{message.chat.id}"
            temp_output = f"temp/output_{message.chat.id}"
            
            # Сохраняем исходное изображение
            with open(temp_input, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            # Открываем изображение с помощью PIL
            with Image.open(temp_input) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Создаем клавиатуру с выбором формата
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn_png = types.InlineKeyboardButton('PNG', callback_data='format_png')
                btn_jpg = types.InlineKeyboardButton('JPEG', callback_data='format_jpg')
                btn_bmp = types.InlineKeyboardButton('BMP', callback_data='format_bmp')
                btn_tiff = types.InlineKeyboardButton('TIFF', callback_data='format_tiff')
                btn_webp = types.InlineKeyboardButton('WEBP', callback_data='format_webp')
                
                markup.add(btn_png, btn_jpg, btn_bmp, btn_tiff, btn_webp)
                
                # Удаляем сообщение о обработке
                bot.delete_message(message.chat.id, processing_msg.message_id)
                
                # Отправляем сообщение с выбором формата
                bot.send_message(
                    message.chat.id,
                    "📁 Выбери формат для конвертации:",
                    reply_markup=markup
                )
                
                # Сохраняем информацию об изображении для callback
                img.save(f"{temp_output}_temp.jpg", "JPEG")
                
        except Exception as e:
            bot.reply_to(message, f"❌ Произошла ошибка при обработке изображения: {str(e)}")
    else:
        bot.reply_to(message, "❌ Пожалуйста, отправьте изображение.")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработчик всех остальных сообщений"""
    bot.reply_to(message, "📸 Отправь мне изображение для конвертации!")

def cleanup_temp_files():
    """Очистка временных файлов (опционально)"""
    import glob
    temp_files = glob.glob('temp/*')
    for file in temp_files:
        try:
            os.remove(file)
        except:
            pass

if __name__ == "__main__":
    print("Бот запущен...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        cleanup_temp_files()