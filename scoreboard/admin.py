from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.widgets import SummernoteWidget
from scoreboard.models import Task, Category, News, SolvedTasks


class NewsModelAdmin(SummernoteModelAdmin):
    list_display = ('title', 'create_date')
    fieldsets = (
        ("News article", {'fields': ('title', 'text')}),
    )
    ordering = ('create_date',)


admin.site.register(News, NewsModelAdmin)


class SolvedTasksModelAdmin(ModelAdmin):
    list_display = ('team', 'task', 'solved_at')
    fieldsets = (
        ("Solve", {'fields': ('team', 'task')}),
    )
    ordering = ('solved_at',)


admin.site.register(SolvedTasks, SolvedTasksModelAdmin)


class TaskModelAdmin(SummernoteModelAdmin):
    list_display = ('name', 'category', 'score')
    list_filter = ('category', 'score',)
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Task info', {'fields': ('category', 'score', 'flag', 'is_enabled')}),
        ('Task text', {'fields': ('text', 'task_file',)}),
    )
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ()


admin.site.register(Task, TaskModelAdmin)


class CategoryModelAdmin(ModelAdmin):
    list_display = ('title', 'position',)
    search_fields = ('title',)
    filter_horizontal = ()


admin.site.register(Category, CategoryModelAdmin)


# class TeamUserAdmin(UserAdmin):
#     # The forms to add and change user instances
#
#     # The fields to be used in displaying the User model.
#     # These override the definitions on the base UserAdmin
#     # that reference specific fields on auth.User.
#     list_display = ('team_name', 'is_admin', 'is_active')
#     list_filter = ('is_admin', 'is_active')
#     fieldsets = (
#         (None, {'fields': ('team_name', 'password')}),
#         ('Permissions', {'fields': ('is_admin', 'is_active',)}),
#     )
#     # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
#     # overrides get_fieldsets to use this attribute when creating a user.
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('team_name', 'password1', 'password2')}
#         ),
#     )
#     search_fields = ('team_name',)
#     ordering = ('team_name',)
#     filter_horizontal = ()
#
# # Now register the new UserAdmin...
# admin.site.register(Player, TeamUserAdmin)
# # ... and, since we're not using Django's built-in permissions,
# # unregister the Group model from admin.
# admin.site.unregister(Group)


class FlatPageCustomAdmin(FlatPageAdmin):
    formfield_overrides = {models.TextField: {'widget': SummernoteWidget}}


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustomAdmin)

