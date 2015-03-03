from django import forms
from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.widgets import SummernoteWidget
from scoreboard.models import Task, Team, Category, News, SolvedTasks


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


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Team
        fields = ('team_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Team
        fields = ['password', 'team_name', 'is_active', 'is_admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class TeamUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('team_name', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        (None, {'fields': ('team_name', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('team_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('team_name',)
    ordering = ('team_name',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(Team, TeamUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


class FlatPageCustomAdmin(FlatPageAdmin):
    formfield_overrides = {models.TextField: {'widget': SummernoteWidget}}


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustomAdmin)

