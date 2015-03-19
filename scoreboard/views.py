# encoding: UTF-8
from collections import defaultdict
import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseNotFound, HttpResponse



# registration view
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from scoreboard.models import News, Task, SolvedTasks, Category
def index(request):
    if request.method == "GET":
        return TemplateResponse(request, "index.html")
    else:
        return HttpResponseNotFound

@never_cache
@login_required
def tasks(request):
    pivot = defaultdict(list)
    team = request.user
    for result in Task.objects.values('category', 'score', 'is_enabled', 'pk').order_by('category', 'score'):
        pivot[Category.objects.get(pk=result['category'])].append(
            {"score": result["score"], "is_enabled": result["is_enabled"], "pk": result["pk"],
             "is_solved": SolvedTasks.objects.filter(team=team, task=Task.objects.get(pk=result["pk"])).exists()})
    return TemplateResponse(request, "tasks_main.html", {"tasks": dict(pivot)})


@never_cache
@login_required
def task_detail(request, task_pk):
    try:
        task = Task.objects.get(pk=task_pk)
        is_solved = SolvedTasks.objects.filter(task=task, team=request.user).exists()
        return TemplateResponse(request, "tasks_detail.html", {"task": task, "is_solved": is_solved})
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