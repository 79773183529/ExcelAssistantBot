import emoji
from aiogram import types, Dispatcher
from with_file import change_language, get_list_ru


async def cmd_language(message: types.Message):
    global list_ru
    change_language(message, list_ru)
    list_ru = get_list_ru()
    await message.answer(['Language changed to English',
                          'Язык изменён на русский'][str(message.from_user.id) in list_ru])


def register_handlers_language(dp: Dispatcher):
    dp.register_message_handler(cmd_language, commands="language", state="*")


list_ru = get_list_ru()
