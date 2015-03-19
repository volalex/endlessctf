from django import template
from django.db.models import Sum

from scoreboard.models import News, SolvedTasks


__author__ = 'volal_000'

register = template.Library()


@register.inclusion_tag("includes/news.html")
def news_block(news_pk):
    try:
        news = News.objects.all().order_by('create_date').reverse()
    except News.DoesNotExist:
        news = []
    return {"news_list": news, "active_pk": news_pk}


@register.inclusion_tag("includes/results.html")
def results():
    # scoreboard = SolvedTasks.objects.extra(select={'team__team_name': 'team_name'}) \
    #     .filter(team__is_admin=False).values("team__team_name").annotate(
    #     sum=Sum('task__score')).order_by("-sum")
    # scoreboard = [(m['team__team_name'], m['sum']) for m in scoreboard]
    return {"results": []}
