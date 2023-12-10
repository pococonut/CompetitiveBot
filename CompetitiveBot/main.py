import logging
from aiogram.utils import executor
from commands.url_requests import read_teams
from create import dp
from aiogram import types
from commands import get_tasks, get_languages, submit_solution, get_result, get_scoreboard, add_user, get_user_info ,back
from keyboards import menu_keyboard, registration_ikb

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

commands = [types.BotCommand(command='/menu', description='Меню')]


async def set_commands(dp):
    await dp.bot.set_my_commands(commands=commands, scope=types.BotCommandScopeAllPrivateChats())


DESCRIPTION = """Телеграм бот предоставляет список доступных задач по программированию трех уровней сложности. Решения принимаются на нескольких доступных языках, благодаря чему, вы можете проверить свои навыки в каждом из них.\n
Также бот выводит рейтинговую таблицу, где вы можете увидеть свое место среди других пользователей. Это поможет вам отслеживать свой прогресс и стремиться к новым результатам.\n"""


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать!\n\n" + DESCRIPTION, reply_markup=registration_ikb)


@dp.message_handler(commands='menu')
async def menu_command(message: types.Message):
    already_exist = [True for t in read_teams() if str(message.from_user.id) in t.get("name")]
    if already_exist:
        await message.answer("Выберите команду.\n\n", reply_markup=menu_keyboard)
    else:
        await message.answer("Пройдите этап регистрации.", reply_markup=registration_ikb)


@dp.callback_query_handler(text=['menu_inline'])
async def menu_command_inline(callback: types.CallbackQuery):
    already_exist = [True for t in read_teams() if str(callback.from_user.id) in t.get("name")]
    if already_exist:
        await callback.message.edit_text("Выберите команду.\n\n", reply_markup=menu_keyboard)
    else:
        await callback.message.edit_text("Пройдите этап регистрации.", reply_markup=registration_ikb)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=set_commands, skip_updates=True)