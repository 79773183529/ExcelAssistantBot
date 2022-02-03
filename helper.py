import emoji
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

import asyncio

from search_data import user_markup_exit
from with_file import get_list_ru
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from bot import bot

cb = CallbackData("call", "group", "id", "name")


class OrderHelp(StatesGroup):
    waiting_for_chapter = State()


# Создаём инлайн клавиатуру
async def help_start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    button = []
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru

    button_help_search = types.InlineKeyboardButton(['Search data', 'Поиск данных'][in_ru],
                                                    callback_data=cb.new(group='help',
                                                                         id=message.from_user.id,
                                                                         name='search_data'))
    markup.row(button_help_search)

    button_help_fill = types.InlineKeyboardButton(['Filling in the template', 'Заполнение шаблона'][in_ru],
                                                  callback_data=cb.new(group='help',
                                                                       id=message.from_user.id,
                                                                       name='fill_pattern'))
    markup.row(button_help_fill)

    button_help_delete = types.InlineKeyboardButton(['Delete a file', 'Удалить файл'][in_ru],
                                                    callback_data=cb.new(group='help',
                                                                         id=message.from_user.id,
                                                                         name='delete'))
    markup.row(button_help_delete)

    button_help_contact = types.InlineKeyboardButton(['contact the developers', 'Связаться с разработчиком'][in_ru],
                                                     callback_data=cb.new(group='help',
                                                                          id=message.from_user.id,
                                                                          name='contact'))
    markup.row(button_help_contact)

    button_help_help = types.InlineKeyboardButton(['Get help', 'Получить помощь'][in_ru],
                                                  callback_data=cb.new(group='help',
                                                                       id=message.from_user.id,
                                                                       name='help'))
    markup.row(button_help_help)

    await message.answer(emoji.emojize(":woman_office_worker:"))
    await message.answer(['What can I help you with ?', 'В чём я могу вам помочь ?'][in_ru], reply_markup=markup)
    await message.answer('..', reply_markup=user_markup_exit)
    await OrderHelp.waiting_for_chapter.set()


async def set_help(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    list_ru = get_list_ru()
    in_ru = str(callback_data["id"]) in list_ru
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru],
               ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    if callback_data["name"] == 'search_data':
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_technologist:"))
        await bot.send_message(callback_data["id"],
                               ['Probably, every person had moments when he urgently needed to find some information in'
                                ' his files – and there was no computer at hand. Fortunately, there is no need to worry'
                                ' about that right now. I can easily help you with this:\n\n To do this, enter the'
                                ' menu - click <b>/searchdata</b>. Next, if you have not sent me the file you need yet'
                                ' – in'
                                ' the options that appear, select:\n<i>Upload a new file</i> – then send it to me'
                                ' – Then write'
                                ' (or better dictate) to me the word or text you want to find – and I will immediately'
                                ' send you all the lines containing the text you are looking for.',
                                'Наверное, у каждого человека бывали моменты, когда ему срочно нужно было найти '
                                'какую-нибудь информацию в своих файлах – а компьютера под рукой не было. К счастью, '
                                'сейчас не стоит беспокоиться об этом. Я легко вам с этим помогу:\n\n Для этого войдите'
                                ' в меню – нажмите <b>/searchdata</b>.  Далее, если вы ещё не присылали мне нужный файл'
                                ' – в '
                                'появившихся вариантах  выберите:\n<i>Загрузить новый файл</i> – затем отправьте'
                                ' мне его – '
                                'После чего напишите (или лучше продиктуйте)  мне слово или текст, который хотите '
                                'найти и я незамедлительно отправлю вам  все строки содержащие искомый текст.'][in_ru],
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=keyboard)

    elif callback_data["name"] == 'fill_pattern':
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_technologist:"))
        await bot.send_message(callback_data["id"],
                               ['It is not uncommon in our time there are situations when there is an urgent need to '
                                'fill out some document (make an application, issue a report...)'
                                '. However, having only a phone at hand, it is extremely inconvenient to do this'
                                ' manually, even if there is a ready-made template.\n I can help you with this:\n'
                                ' First of all, prepare the template in advance. To do this, write "/text" in the upper'
                                ' left cell of your table (as shown in the figures)',
                                'Не редко в наше время бывают ситуации, когда возникает необходимость  срочно заполнить'
                                ' какой-нибудь документ (сделать заявку, оформить отчёт, написать заявление... )  '
                                'Однако, имея под рукой только телефон, в ручную сделать это крайне не удобно даже при'
                                ' наличии готового шаблона.\n'
                                'Я могу вам с этим помочь:\n'
                                'В первую очередь заблаговременно подготовьте шаблон. Для этого в левой верхней ячейки'
                                ' вашей таблицы  пропишите "/text" (как показано на рисунки)'][in_ru])
        src = 'Data/Static/Helper/text.png'
        with open(src, 'rb') as png:
            await bot.send_photo(callback_data["id"], png)

        await bot.send_message(callback_data["id"],
                               ['In order to put a number in the document, write in the cells /number \n or, for'
                                ' example, /number=abc123 (if you want the numbering to start with abc123',
                                'Для того чтобы проставить номер в документ - пропишите в ячейки /number \n'
                                'или к примеру /number=авс123 (если хотите чтобы нумерация начиналась с авс123'][in_ru])

        await bot.send_message(callback_data["id"],
                               ['If you need to insert the current date, write /date',
                                'Кроме того, если вам необходимо вставить текущую дату - вы можете прописать'
                                ' /date'][in_ru])
        src = 'Data/Static/Helper/number_date.png'
        with open(src, 'rb') as png:
            await bot.send_photo(callback_data["id"], png)

        await bot.send_message(callback_data["id"],
                               ['Next, when you need to fill out your template, just go to the menu and select'
                                ' <b>/fillpattern</b> \n After which you will be asked to choose: use previously '
                                'downloaded templates or upload a new one. Just send me the text to insert by voice '
                                'or regular message and I will immediately send you the file with all the necessary '
                                'adjustments',
                                'Далее, когда вам потребуется заполнить ваш шаблон - просто зайдите в меню и выберите '
                                'там \n <b>/fillpattern</b> \nПосле чего вам будет предложено выбрать: использовать '
                                'ранее загруженные шаблоны или подгрузить новый. \n'
                                'Просто пришлите мне текст для вставки голосовым или обычным сообщением и я '
                                'незамедлительно вышлю вам файл со всеми необходимыми изменениями'][in_ru],
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=keyboard)

    elif callback_data["name"] == 'delete':
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_technologist:"))
        await bot.send_message(callback_data["id"], ['To delete a previously downloaded file, simply enter the menu'
                                                     ' and press \n<b>/delete</b>\n Then select the file you want'
                                                     ' to delete',
                                                     'Для того чтобы удалить ранее загруженный файл просто войдите в '
                                                     ' меню и нажмите \n<b>/delete</b> \n.'
                                                     'После чего выберите файл, который необходимо удалить'][in_ru],
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=keyboard)

    elif callback_data["name"] == 'contact':
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_technologist:"))
        await bot.send_message(callback_data["id"],
                               ['Already want to complain about me :)??',
                                'Уже задумали что-нибудь нажаловаться на меня ??\n\n'
                                'Признаться я от вас такого не ожидала :))'][in_ru],
                               parse_mode=types.ParseMode.HTML)
        await asyncio.sleep(5)
        await bot.send_message(callback_data["id"],
                               ['To send a message to the developers, just go to the menu and click \n'
                                '<b>/contact</b>\n',
                                'Для того чтобы отправить сообщение разработчикам - просто зайдите в меню и нажмите\n'
                                '<b>/contact</b>'][in_ru],
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=keyboard)

    elif callback_data["name"] == 'help':
        await bot.send_message(callback_data["id"], emoji.emojize(":woman_facepalming:"))
        await bot.send_message(callback_data["id"], ['To get instructions, simply enter the menu and press'
                                                     ' \n<b>/help</b>\n. ',
                                                     'Для того чтобы получить инструкции просто войдите в '
                                                     ' меню и нажмите\n <b>/help</b>. \n'
                                                     'После чего выберите интиресующий вас раздел'][in_ru],
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=keyboard)

    await call.answer()


def register_handlers_helper(dp: Dispatcher):
    dp.register_message_handler(help_start, commands=["help", "помощь"], state="*")
    dp.register_callback_query_handler(set_help,
                                       cb.filter(group=['help']),
                                       state=OrderHelp.waiting_for_chapter)
