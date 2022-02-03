import emoji
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType

from bot import bot, id_creator
from with_file import get_list_ru
from search_data import user_markup_exit


class OrderContact(StatesGroup):
    waiting_for_message = State()


async def cmd_contact(message: types.Message):
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    await message.answer(emoji.emojize(":woman_office_worker:"))
    await message.answer(['Now you can send me a message that I will forward to the developers or click '
                          '<b>/cancel</b> to cancel',
                          'Сейчас вы можете отправить мне сообщение, которое я перешлю разработчикам или нажмите'
                          ' <b>/cancel</b> для выхода'][in_ru],
                         parse_mode=types.ParseMode.HTML,
                         reply_markup=user_markup_exit)
    await OrderContact.waiting_for_message.set()


async def cmd_message(message: types.Message):
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru],
               ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    await message.answer(['The message has been sent',
                          ' Ваше сообщение отправлено'][in_ru],
                         parse_mode=types.ParseMode.HTML,
                         reply_markup=keyboard)
    await bot.send_message(id_creator,
                           f'Bot: WordAssistantBot \n'
                           f'ID: {message.from_user.id}\n'
                           f'name: {message.from_user.first_name}\n'
                           f'text: {message.text}\n'
                           )
    await bot.send_message(id_creator,
                           message)


def register_handlers_contact(dp: Dispatcher):
    dp.register_message_handler(cmd_contact, commands="contact", state="*")
    dp.register_message_handler(cmd_message,
                                content_types=[ContentType.VOICE, ContentType.TEXT, ContentType.DOCUMENT],
                                state=OrderContact.waiting_for_message)
