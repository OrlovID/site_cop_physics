from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
# from . import tasks_work
from . import tasks_db
from .tasks_db import get_phys_themes, default_vals


def index(request):
    return render(request, "index.html")


def tasks_list(request):
    tasks_lst = tasks_db.get_tasks_for_table()
    return render(request, "tasks_list.html", context={"tasks_lst": tasks_lst})


def add_task(request):
    phys_themes_str = ", ".join(get_phys_themes())
    return render(request, "task_add.html", context={"theme_examples": phys_themes_str})


def send_task(request):
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
            context["success"] = True
            context["comment"] = "Ваша задача принята"
            tasks_db.db_write_task(name=new_task, description=new_description, answer=new_answer, author=new_author,
                                   image=new_image, theme=new_theme, complexity=new_cmplx, trust=new_trust,
                                   source="user")
        if context["success"]:
            context["success-title"] = ""
        return render(request, "task_request.html", context=context)
    else:
        add_task(request)


def show_content_stats(request):
    stats = tasks_db.get_tasks_stats()
    return render(request, "content_stats.html", context=stats)


# def show_task(request)


def lesson_random(request):
    context = {"show_conclusion": False}
    if request.session.get("task_given", False) and "task_data" in request.session:
        task_id = request.session["task_id"]
        # current_task = tasks_db.get_task_by_id()
        context.update(request.session["task_data"])
        user_answer = request.GET.get("user_answer", "")
        if user_answer != "":
            # Пользователь ввел ответ
            context["show_conclusion"] = True
            check_res = tasks_db.check_answers([task_id,], [user_answer,])[task_id]
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
    context = {"show_conclusion": False}
    _buf = tasks_db.get_random_task()
    context.update(_buf)
    request.session["task_id"] = context["task_id"]
    request.session["task_given"] = True
    request.session["task_data"] = _buf
    return render(request, "lesson_random.html", context=context)


def lesson_settings(request, retry: bool = False, comment: str = ""):
    context = dict()
    """if len(comment) > 0 and retry:
        context["comment"] = comment
        context["retry"] = retry"""
    context["idx_themes"] = tasks_db.get_phys_themes_idx()
    # request.session["idx_themes"] = (context["idx_themes"]).copy()
    return render(request, "lesson_settings.html", context=context)


def lesson_main(request):
    context = dict()
    if request.method == "POST":
        cache.clear()
        idx_themes = tasks_db.get_phys_themes_idx()
        themes_selected = []
        for idx, theme in idx_themes:
            if f"theme_{idx}" in request.POST.keys():
                themes_selected.append(theme)
        if len(themes_selected) == 0:
            context["comment"] = "Выберете хотя бы одну тему в списке настроек"
            context["success"] = False
            # render page with retry option: href="lesson-settings"
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
    context = dict()
    if request.method == "POST":
        id_lst = request.session["id_lst"]
        user_answers = {idx: request.POST.get(f"user_answer_{idx}", "") for idx in id_lst}
        check_res = tasks_db.check_answers(id_lst, user_answers)
        all_right = True
        for check_bool in check_res:
            all_right = all_right and check_bool
        context["all_right"] = all_right
        context["result"] = tuple(check_res.items())

        return render(request, "lesson_checking.html", context=context)
    else:
        # return render(request, "lesson_checking.html", context=context)
        context["comment"] = "Нечего проверять!"
        context["retry"] = True
        return HttpResponse("Нечего проверять!")
