import asyncio
import datetime
import subprocess
import random
import urllib.request
import pandas as pd
from openpyxl import load_workbook
import os
import numpy as np

import emoji
import speech_recognition as sr

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from aiogram.utils.callback_data import CallbackData

from bot import bot, TOKEN
from with_file import get_list_topic, name_to_src, get_list_ru, get_list_df, is_text_in_df
from word_start import search_object_in_src

cb = CallbackData("call", "group", "id", "name")


class OrderSearch(StatesGroup):
    waiting_for_file_name = State()
    waiting_for_file = State()
    waiting_for_object = State()
    waiting_for_acknowledgment = State()
    waiting_for_accuracy = State()


# Выводит на экран Inline клавиатуру с вариантами
async def search_start(message: types.Message):
    list_topic = get_list_topic(the_id=message.from_user.id)
    print('list_topic= ', list_topic)
    markup = types.InlineKeyboardMarkup()
    button = []
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    for i in range(len(list_topic)):
        button.append(types.InlineKeyboardButton(text=[f'Search in {list_topic[i][: -28]}',
                                                       f'Искать в: {list_topic[i][: -28]}'][in_ru],
                                                 callback_data=cb.new(group='topic',
                                                                      id=message.from_user.id,
                                                                      name=list_topic[i][-27:])
                                                 ))
        print('list_topic[i][-27:]= ', list_topic[i][-27:])
        markup.row(button[i])
    if len(list_topic) > 1:
        button_choice_all = types.InlineKeyboardButton(['Search everywhere', 'Искать везде'][in_ru],
                                                       callback_data=cb.new(group='topic',
                                                                            id=message.from_user.id,
                                                                            name='search_everywhere'))
        markup.row(button_choice_all)

    button_choice_other = types.InlineKeyboardButton(['Upload a new file', 'Загрузить новый файл'][in_ru],
                                                     callback_data=cb.new(group='topic',
                                                                          id=message.from_user.id,
                                                                          name='create_new_topic'))
    markup.row(button_choice_other)
    await message.answer(['Select an option', f'Выберите нужный  вариант '][in_ru], reply_markup=markup)
    await message.answer('..', reply_markup=user_markup_exit)
    await OrderSearch.waiting_for_file_name.set()


# Обрабатывает коллбеки. Обратите внимание: есть второй аргумент
async def search_location_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    list_ru = get_list_ru()
    in_ru = str(callback_data["id"]) in list_ru
    if callback_data["name"] == 'create_new_topic':
        await bot.send_message(callback_data["id"],
                               ['Ok. Send me this file',
                                'Хорошо. Пришлите мне этот файл'][in_ru])
        await call.answer()
        await OrderSearch.waiting_for_file.set()
    else:
        list_topic = get_list_topic(the_id=callback_data["id"])
        for topic in list_topic:
            print('if callback_data["name"] = ', callback_data['name'], 'in topic= ', topic)
            if callback_data['name'] in topic:
                print('!!! callback_data["name"] = ', callback_data['name'], 'in topic= ', topic)
                list_topic = [topic]
                print("Я в ife. list_topic=", list_topic)
                break
        list_src_topic = name_to_src(lst=list_topic)
        print('name_to_src  send: ', list_src_topic)
        list_src_topic = list_src_topic[0].strip('"[]').split(', ')
        list_src_topic = list(map(lambda x: x.strip("'"), list_src_topic))
        print('list_src_topic = ', list_src_topic)
        await bot.send_message(callback_data["id"],
                               ['Ok. Now send me what we need to find',
                                'Хорошо. Теперь пришлите мне, что нам нужно найти'][in_ru])
        await state.update_data(list_src=list_src_topic)
        await call.answer()
        await OrderSearch.waiting_for_object.set()


# Принимает новый файл .docx
async def search_set_file(message: types.Message, state: FSMContext):
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    if not message.document or '.xls' not in message.document.file_name:
        await message.reply(["The file must be Excel.\nTry again",
                             "Файл должен быть Эксель ..\nПопробуйте ещё раз"][in_ru])
        return
    else:
        try:
            chat_id = message.chat.id
            make_topic_time = datetime.datetime.now() + datetime.timedelta(hours=3)  # Перевод в Московское время
            make_topic_time = make_topic_time.strftime('%Y.%m.%d-%H.%M')

            document_id = message.document.file_id
            file_info = await bot.get_file(document_id)

            fi = file_info.file_path
            name = message.document.file_name

            print('name= ', name)
            src_new = f'Data/User_files/Topics/{chat_id}_{random.randrange(10000)}_{name}'
            src_new = src_new.replace(';', '_')
            src_new = src_new.replace(' ', '_')
            src_topic = src_new.replace(',', '_')

            urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',
                                       src_topic)

            if '.csv' in src_topic:
                list_src_topics = [src_topic]
            else:
                list_src_topics = []
                xlsx = pd.ExcelFile(src_topic, engine='openpyxl')
                sheets = xlsx.sheet_names
                wb = load_workbook(src_topic)
                for sheet in sheets:
                    the_sheet = wb[sheet]
                    row = 0
                    for i in range(1, 16):
                        position = 'B' + str(i)
                        if the_sheet[position].border.top.style == "thin" \
                                or the_sheet[position].border.top.style == "thick":
                            print(f"Ячейка {position} имеет границу сверху")
                            row = i - 1
                            break
                    df = xlsx.parse(sheet, skiprows=row)
                    df.columns = df.columns.str.strip()
                    print(df)
                    if not df.empty:
                        if df.shape[1] > 200:
                            df = df.iloc[:, : 50]
                        src_topic_el = '.'.join(src_topic.split('.')[:-1]) + '_' + sheet + '_' + '.csv'
                        df.to_csv(src_topic_el, sep=';', encoding='utf-8-sig', index=False)
                        list_src_topics.append(src_topic_el)
                        print('list_src_topics = ', list_src_topics)
                # os.remove(src_topic)
            print(list_src_topics)

            with open('Data/Main_files/table_topics.txt', 'a', encoding='utf-8') as f:
                name_topic = name + '_' + make_topic_time + '_' + '(cod_' + str(random.randrange(10000)) + ')'
                name_topic = name_topic.replace(';', '_')
                name_topic = name_topic.replace(':', '_')
                print(name_topic, message.from_user.id, list_src_topics, True, sep=';', file=f)

            await message.reply(['File saved\nSend me what you want to find in it',
                                 "Файл  успешно сохранён\nПришлите мне, что вы хотите в нём найти"][in_ru])
            await asyncio.sleep(2)
            await message.answer(['And by the way, you do not have to type'
                                  ' - i understand voice messages perfectly',
                                  'Да и кстати вам не обязательно печатать '
                                  '- я прекрасно понимаю голосовые сообщения'][in_ru])
            await state.update_data(list_src=list_src_topics)
            await OrderSearch.waiting_for_object.set()
        except Exception as e:
            print(e)


# Принимает объект для поиска
async def search_set_object(message: types.voice, state: FSMContext):
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru],
               ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    try:
        document_id = message.voice.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path

        await message.answer(emoji.emojize(":deaf_woman:"))

        file_name = 'audio.ogg'
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',
                                   file_name)

        process = subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])
        file = sr.AudioFile('audio.wav')
        with file as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language=['en-US', 'ru-RU'][in_ru])
            print('voice_to_text return: ', text)

        markup = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(['That is right. Continue', 'Всё верно. Продолжить'][in_ru],
                                                callback_data=cb.new(group='acknowledgment',
                                                                     id=message.from_user.id,
                                                                     name='yes'))
        markup.row(button_yes)
        button_no = types.InlineKeyboardButton(['No. Repeat input', 'Нет. Повторить ввод'][in_ru],
                                               callback_data=cb.new(group='acknowledgment',
                                                                    id=message.from_user.id,
                                                                    name='no'))
        markup.row(button_no)
        await message.answer([f'Did I understand you correctly?\n We are looking for: "{text}"',
                              f'Я вас правильно поняла?\n Мы ищем: "{text}"'][in_ru],
                             reply_markup=markup)

        await message.answer('..', reply_markup=user_markup_exit)
        await state.update_data(the_object=text)
        await OrderSearch.waiting_for_acknowledgment.set()
    except Exception as e:
        print(e)
        print('message.text= ', message.text)
        await state.update_data(the_object=message.text)
        markup_accuracy = types.InlineKeyboardMarkup()
        button_full = types.InlineKeyboardButton(['Full match', 'Абсолютное совпадение'][in_ru],
                                                 callback_data=cb.new(group='accuracy',
                                                                      id=message.from_user.id,
                                                                      name='full'))
        markup_accuracy.row(button_full)
        button_include = types.InlineKeyboardButton(['Entry into the cell', 'Вхождение в ячейку'][in_ru],
                                                    callback_data=cb.new(group='accuracy',
                                                                         id=message.from_user.id,
                                                                         name='include'))
        markup_accuracy.row(button_include)
        await message.answer([f"Let's further clarify the accuracy of the search:\n we will search for cells that"
                              f" absolutely match the text, or is it enough for us to enter the cell",
                              f'Давайте ещё уточним точность поиска:\nБудем искать ячейки абсолютно совпадающие'
                              f' с текстом или нам достаточно вхождения в ячейку'][in_ru],
                             reply_markup=markup_accuracy)
        await OrderSearch.waiting_for_accuracy.set()


# Обрабатывает коллбеки - точности поиска и отпраляет РЕЗУЛЬТАТ
async def set_accuracy(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    list_ru = get_list_ru()
    in_ru = str(callback_data["id"]) in list_ru
    if callback_data["name"] == 'full':
        search_accuracy = 0
    else:
        search_accuracy = 1
    user_data = await state.get_data()
    the_object = user_data['the_object']
    list_src = user_data['list_src']
    print("It is victory ", search_accuracy)
    list_df = get_list_df(list_src)
    print(list_df)
    result = False
    for df in list_df:
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_technologist:"))
        list_rows = is_text_in_df(df, the_object, search_accuracy)
        list_rows = list(set(list_rows))
        for row in list_rows:
            for column in df.columns.values:
                value = df.at[row, column]
                if value is not np.NaN and str(value) != 'NaN' and str(value) != 'nan':
                    result = True
                    print(f'{column}:   {value}')
                    print(type(value))
                    await bot.send_message(callback_data["id"], f'{column}:   {value}')
            await bot.send_message(callback_data["id"], '____________')
            await asyncio.sleep(2)
    if not result:
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_shrugging:"))
        await bot.send_message(callback_data["id"], ['Nothing found', 'Ничего не найдено'][in_ru])

    await bot.send_message(callback_data["id"],
                           ['You can repeat the search or press \n<b>/cancel</b>\n ',
                            'Вы можете повторить поиск или нажать \n<b>/cancel</b>\n для выхода'][in_ru],
                           parse_mode=types.ParseMode.HTML,
                           reply_markup=user_markup_exit)
    await OrderSearch.waiting_for_object.set()
    await call.answer()


# Обрабатывает коллбеки - подтверждения после обработки голосового сообщения
async def set_acknowledgment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    list_ru = get_list_ru()
    in_ru = str(callback_data["id"]) in list_ru
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru],
               ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    if callback_data["name"] == 'no':
        await bot.send_message(callback_data["id"],
                               [f'{emoji.emojize(":woman_shrugging:")}  Well, it happens. '
                                f'Send me your search text again',
                                emoji.emojize(":woman_shrugging:") + '  Что ж такое бывает. '
                                                                     'Пришлите мне ваш текст для'
                                                                     ' поиска ещё раз'][in_ru])
        await call.answer()
        await bot.send_message(callback_data["id"], '..', reply_markup=user_markup_exit)
        await OrderSearch.waiting_for_object.set()
    elif callback_data["name"] == 'yes':
        markup_accuracy = types.InlineKeyboardMarkup()
        button_full = types.InlineKeyboardButton(['Full match', 'Абсолютное совпадение'][in_ru],
                                                 callback_data=cb.new(group='accuracy',
                                                                      id=callback_data["id"],
                                                                      name='full'))
        markup_accuracy.row(button_full)
        button_include = types.InlineKeyboardButton(['Entry into the cell', 'Вхождение в ячейку'][in_ru],
                                                    callback_data=cb.new(group='accuracy',
                                                                         id=callback_data["id"],
                                                                         name='include'))
        markup_accuracy.row(button_include)
        await bot.send_message(callback_data["id"],
                               [f"Let's further clarify the accuracy of the search:\n"
                                f" we will search for cells that"
                                f" absolutely match the text, or is it enough for us to enter the cell",
                                f'Давайте ещё уточним точность поиска:\nБудем искать ячейки абсолютно совпадающие'
                                f' с текстом или нам достаточно вхождения в ячейку'][in_ru],
                               reply_markup=markup_accuracy)
        await call.answer()
        await OrderSearch.waiting_for_accuracy.set()


def register_handlers_search(dp: Dispatcher):
    dp.register_message_handler(search_start, commands="searchdata", state="*")
    dp.register_callback_query_handler(search_location_chosen,
                                       cb.filter(group=['topic']),
                                       state=OrderSearch.waiting_for_file_name)
    dp.register_message_handler(search_set_file,
                                content_types=['document'],
                                state=OrderSearch.waiting_for_file)
    dp.register_message_handler(search_set_object,
                                content_types=[ContentType.VOICE, ContentType.TEXT],
                                state=OrderSearch.waiting_for_object)
    dp.register_callback_query_handler(set_acknowledgment,
                                       cb.filter(group=['acknowledgment']),
                                       state=OrderSearch.waiting_for_acknowledgment)
    dp.register_callback_query_handler(set_accuracy,
                                       cb.filter(group=['accuracy']),
                                       state=OrderSearch.waiting_for_accuracy)


user_markup_exit = types.ReplyKeyboardMarkup(resize_keyboard=True)
user_markup_exit.row('/cancel')

r = sr.Recognizer()
