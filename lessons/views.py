from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
# from . import tasks_work
from . import tasks_db
from .tasks_db import get_phys_themes, default_vals


def index(request):
    """
    Главная страница
    """
    return render(request, "index.html")


def tasks_list(request):
    """
    Список всех задач
    """
    tasks_lst = tasks_db.get_tasks_for_table()
    return render(request, "tasks_list.html", context={"tasks_lst": tasks_lst})


def add_task(request):
    """
    Страница с формой добавления задачи
    """
    phys_themes_str = ", ".join(get_phys_themes())
    return render(request, "task_add.html", context={"theme_examples": phys_themes_str})


def send_task(request):
    """
    Страницы с результатом добавления задачи. Задача запишется в БД и пользователь увидит сообщение об успехе,
    иначе пользователь увидит сообщение об ошибке и причину.
    """
    if request.method == "POST":
        cache.clear()
        user_name = request.POST.get("name")
        user_email = request.POST.get("email")
        # task data
        new_task = request.POST.get("new_task", "")  # required, name, not blank
        new_description = request.POST.get("new_description", "")  # required not blank
        new_theme = request.POST.get("new_theme")  # check not blank and not "Undefined"
        new_cmplx = request.POST.get("new_cmplx", default_vals()["cmplx"])  # has default
        new_image = request.POST.get("new_image", "")  # can be NULL if blank
        new_answer = request.POST.get("new_answer", "")  # required not blank
        # New_answer_type # all be "str" for default
        new_author = request.POST.get("new_author", "")  # can be NULL if blank
        new_trust = False  # all user added are not trusted

        context = {"user": user_name, "email": user_email}
        if len(new_description) == 0:
            context["success"] = False
            context["comment"] = "Описание задачи не может быть пустым"
        elif len(new_task) == 0:
            context["success"] = False
            context["comment"] = "Имя задачи не должно быть пустым"
        elif len(new_answer) == 0:
            context["success"] = False
            context["comment"] = "Ответ на задачу должен быть задан"
        elif new_theme not in set(get_phys_themes()):
            context["success"] = False
            context["comment"] = "Тема задачи должна быть одной из списка: " + ", ".join(get_phys_themes())
        else:
            written = tasks_db.db_write_task(name=new_task, description=new_description,
                                             answer=new_answer, author=new_author,
                                             image=new_image, theme=new_theme,
                                             complexity=new_cmplx, trust=new_trust,
                                             source="user")
            context["success"] = written
            if written:
                context["comment"] = "Ваша задача принята"
            else:
                context["comment"] = "Эта задача уже есть в базе данных"
        return render(request, "task_request.html", context=context)
    else:
        return HttpResponseRedirect("/add-task")


def show_content_stats(request):
    """
    Статистика по задачам в БД
    """
    stats = tasks_db.get_tasks_stats()
    return render(request, "content_stats.html", context=stats)


# def show_task(request)


def lesson_random(request):
    """
    Пользователю показывается случайная задача, на этой же странице происходит обработка ответа и результат.
    При обновлении страницы задача остается той же
    """
    context = {"show_conclusion": False}
    if request.session.get("task_given", False) and "task_data" in request.session:
        task_id = request.session["task_id"]
        # current_task = tasks_db.get_task_by_id()
        context.update(request.session["task_data"])
        user_answer = request.GET.get("user_answer", "")
        if user_answer != "":
            # Пользователь ввел ответ
            context["show_conclusion"] = True
            check_res = tasks_db.check_answers({task_id: user_answer})[task_id]
            if check_res:
                del request.session["task_id"]
                del request.session["task_given"]
                context["success"] = True
                context["comment"] = "Можете перезагрузить страницу чтобы получить новую задачу"
            else:
                context["success"] = False
                context["comment"] = "Попробуйте ещё раз, или нажмите на кнопку для получения новой задачи"
        else:
            # Пользователь не вводил ответ, но все ещё та же задача (перезагрузка страницы)
            context["show_conclusion"] = False
    else:
        _buf = tasks_db.get_random_task()
        context.update(_buf)
        request.session["task_id"] = context["task_id"]
        request.session["task_given"] = True
        request.session["task_data"] = _buf

    return render(request, "lesson_random.html", context=context)


def lesson_random_reset(request):
    """
    Функция для смены случайной задачи на новую
    """
    context = {"show_conclusion": False}
    _buf = tasks_db.get_random_task()
    context.update(_buf)
    request.session["task_id"] = context["task_id"]
    request.session["task_given"] = True
    request.session["task_data"] = _buf
    return render(request, "lesson_random.html", context=context)


def lesson_settings(request, retry: bool = False, comment: str = ""):
    """
    Страница с формой настроек критериев урока.
    Урок - список случайно выбранных из базы данных задач по заданным критериям.
    """
    context = {"idx_themes": tasks_db.get_phys_themes(with_idx=True)}
    return render(request, "lesson_settings.html", context=context)


def lesson_main(request):
    """
    Страница с показом списка задач и формой ввода ответа.
    Должна вызваться только после lesson_settings, в противном случае предложит перейти на страницу настроек
    """
    context = {}
    if request.method == "POST":
        cache.clear()
        idx_themes = tasks_db.get_phys_themes(with_idx=True)
        themes_selected = []
        for idx, theme in idx_themes:
            if f"theme_{idx}" in request.POST.keys():
                themes_selected.append(theme)
        if len(themes_selected) == 0:
            context["comment"] = "Выберете хотя бы одну тему в списке настроек"
            context["success"] = False
            return render(request, "lesson_main.html", context=context)
        # options:
        # 0 : N for each theme
        # 1 : N as whole quantity
        option = int(request.POST.get("options", 0))
        quantity = int(request.POST.get("quantity"))
        flag, res, comment = tasks_db.get_tasks_lesson(themes_selected, option, quantity)
        context["comment"] = comment
        context["success"] = flag
        if not flag:
            return render(request, "lesson_main.html", context=context)
        id_lst = [entry["task_id"] for entry in res]
        tasks_data = [(entry["task_id"], entry["name"], entry["description"], entry["image"], entry["theme"],
                       entry["complexity"]) for entry in res]
        request.session["id_lst"] = id_lst
        context["tasks_data"] = tasks_data
        return render(request, "lesson_main.html", context=context)
    else:
        context["comment"] = "Похоже, что Вы не заполнили форму на странице настроек."
        context["success"] = False
        return render(request, "lesson_main.html", context=context)


def lesson_check_answers(request):
    """
    Страница, показывающая список задач из урока, ответ пользователя и вердикт проверки
    Должна вызваться только после lesson_main, в противном случае предложит перейти на страницу настроек или домой
    """
    context = {"success": True}
    if request.method == "POST":
        try:
            # А вдруг данные сессии пропадут?
            id_lst = request.session["id_lst"]
        except KeyError:
            context["success"] = False
            context["comment_no_task"] = "Не найдены ключи."
            return render(request, "lesson_check.html", context=context)
        user_answers = {idx: request.POST.get(f"user_answer_{idx}", "") for idx in id_lst}
        check_res = tasks_db.check_answers(user_answers)
        tasks = tasks_db.get_tasks_filter({"task_id__in": id_lst})
        all_right = True
        check_comment = {}
        right_cnt = 0
        for idx, check_bool in check_res.items():
            all_right = all_right and check_bool
            if check_bool:
                right_cnt += 1
                check_comment[idx] = "Правильно!"
            else:
                check_comment[idx] = "Неверно."
        context["all_right"] = all_right
        if all_right:
            context["comment_all_right"] = "Поздравляем! Все решено верно!"
        else:
            context["comment_all_right"] = "Некоторые из ваших ответов неверны."
        # составим список кортежей для отображения, содержащих:
        # idx, user_answer, check_comment, name, description, image, theme, cmplx
        task_data_d = {task["task_id"]: (task["name"], task["description"], task["image"],
                                         task["theme_id"], task["complexity"]) for task in tasks}
        result = [(idx, user_answers[idx], check_comment[idx], task_data_d[idx][0], task_data_d[idx][1],
                   task_data_d[idx][2], task_data_d[idx][3], task_data_d[idx][4],) for idx in id_lst]
        table_result = [(i + 1, check_res[result[i][0]], result[i][1], result[i][2], result[i][3])
                        for i in range(len(result))]
        context["result"] = result
        context["table_result"] = table_result
        context["success"] = True
        context["all_count"] = len(id_lst)
        context["right_cnt"] = right_cnt
        context["right_percent"] = int(right_cnt*100.0/len(id_lst))
    else:
        context["success"] = False
        context["comment_no_task"] = "Сначал решите задачи."
    return render(request, "lesson_check.html", context=context)
