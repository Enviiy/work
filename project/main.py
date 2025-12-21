import telebot
from telebot import types
import crud.list as list_db

API_TOKEN = '8328540055:AAGr0cvV6H7HvM32T4irVug6Z5Q6k4pBfIQ'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    list_db.table() 
    
    first_name = message.from_user.first_name
    user_id = message.from_user.id

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    newlist_btn = types.KeyboardButton(text="/newlist")
    viewlists_btn = types.KeyboardButton(text="/viewlists")
    additem_btn = types.KeyboardButton(text="/additem")
    showlist_btn = types.KeyboardButton(text="/showlist")
    delitem_btn = types.KeyboardButton(text="/deleteitem")
    dellist_btn = types.KeyboardButton(text="/deletelist")
    kb.add(newlist_btn, viewlists_btn, additem_btn, showlist_btn, delitem_btn, dellist_btn)
    
    bot.send_message(message.chat.id, f"Привет, {first_name}, я бот для списка продуктов! \n\nПропиши /help - чтобы увидеть все мои команды!", reply_markup=kb)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Список всех команд:"
        "\n\nСписки покупок"
        "\n/newlist - Создать новый список"
        "\n/viewlists - Посмотреть все списки"
        "\n/additem - Добавить товар в список"
        "\n/showlist - Показать товары в списке"
        "\n/deleteitem - Удалить товар из списка"
        "\n/deletelist - Удалить список"
    )


@bot.message_handler(commands=['newlist'])
def post_list(message):
    bot.send_message(message.chat.id, "Введите название списка.\n\nЕсли хотите отменить создание списка, введите \"Отмена.\"")
    bot.register_next_step_handler(message, create_list_name)

def create_list_name(message):
    user_id = message.from_user.id
    if message.text != "Отмена.":
        name = message.text
        lst = {}
        lst['name'] = name
        lst['user_id'] = user_id
        list_id = list_db.create_list(lst)
        
        bot.send_message(message.chat.id, f"Список \"{name}\" создан! ID списка: {list_id}")

        bot.send_message(message.chat.id, "Теперь можете добавить товары в этот список командой /additem")
        
        bot.send_message(message.chat.id, "Хотите сразу добавить товар? Введите название товара или \"Отмена.\" чтобы пропустить")
        bot.register_next_step_handler(message, add_item_after_creation, list_id)
    else:
        bot.send_message(message.chat.id, "Отмена создания списка")

def add_item_after_creation(message, list_id):
    if message.text != "Отмена.":
        item = {}
        item['list_id'] = list_id
        item['product_name'] = message.text
        
        bot.send_message(message.chat.id, "Введите количество товара.\n\nЕсли хотите отменить добавление, введите \"Отмена.\"")
        bot.register_next_step_handler(message, add_item_quantity, item)
    else:
        bot.send_message(message.chat.id, "Хорошо, список создан. Вы всегда можете добавить товары позже командой /additem")

@bot.message_handler(commands=['viewlists'])
def view_lists(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Все ваши списки:")
    lists = list_db.read_lists(user_id)
    for lst in lists:
        kb = types.InlineKeyboardMarkup(row_width=2)
        show_btn = types.InlineKeyboardButton(text=f"Показать", callback_data=f"/showlist {lst['id']}")
        delete_btn = types.InlineKeyboardButton(text="\tУдалить\t", callback_data=f"/deletelist {lst['id']}")
        kb.add(show_btn, delete_btn)
        bot.send_message(message.chat.id, f"id - {lst['id']} \n{lst['name']} - {lst['total_price']} руб.", reply_markup=kb)


@bot.message_handler(commands=['additem'])
def add_item(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Введите id списка, в который хотите добавить товар.\n\nЕсли хотите отменить добавление, введите \"Отмена.\"")
    bot.register_next_step_handler(message, add_item_list_id, user_id)

def add_item_list_id(message, user_id):
    if message.text != "Отмена.":
        list_id = message.text
        if list_id.isdigit() and list_db.check_list_id(list_id, user_id):
            item = {}
            item['list_id'] = list_id
            bot.send_message(message.chat.id, "Введите название товара.\n\nЕсли хотите отменить добавление, введите \"Отмена.\"")
            bot.register_next_step_handler(message, add_item_name, item)
        else:
            bot.send_message(message.chat.id, "Неправильный ввод. Введите id списка ещё раз")
            bot.register_next_step_handler(message, add_item_list_id, user_id)
    else:
        bot.send_message(message.chat.id, "Отмена добавления товара")

def add_item_name(message, item):
    if message.text != "Отмена.":
        product_name = message.text
        item['product_name'] = product_name
        bot.send_message(message.chat.id, "Введите количество товара.\n\nЕсли хотите отменить добавление, введите \"Отмена.\"")
        bot.register_next_step_handler(message, add_item_quantity, item)
    else:
        bot.send_message(message.chat.id, "Отмена добавления товара")

def add_item_quantity(message, item):
    if message.text != "Отмена.":
        quantity = message.text
        if quantity.isdigit():
            item['quantity'] = quantity
            bot.send_message(message.chat.id, "Введите цену товара.\n\nЕсли хотите отменить добавление, введите \"Отмена.\"")
            bot.register_next_step_handler(message, add_item_price, item)
        else:
            bot.send_message(message.chat.id, "Неправильный ввод. Количество должно состоять из цифр")
            bot.register_next_step_handler(message, add_item_quantity, item)
    else:
        bot.send_message(message.chat.id, "Отмена добавления товара")

def add_item_price(message, item):
    if message.text != "Отмена.":
        price = message.text
        if price.isdigit():
            item['price'] = price
            list_db.add_item(item)
            bot.send_message(message.chat.id, "Товар добавлен в список")
        else:
            bot.send_message(message.chat.id, "Неправильный ввод. Цена должна состоять из цифр")
            bot.register_next_step_handler(message, add_item_price, item)
    else:
        bot.send_message(message.chat.id, "Отмена добавления товара")


@bot.message_handler(commands=['showlist'])
def show_list(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Введите id списка, который хотите посмотреть.\n\nЕсли хотите отменить просмотр, введите \"Отмена.\"")
    bot.register_next_step_handler(message, show_list_id, user_id)

def show_list_id(message, user_id):
    if message.text != "Отмена.":
        list_id = message.text
        if list_id.isdigit() and list_db.check_list_id(list_id, user_id):
            lst = list_db.read_list(list_id, user_id)
            if lst:
                text = f"📋 Список: {lst['name']}\n"
                text += f"💰 Общая сумма: {lst['total_price']} руб.\n\n"
                
                if lst['items']:
                    for item in lst['items']:
                        status = "✅" if item['is_purchased'] else "⬜"
                        text += f"{status} {item['product_name']} - {item['quantity']} x {item['price']} руб. = {item['total']} руб.\n"
                else:
                    text += "Список пуст. Добавьте товары командой /additem"
                
                bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, "Неправильный ввод. Введите id списка ещё раз")
            bot.register_next_step_handler(message, show_list_id, user_id)
    else:
        bot.send_message(message.chat.id, "Отмена просмотра списка")


@bot.message_handler(commands=['deleteitem'])
def delete_item(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Введите id товара, который хотите удалить из списка.\n\nЕсли хотите отменить удаление, введите \"Отмена.\"")
    bot.register_next_step_handler(message, delete_item_id, user_id)

def delete_item_id(message, user_id):
    if message.text != "Отмена.":
        item_id = message.text
        if item_id.isdigit() and list_db.check_item_id(item_id, user_id):
            bot.send_message(message.chat.id, "Вы уверены, что хотите удалить товар из списка? Если да, то напишите \"Удалить.\"\n\nЕсли хотите отменить удаление, введите \"Отмена.\"")
            bot.register_next_step_handler(message, delete_item_check, item_id)
        else:
            bot.send_message(message.chat.id, "Неправильный ввод. Введите id товара ещё раз")
            bot.register_next_step_handler(message, delete_item_id, user_id)
    else:
        bot.send_message(message.chat.id, "Отмена удаления товара")

def delete_item_check(message, item_id):
    if message.text != "Отмена.":
        if message.text == "Удалить.":
            list_db.delete_item(item_id)
            bot.send_message(message.chat.id, "Товар удалён из списка")
    else:
        bot.send_message(message.chat.id, "Отмена удаления товара")


@bot.message_handler(commands=['deletelist'])
def delete_list_command(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Введите id списка, который хотите удалить.\n\nЕсли хотите отменить удаление, введите \"Отмена.\"")
    bot.register_next_step_handler(message, delete_list_id, user_id)

def delete_list_id(message, user_id):
    if message.text != "Отмена.":
        list_id = message.text
        if list_id.isdigit() and list_db.check_list_id(list_id, user_id):
            bot.send_message(message.chat.id, "Вы уверены, что хотите удалить список? Если да, то напишите \"Удалить.\"\n\nЕсли хотите отменить удаление, введите \"Отмена.\"")
            bot.register_next_step_handler(message, delete_list_check, list_id)
        else:
            bot.send_message(message.chat.id, "Неправильный ввод. Введите id списка ещё раз")
            bot.register_next_step_handler(message, delete_list_id, user_id)
    else:
        bot.send_message(message.chat.id, "Отмена удаления списка")

def delete_list_check(message, list_id):
    if message.text != "Отмена.":
        if message.text == "Удалить.":
            list_db.delete_list(list_id)
            bot.send_message(message.chat.id, "Список удалён")
    else:
        bot.send_message(message.chat.id, "Отмена удаления списка")


@bot.callback_query_handler(func=lambda callback: callback.data)
def make_callback(callback):
    data = callback.data.split()
    user_id = callback.from_user.id
    
    if len(data) >= 2:
        if data[0] == "/showlist":
            list_id = data[1]
            if list_id.isdigit() and list_db.check_list_id(list_id, user_id):
                lst = list_db.read_list(list_id, user_id)
                if lst:
                    text = f" Список: {lst['name']}\n"
                    text += f" Общая сумма: {lst['total_price']} руб.\n\n"
                    
                    if lst['items']:
                        for item in lst['items']:
                            status = "✅" if item['is_purchased'] else "⬜"
                            text += f"{status} {item['product_name']} - {item['quantity']} x {item['price']} руб. = {item['total']} руб.\n"
                            
                            kb = types.InlineKeyboardMarkup(row_width=2)
                            toggle_btn = types.InlineKeyboardButton(
                                text=f"Отметить {'✅' if not item['is_purchased'] else '⬜'}",
                                callback_data=f"/toggleitem {item['id']}"
                            )
                            delete_btn = types.InlineKeyboardButton(
                                text="Удалить из списка",
                                callback_data=f"/deleteitemcallback {item['id']}"
                            )
                            kb.add(toggle_btn, delete_btn)
                            
                            bot.send_message(callback.message.chat.id, 
                                            f"{status} {item['product_name']} - {item['quantity']} x {item['price']} руб. = {item['total']} руб.",
                                            reply_markup=kb)
                    else:
                        text += "Список пуст. Добавьте товары командой /additem"
                        bot.send_message(callback.message.chat.id, text)
        
        elif data[0] == "/deletelist":
            list_id = data[1]
            if list_id.isdigit() and list_db.check_list_id(list_id, user_id):
                bot.send_message(callback.message.chat.id, "Вы уверены, что хотите удалить список? Если да, то напишите \"Удалить.\"\n\nЕсли хотите отменить удаление, введите \"Отмена.\"")
                bot.register_next_step_handler(callback.message, delete_list_check, list_id)
        
        elif data[0] == "/toggleitem":
            item_id = data[1]
            if item_id.isdigit() and list_db.check_item_id(item_id, user_id):
                list_db.toggle_purchased(item_id)
                bot.send_message(callback.message.chat.id, "Статус товара изменён")
        
        elif data[0] == "/deleteitemcallback":
            item_id = data[1]
            if item_id.isdigit() and list_db.check_item_id(item_id, user_id):
                list_db.delete_item(item_id)
                bot.send_message(callback.message.chat.id, "Товар удалён из списка")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "Такой команды нет")


bot.infinity_polling()