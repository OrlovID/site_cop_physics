import random
from typing import List, Tuple, Dict
from django.db.models import QuerySet
from django.db.models.query import EmptyQuerySet
from django.db.models import Q
from lessons.models import PhysTasks, PhysThemes


# globals
# phys_themes = ["Undefined", "Механика", "Термодинамика", "Электричество", "Оптика", "Квантовая физика"]
def get_phys_themes(with_idx=False) -> List[str] | List[Tuple[int, str]]:
    """
    Получение названий разделов физики без или вместе с индексами
    """
    res = []
    for theme_entry in PhysThemes.objects.all():
        if theme_entry.theme != "Undefined":
            # Undefined - имя для всех неопределенных тем, их добавление должно быть исключено
            res.append((theme_entry.id, theme_entry.theme))
    if not with_idx:
        res = [tup[1] for tup in res]
    return res


def default_vals() -> Dict:
    """
    Функция получения значений по умолчанию
    """
    return PhysTasks.default_values


def check_answers(user_answers: Dict[int, str]) -> Dict[int, bool]:
    """
    Возвращает результат проверки списка задач по переданным первичным ключам задач и словарю ответов пользователя.
    Возвращает словарь {'первичные ключи задач' : boolean результаты проверки (True == верный ответ)}.
    """
    task_id_lst = user_answers.keys()
    tasks = PhysTasks.objects.filter(task_id__in=task_id_lst)
    return {task.task_id: task.check_answer(user_answers[task.task_id]) for task in tasks}


def get_tasks_for_table() -> List:
    """
    Получение необходимых элементов для отображения таблицы задач
    Описание краткое <=100 символов; ключи скрыты так как сортировка по имени, теме.
    """
    tasks_lst = []
    for idx, item in enumerate(PhysTasks.objects.all()):
        if len(item.description) > 100:
            short_description = item.description[:100] + "..."
        else:
            short_description = item.description
        if item.complexity:
            cmplx = item.complexity
        else:
            cmplx = "-"
        tasks_lst.append([idx + 1, item.name, short_description, item.theme.theme, cmplx])
    return tasks_lst


def db_write_task(name: str, description: str, answer: str, author: str = "", image: str = "",
                  theme: str = default_vals()["theme"], answer_type: str = default_vals()["answer_type"],
                  complexity: int = default_vals()["cmplx"], trust: bool = default_vals()["trust"],
                  source: str = "user") -> bool:
    """
    Запись задачи в БД если записи нет и возвращает True. Если задача уже есть в БД, то возвращает False
    """
    theme_entry, _ = PhysThemes.objects.get_or_create(theme=theme)
    args = {"name": name,
            "description": description,
            "theme": theme_entry,
            "complexity": complexity,
            "image": image,
            "answer": answer,
            "answer_type": answer_type,
            "author": author,
            "trust": trust,
            "source": source}
    _, flag = PhysTasks.objects.get_or_create(**args)
    return flag


def get_tasks_stats() -> Dict:
    """
    Получение статистики
    """
    tasks = PhysTasks.objects.all()
    db_tasks = len(tasks.filter(source="db"))
    user_tasks = len(tasks.filter(source="user"))
    descr_len = [len(task.description) for task in tasks]
    themes_cnt = {theme: 0 for theme in get_phys_themes()}
    themes_cnt["не определено"] = 0
    # cmplx_cnt = dict()
    for task in tasks:
        if task.theme.theme in set(get_phys_themes()) - {"Undefined"}:
            themes_cnt[task.theme.theme] += 1
        else:
            themes_cnt["не определено"] += 1
    themes_cnt_lst = [(key, val) for key, val in themes_cnt.items() if key != "Undefined"]
    stats = {
        "tasks_all": db_tasks + user_tasks,
        "tasks_own": db_tasks,
        "tasks_added": user_tasks,
        "words_avg": int(sum(descr_len) / len(descr_len)),
        "words_max": max(descr_len),
        "words_min": min(descr_len),
        "themes_cnt_lst": themes_cnt_lst
    }
    return stats


def get_task_by_id(task_id: int) -> PhysTasks:
    """
    Получение задачи из БД по первичному ключу
    """
    return PhysTasks.objects.get(task_id=task_id)


def get_random_task(trust=True) -> Dict:
    """
    Получение одной случайной задачи
    """
    trusted_tasks_count = PhysTasks.objects.filter(trust=trust).count()
    random.seed()
    rand_int = random.randint(1, trusted_tasks_count)
    random_task = get_task_by_id(rand_int)
    res = {"task_id": random_task.task_id, "name": random_task.name, "description": random_task.description,
           "image": random_task.image, "theme": random_task.theme.theme, "complexity": random_task.complexity}
    return res


def get_random_tasks_filter(filtering: Dict, quantity=1) -> List:
    """
    Получает по заданному фильтру (критерию) filtering задачи из БД.
    Среди них случайным образом выбирает задачи в количестве = 'quantity'.
    Если значение 'quantity' больше количества полученных по фильтру задач,
    то возвращает все задачи по фильтру, перемешанные в случайном порядке
    """
    random.seed()
    tasks = PhysTasks.objects.filter(**filtering)
    task_id_all = tasks.values_list("task_id")
    id_lst = [x[0] for x in task_id_all]
    count = len(id_lst)
    qx = min(quantity, count)
    idxlst = sorted(random.sample(id_lst, qx))
    res = list(tasks.filter(task_id__in=idxlst))
    return res


def get_tasks_filter(filtering: Dict) -> List[Dict]:
    """
    Получает по заданному фильтру (критерию) filtering задачи из БД в виде списка словарей (ключи == поля в БД)
    """
    tasks = PhysTasks.objects.filter(**filtering).values()
    res = list(tasks)
    return res


def get_tasks_lesson(selected_themes: List[str], option: int, quantity: int) -> Tuple[bool, List[Dict], str]:
    """
    Получает из БД задачи для урока, по темам 'selected_themes' с опцией 'option' и в количестве 'quantity'
        # options:
        # 0 : => 'quantity' - количество по каждой теме
        # 1 : => 'quantity' - общее количество
    """
    res = []
    resbuf = []
    if quantity <= 0:
        return False, [], "Введите положительное количество"
    if option == 0:
        for theme in selected_themes:
            buf = get_random_tasks_filter({"theme": theme}, quantity=quantity)
            resbuf.extend(buf)
    elif option == 1:
        resbuf = get_random_tasks_filter({"theme__in": selected_themes, "trust": True}, quantity=quantity)
    else:
        return False, [], "Выбранная опция не распознана"
    for task in resbuf:
        res.append({"task_id": task.task_id, "name": task.name, "description": task.description,
                    "image": task.image, "theme": task.theme.theme, "complexity": task.complexity})
    if res:
        comment = "Список сформирован"
        flag = True
    else:
        comment = "Похоже, по заданным критериям ничего не нашлось"
        flag = False
    return flag, res, comment
