from create import dp
from aiogram import types
from commands.general_func import print_task, navigation
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from commands.url_requests import read_problems, read_teams, read_scoreboard
from keyboards import tasks_navigation, menu_keyboard, level_ikb, menu_inline_b, tn_b2, menu_ikb

globalDict_level = dict()
globalDict_move = dict()
globalDict_task = dict()


def get_unsolved_tasks(callback_data, u_id):
    """
    Функция для получения не решенных пользователем задач
    Args:
        callback_data: Данные нажатия кнопки
        u_id: Идентификатор пользователя

    Returns: Массив, который включает сообщение, меню, пустой список задач, если возникла ошибка.
             Иначе возвращается только список нерешенных задач.
    """

    tasks = []
    problems = read_problems()
    scoreboard = read_scoreboard()
    if not problems or not scoreboard:
        return ['Ошибка при отправке запроса.', menu_ikb, tasks]

    if 'task' not in callback_data:
        globalDict_level[u_id] = callback_data
    all_tasks = [t for t in problems if globalDict_level[u_id] in t.get("label")]
    if not all_tasks:
        return ['В данный момент задач нет.\nЗагляните позже.', menu_keyboard, tasks]

    team_info = None
    table = scoreboard.get("rows")
    for t in read_teams():
        if "_" in t.get("name") and u_id == t.get("name").split("_")[1]:
            team_info = t

    u_info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
    solved_tasks_ids = [p.get("problem_id") for p in u_info.get("problems") if p.get("solved")]
    tasks = [t for t in all_tasks if t.get("id") not in solved_tasks_ids]

    if not tasks:
        return ['Вы решили все задачи данного уровня!', menu_keyboard, tasks]

    return [tasks]


@dp.callback_query_handler(text='tasks')
async def get_lvl(callback: types.CallbackQuery):
    """
    Функция выбора сложности задач.
    """
    await callback.message.edit_text("Выберите уровень сложности.", reply_markup=level_ikb)
    globalDict_move[str(callback.from_user.id)] = 0


@dp.callback_query_handler(text=['A', 'B', 'C', 'left_task', 'right_task'])
async def show_tasks(callback: types.CallbackQuery):
    """
    Функция просмотра доступных задач.
    """
    usr_id = str(callback.from_user.id)
    if usr_id not in globalDict_move:
        globalDict_move[usr_id] = 0

    tasks_lst = get_unsolved_tasks(callback.data, usr_id)
    if not tasks_lst[-1]:
        await callback.message.edit_text(tasks_lst[0], reply_markup=tasks_lst[1])
        await callback.answer()
    else:
        if 'task' not in callback.data:
            globalDict_level[usr_id] = callback.data

        tasks = tasks_lst[-1]
        if usr_id not in globalDict_task or callback.data in ('A', 'B', 'C'):
            globalDict_task[usr_id] = tasks[0].get('id')

        count_tasks = len(tasks)

        if callback.data == globalDict_level[usr_id]:
            p = globalDict_move[usr_id]
            if globalDict_move[usr_id] <= -1:
                p = count_tasks + globalDict_move[usr_id]

            s = f"<b>№</b> {p + 1}/{count_tasks}\n\n"
            await callback.message.edit_text(s + print_task(tasks[globalDict_move[usr_id]]), parse_mode='HTML',
                                             reply_markup=tasks_navigation,
                                             disable_web_page_preview=True)

        elif callback.data in ('left_task', 'right_task'):
            s, globalDict_move[usr_id] = navigation(callback.data, globalDict_move[usr_id], count_tasks)
            globalDict_task[usr_id] = tasks[globalDict_move[usr_id]].get('id')

            await callback.message.edit_text(s + print_task(tasks[globalDict_move[usr_id]]),
                                             parse_mode='HTML',
                                             reply_markup=tasks_navigation,
                                             disable_web_page_preview=True)


@dp.callback_query_handler(text="more_task")
async def show_more_task(callback: types.CallbackQuery):
    """
    Функция для подробного просмотра данных задачи.
    """
    usr_id = str(callback.from_user.id)
    tasks_lst = get_unsolved_tasks(callback.data, usr_id)
    if not tasks_lst[-1]:
        await callback.message.edit_text(tasks_lst[0], reply_markup=tasks_lst[1])
        await callback.answer()

    # Клавиатура при подробном просмотре задачи
    tasks_more_navigation = InlineKeyboardMarkup()
    tmn_b1 = InlineKeyboardButton(text="Вернуться к просмотру", callback_data=globalDict_level[usr_id])
    tasks_more_navigation.add(tmn_b1).add(tn_b2).add(menu_inline_b)

    tasks = tasks_lst[-1]
    text_task = print_task(tasks[globalDict_move[usr_id]], 1)
    await callback.message.edit_text(text_task, parse_mode='HTML', reply_markup=tasks_more_navigation,
                                     disable_web_page_preview=True)
