from collections import defaultdict
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseNotFound, HttpResponse, HttpResponseRedirect


# registration view
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from schoolctf.forms import RegistrationForm
from scoreboard.models import News, Task, SolvedTasks, Category


def index(request):
    if request.method == "GET":
        return TemplateResponse(request, "index.html")
    else:
        return HttpResponseNotFound


@csrf_protect
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("scoreboard.views.index")
            else:
                messages.add_message(request, messages.ERROR, 'Неверное имя пользователя или пароль')
                return redirect("scoreboard.views.index")

        else:
            messages.add_message(request, messages.ERROR, 'Неверное имя пользователя или пароль')
            return redirect("scoreboard.views.index")
    else:
        messages.add_message(request, messages.ERROR, 'Пожалуйста войдите в систему')
        return redirect("scoreboard.views.index")

@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


@never_cache
@login_required
def tasks(request):
    pivot = defaultdict(list)
    for result in Task.objects.values('category', 'score', 'is_enabled', 'pk').order_by('category', 'score'):
        pivot[Category.objects.get(pk=result['category'])].append(
            {"score": result["score"], "is_enabled": result["is_enabled"], "pk": result["pk"],
             "is_solved": False})
    return TemplateResponse(request, "tasks_main.html", {"tasks": dict(pivot)})


@never_cache
@login_required
def task_detail(request, task_pk):
    try:
        task = Task.objects.get(pk=task_pk)
        return TemplateResponse(request, "tasks_detail.html", {"task": task, "is_solved": False})
    except Task.DoesNotExist:
        return HttpResponseNotFound("Not found")


@csrf_protect
@login_required
@never_cache
def task_solve(request, task_pk):
    response_data = {}
    if request.method == "POST":
        try:
            task = Task.objects.get(pk=task_pk)
            flag = request.POST["flag"]
            if flag.strip() == task.flag:
                solve = SolvedTasks(team=request.user, task=task)
                try:
                    solve.save()
                    response_data["result"] = "success"
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                except ValidationError:
                    response_data["result"] = "failed"
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data["result"] = "failed"
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Task.DoesNotExist:
            return HttpResponseNotFound("Task not found")

    else:
        return HttpResponseNotFound("Not Found")


def detail_news(request, pk):
    return TemplateResponse(request, "article.html", context={"article": News.objects.get(pk=pk), "news_pk": pk})


@sensitive_post_parameters()
@csrf_protect
@never_cache
def registration(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return TemplateResponse(request, "registration/registration_success.html")
    else:
        context = {
            'form': RegistrationForm(),
        }
    return TemplateResponse(request, "registration/reg_form.html", context)
