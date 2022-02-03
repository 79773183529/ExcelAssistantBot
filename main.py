import asyncio
import logging

import emoji
from aiogram import Bot
from aiogram.types import BotCommand

from common import register_handlers_common
from contact import register_handlers_contact
from food import register_handlers_food
from search_data import register_handlers_search
from delete_file import register_handlers_delete
from fill_pattern import register_handlers_fill
from language import register_handlers_language
from helper import register_handlers_helper

from bot import bot, dp
logging.basicConfig(level=logging.INFO)


async def main():
    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_food(dp)
    register_handlers_language(dp)
    register_handlers_search(dp)
    register_handlers_delete(dp)
    register_handlers_fill(dp)
    register_handlers_helper(dp)
    register_handlers_contact(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/language", description=f"{emoji.emojize(':tongue:')}Change the language"),
        BotCommand(command="/fillpattern", description=f"{emoji.emojize(':memo:')} Fill in the template"),
        BotCommand(command="/searchdata", description=f"{emoji.emojize(':magnifying_glass_tilted_left:')} Searching"
                                                      f" for data"),
        BotCommand(command="/delete", description=f"{emoji.emojize(':wastebasket:')}Delete a file"),
        BotCommand(command="/cancel", description=f"{emoji.emojize(':chequered_flag:')} Cancel the current action")
                ]
    await bot.set_my_commands(commands)


if __name__ == '__main__':
    asyncio.run(main())

