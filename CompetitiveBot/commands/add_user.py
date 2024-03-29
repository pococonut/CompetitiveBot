import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from create import dp
from config import settings, admin_authorization
from keyboards import menu_keyboard, registration_ikb
from commands.menu import global_Dict_del_msg
from commands.general_func import write_user_values
from commands.url_requests import read_teams, send_user, send_team


class User(StatesGroup):
    name = State()


def make_name_capital_letters(user_name):
    """
    Функция для привидения первых букв в ФИО к верхнему регистру
    Args:
        user_name: ФИО пользователя

    Returns: ФИО в правильном формате
    """

    return " ".join([w.capitalize() for w in user_name.split()])


def get_uid_from_team_name(team):
    """
    Функция возвращает идентификатор пользователя в
    телеграм, который содержится в названии команды
    Args:
        team: Команда

    Returns: Идентификатор пользователя телеграм, соответствующий команде
    """

    return team.get("name").split("_")[-1]


def get_user_team_id(user_id):
    """
    Функция возвращает идентификатор команды, который
    соответствует идентификатору пользователя в телеграм
    Args:
        user_id: Идентификатор пользователя в телеграм

    Returns: Идентификатор команды, если он был найден, иначе None
    """

    for team in read_teams():
        if user_id == get_uid_from_team_name(team):
            return team.get("id")


def make_team_data(team_name, user_id):
    """
    Функция для создания словаря с данными новой команды
    Args:
        team_name: Имя пользователя
        user_id: Идентификатор пользователя в телеграм

    Returns: Словарь с данными новой команды
    """

    unic_team_name = team_name + "_" + user_id

    if not read_teams():
        new_team_id = "3"
    else:
        new_team_id = str(int(read_teams()[-1].get("id")) + 1)

    return {"display_name": team_name,
            "name": unic_team_name,
            "id": new_team_id,
            "group_ids": ["3"]}


def make_user_data(user_name, user_id, team_id):
    """
    Функция для создания словаря с данными нового пользователя
    Args:
        user_name: Имя пользователя
        user_id: Идентификатор пользователя в телеграм
        team_id: Идентификатор команды

    Returns: Словарь с данными нового пользователя
    """

    unic_user_name = user_name + "_" + user_id

    return {'username': unic_user_name,
            'name': user_name,
            'password': f"user_{user_id}",
            'enabled': True,
            "team_id": team_id,
            'roles': ['team']}


def check_user_already_exist(user_id):
    """
    Функция для проверки наличия пользователя в БД
    Args:
        user_id: Идентификатор пользователя в телеграм

    Returns: True - пользователь уже зарегистрирован,
             False - пользователь не зарегистрирован
    """

    try:
        for team in read_teams():
            if user_id in team.get("name"):
                return True
    except Exception as e:
        logging.warning(e)
        return False


def check_user_name(name):
    """
    Функция для валидации ФИО
    Args:
        name: ФИО пользователя

    Returns: True - ФИО корректно, False - ФИО некорректно
    """

    if len(name) > 60:
        return False

    if len(name.split()) != 3:
        return False

    no_numbers = name.replace(" ", "").replace("-", "").isalpha()
    if not no_numbers:
        return False

    return True


def user_registration(name, user_id):
    """
    Функция для регистрации пользователя в системе
    Args:
        name: Имя пользователя
        user_id: Идентификатор пользователя в телеграм

    Returns: Сообщение, клавиатура
    """

    session = admin_authorization(settings.admin_username, settings.admin_password)

    new_team_data = make_team_data(name, user_id)
    team_has_been_added = send_team(session, new_team_data)
    if not team_has_been_added:
        return "Ошибка сервера.", registration_ikb

    team_id = get_user_team_id(user_id)
    if not team_id:
        return "Ошибка сервера.", registration_ikb

    new_user_data = make_user_data(name, user_id, team_id)
    user_has_been_added = send_user(session, new_user_data)
    if not user_has_been_added:
        return "Ошибка сервера.", registration_ikb

    return "Вы были успешно зарегистрированы.", menu_keyboard


@dp.callback_query(F.data == "registration")
async def reg_user(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция регистрации пользователя
    """

    usr_id = str(callback.from_user.id)
    already_exist = check_user_already_exist(usr_id)

    if already_exist:
        await callback.message.edit_text("Вы уже зарегистрированы.",  reply_markup=menu_keyboard)
        return
    await callback.message.edit_text("Отправьте ФИО в формате Иванов Иван Иванович.")
    await state.set_state(User.name)


@dp.message(User.name)
async def get_user_name(message: types.Message, state: FSMContext):
    """
    Функция для получения имени пользователя и занесения пользователя в БД
    """

    user_message = message.text
    name_is_correct = check_user_name(user_message)

    if not name_is_correct:
        await message.answer("ФИО введено в некорректном формате, повторите ввод.")
        return

    name = make_name_capital_letters(user_message)
    await state.update_data(name=name)
    data = await state.get_data()
    await state.clear()

    usr_id = str(message.from_user.id)
    text, keyboard = user_registration(data['name'], usr_id)
    sent_msg = await message.answer(text, reply_markup=keyboard)
    global_Dict_del_msg[usr_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)
