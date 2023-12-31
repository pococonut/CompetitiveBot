def get_lvl_task(el):
    """
    Возвращает уровень задачи
    Args:
        el: Задача
    Returns: Уровень
    """

    levels = {"A": "Легкий",
              "B": "Средний",
              "C": "Сложный"}

    level = el.get('label')
    for k, v in levels.items():
        if k in el.get('label'):
            return v
    return level
