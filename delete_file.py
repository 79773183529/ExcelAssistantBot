import asyncio

import emoji
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from bot import bot
from search_data import user_markup_exit
from with_file import get_list_topic, get_list_ru, delete_file

cb = CallbackData("call", "group", "id", "name")


class OrderDelete(StatesGroup):
    waiting_for_delete_file_name = State()
    waiting_for_delete_acknowledgment = State()


# Выводит на экран Inline клавиатуру с вариантами
async def delete_start(message: types.Message):
    list_ru = get_list_ru()
    markup_delete = types.InlineKeyboardMarkup()
    button, k = [], -1
    in_ru = str(message.from_user.id) in list_ru
    result = False
    for src in ['Data/Main_files/table_topics.txt', 'Data/Main_files/table_patterns.txt']:  # добавил Патерны !!!
        print('src(delete) = ', src)
        list_topic = get_list_topic(the_id=message.from_user.id, src=src)
        print('list_topic(delete) = ', list_topic)
        if list_topic:
            result = True
        for i in range(len(list_topic)):
            k += 1
            button.append(types.InlineKeyboardButton(text=[f'Delete: {list_topic[i][: -28]}',
                                                           f'Удалить: {list_topic[i][: -28]}'][in_ru],
                                                     callback_data=cb.new(group='delete',
                                                                          id=message.from_user.id,
                                                                          name=list_topic[i][-27:])
                                                     ))
            print('list_topic[i][:-28]= ', list_topic[i][:-28])
            markup_delete.row(button[k])
    if result:
        await message.answer(['Choose which of your files you want to delete',
                              'Выберите какой из ваших файлов вы хотите удалить'][in_ru],
                             reply_markup=markup_delete)
        await message.answer('..', reply_markup=user_markup_exit)
        await OrderDelete.waiting_for_delete_file_name.set()
    else:
        await message.answer(["You don't have any files yet",
                              'У вас пока нет файлов'][in_ru])
        await message.answer('..', reply_markup=user_markup_exit)


# Обрабатывает коллбеки.
async def search_delete_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    the_id = callback_data["id"]
    list_ru = get_list_ru()
    in_ru = str(the_id) in list_ru
    result = False
    delete_name = None
    for src in ['Data/Main_files/table_topics.txt', 'Data/Main_files/table_patterns.txt']:  #  добавил Патерны !!!
        list_topic = get_list_topic(the_id=callback_data["id"], src=src)
        for topic in list_topic:
            if callback_data['name'] in topic:
                delete_name = topic
                result = True
                break
        if result:
            break
    if delete_name:
        await state.update_data(delete_name=delete_name)
        markup = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(['YES', 'ДА'][in_ru],
                                                callback_data=cb.new(group='delete_acknowledgment',
                                                                     id=the_id,
                                                                     name='yes'))
        markup.row(button_yes)
        button_no = types.InlineKeyboardButton(['NO', 'НЕТ'][in_ru],
                                               callback_data=cb.new(group='delete_acknowledgment',
                                                                    id=the_id,
                                                                    name='no'))
        markup.row(button_no)
        await bot.send_message(the_id, emoji.emojize(":woman_pouting:"))
        await bot.send_message(the_id, [f'Did I understand you correctly?\n'
                                        f'Do you really want to delete:\n<i>"{delete_name[: -28]}"</i>',
                                        f'Вы уверены?\n'
                                        f'Вы действительно хотите удалить:\n<i>"{delete_name[: -28]}"</i>'][in_ru],
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=markup)
        await call.answer()
        await OrderDelete.waiting_for_delete_acknowledgment.set()
        await bot.send_message(the_id, '..', reply_markup=user_markup_exit)
    else:
        await bot.send_message(the_id, ['This file has already been deleted', 'Этот файл уже удалён'][in_ru])
        await call.answer()
        await bot.send_message(the_id, '..', reply_markup=user_markup_exit)


# Обрабатывает коллбеки подтверждения удаления
async def delete_acknowledgment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    the_id = callback_data["id"]
    in_ru = str(the_id) in get_list_ru()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru],
               ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    if callback_data["name"] == 'no':
        await bot.send_message(the_id, emoji.emojize(":woman_tipping_hand:"))
        await bot.send_message(the_id, ['Select the file you want to delete or click  <b>/cancel</b>  to exit',
                                        'Выберите файл, который вы хотите удалить мли нажмите  <b>/cancel</b>  '
                                        'для выхода'][in_ru],
                               parse_mode=types.ParseMode.HTML)
        await call.answer()
        await bot.send_message(the_id, '..', reply_markup=user_markup_exit)
        await OrderDelete.waiting_for_delete_file_name.set()
    else:
        user_data = await state.get_data()
        await bot.send_message(the_id, emoji.emojize(":axe:"))
        delete_name = user_data['delete_name']
        delete_file(delete_name)
        await call.answer()
        await asyncio.sleep(2)
        await bot.send_message(the_id, ['File deleted', 'Файл удалён'][in_ru], reply_markup=keyboard)


def register_handlers_delete(dp: Dispatcher):
    dp.register_message_handler(delete_start, commands="delete", state="*")
    dp.register_callback_query_handler(search_delete_chosen,
                                       cb.filter(group=['delete']),
                                       state=OrderDelete.waiting_for_delete_file_name)
    dp.register_callback_query_handler(delete_acknowledgment,
                                       cb.filter(group=['delete_acknowledgment']),
                                       state=OrderDelete.waiting_for_delete_acknowledgment)
