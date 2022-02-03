import emoji
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from with_file import start_registration, get_list_ru


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    list_ru = get_list_ru()
    start_registration(message)
    in_ru = str(message.from_user.id) in list_ru
    await message.answer(['Hi.\n I am your new mobile assistant',
                          'Привет, Я ваш новый мобильнай ассистент!!!'][in_ru])
    await message.answer(emoji.emojize(":woman_raising_hand:"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru], ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    await message.answer(['Nowadays, the one who is always more successful is the one who quickly navigates the'
                          ' ever-increasing flow of information \n\n I am Asya !! and I am completely\n<b>free</b>'
                          ' and \n<b> without</b> <b>registration</b>\n of our relationship will help you navigate'
                          ' your Word documents\n\n To start, click /menu',
                          'В наше время более успешным всегда оказывается тот кто быстрее оринтируется во всё '
                          'нарастающем потоке информации.\n\nЯ Ася !! и я совершенно\n<b>бесплатно</b> и \n'
                          '<b>без регистрации</b> \nнаших отношений помогу вам легко и быстро ориентироваться в ваших'
                          ' Excel и CSV документах\n\n'
                          ' Для того чтобы начать нажмите \n<i>/меню</i>'][in_ru],
                         parse_mode=types.ParseMode.HTML,
                         reply_markup=keyboard)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    await message.answer(["Action canceled", "Действие отменено"][in_ru], reply_markup=types.ReplyKeyboardRemove())
    start_registration(message)
    await message.answer(emoji.emojize(":woman_frowning:"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [["/menu", "/меню"][in_ru], ["/help", "/помощь"][in_ru]]
    keyboard.add(*buttons)
    await message.answer('..',
                         reply_markup=keyboard)


async def cmd_menu(message: types.Message):
    list_ru = get_list_ru()
    in_ru = str(message.from_user.id) in list_ru
    print('in_ru= ', in_ru)
    if in_ru:
        await message.answer(f"<b>/searchdata</b>  {emoji.emojize(':magnifying_glass_tilted_left:')}"
                             f"  <i>Поиск данных в файле</i>\n\n"
                             f"<b>/fillpattern</b>  {emoji.emojize(':memo:')} <i>Записать данные в файл</i>\n\n"
                             f"<b>/language</b>    {emoji.emojize(':tongue:')} <i>Изменить язык</i>\n\n"
                             f"<b>/delete</b>       {emoji.emojize(':wastebasket:')} <i>Удалить файл</i>\n\n"
                             f"<b>/cancel</b>       {emoji.emojize(':chequered_flag:')}  <i>Рестарт бота</i>\n\n"
                             f"<b>/help</b>         {emoji.emojize(':bookmark_tabs:')}  <i>Получить инструкции</i>\n\n"
                             f"<b>/contact</b>   {emoji.emojize(':envelope:')} <i>Связаться с разработчиками</i>\n\n",
                             parse_mode=types.ParseMode.HTML)
    else:
        await message.answer(f"<b>/searchdata</b>  {emoji.emojize(':magnifying_glass_tilted_left:')}"
                             f" <i>Searching for data in a file</i>\n\n"
                             f"<b>/fillpattern</b>  {emoji.emojize(':memo:')} <i>Write data to a file</i>\n\n"
                             f"<b>/language</b>   {emoji.emojize(':tongue:')} <i>Change the language</i>\n\n"
                             f"<b>/delete</b>       {emoji.emojize(':wastebasket:')} <i>Delete a file</i>\n\n"
                             f"<b>/cancel</b>       {emoji.emojize(':chequered_flag:')}  <i>Restart the bot</i>\n\n"
                             f"<b>/help</b>            {emoji.emojize(':bookmark_tabs:')} <i>Get instructions</i>\n\n"
                             f"<b>/contact</b>   {emoji.emojize(':envelope:')} <i>Contact the developers</i>\n\n",
                             parse_mode=types.ParseMode.HTML)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(cmd_menu, commands=['menu', "меню"], state="*")
