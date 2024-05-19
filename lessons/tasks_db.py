import random
from django.db.models import QuerySet
from django.db.models import Q
from lessons.models import PhysTasks, PhysThemes


# globals
# phys_themes = ['Undefined', 'Механика', 'Термодинамика', 'Электричество', 'Оптика', 'Квантовая физика']
def get_phys_themes() -> list[str]:
    res = []
    for theme_entry in PhysThemes.objects.all():
        if theme_entry.theme != "Undefined":
            # Undefined - имя для всех неопределенных тем, их добавление должно быть исключено
            res.append(theme_entry.theme)
    return res


def get_phys_themes_numerical() -> list[[int, str]]:
    res = []
    for idx, theme in enumerate(get_phys_themes()):
        res.append((idx, theme))
    return res


def default_vals() -> dict:
    return PhysTasks.default_values


def check_answer(task: PhysTasks, user_answer: str) -> bool:
    return task.check_answer(user_answer)


def get_tasks_for_table() -> list:
    tasks_lst = []
    for item in PhysTasks.objects.all():
        if len(item.description) > 100:
            short_description = item.description[:100]+'...'
        else:
            short_description = item.description
        if item.complexity:
            cmplx = item.complexity
        else:
            cmplx = '-'
        tasks_lst.append([item.task_id, item.name, short_description, item.theme.theme, cmplx])
    return tasks_lst


def write_task(name: str, description: str, answer: str, author: str = "", image: str = "",
               theme: str = default_vals()["theme"], answer_type: str = default_vals()["answer_type"],
               complexity: int = default_vals()["cmplx"], trust: bool = default_vals()["trust"],
               source: str = "user") -> None:
    task = PhysTasks(name=name, description=description, theme=theme, complexity=complexity, image=image,
                     answer=answer, answer_type=answer_type, author=author, trust=trust, source=source)
    task.save()


def get_tasks_stats() -> dict:
    tasks = PhysTasks.objects.all()
    db_tasks = len(tasks.filter(source='db'))
    user_tasks = len(tasks.filter(source='user'))
    descr_len = [len(task.description) for task in tasks]
    themes_cnt = {theme: 0 for theme in get_phys_themes()}
    themes_cnt['не определено'] = 0
    # cmplx_cnt = dict()
    for task in tasks:
        if task.theme.theme in set(get_phys_themes())-{"Undefined"}:
            themes_cnt[task.theme.theme] += 1
        else:
            themes_cnt['не определено'] += 1
    themes_cnt_lst = [(key, val) for key, val in themes_cnt.items() if key != "Undefined"]
    stats = {
        "tasks_all": db_tasks + user_tasks,
        "tasks_own": db_tasks,
        "tasks_added": user_tasks,
        "words_avg": sum(descr_len) / len(descr_len),
        "words_max": max(descr_len),
        "words_min": min(descr_len),
        "themes_cnt_lst": themes_cnt_lst
    }
    return stats


def get_task_by_id(task_id: int) -> PhysTasks:
    return PhysTasks.objects.get(task_id=task_id)


def get_random_task() -> dict:
    trusted_tasks_count = PhysTasks.objects.filter(trust=True).count()
    random.seed()
    rand_int = random.randint(1, trusted_tasks_count)
    random_task = get_task_by_id(rand_int)
    res = {'task_id': random_task.task_id, 'name': random_task.name, 'description': random_task.description,
           'image': random_task.image, 'theme': random_task.theme.theme, 'complexity': random_task.complexity}
    return res


def get_tasks_by_filter(filtering: dict) -> list[dict]:
    tasks = PhysTasks.objects.filter(**filtering)
    return []
