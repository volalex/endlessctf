# encoding: UTF-8
import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver


class Category(models.Model):
    title = models.CharField(max_length=50)
    position = models.IntegerField(name='position', unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('position',)


class News(models.Model):
    title = models.CharField(max_length=50, name="title", verbose_name="Заголовок новости")
    text = models.TextField(name="text", verbose_name="Текст новости")
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = "News"


class Task(models.Model):
    name = models.CharField(max_length=100, blank=False)
    score = models.IntegerField(name='score', blank=False)
    category = models.ForeignKey(Category, blank=False)
    text = models.TextField(name='text', blank=False)
    task_file = models.FileField(verbose_name="Task file", upload_to="task_files", blank=True)
    flag = models.CharField(max_length=100, blank=False)
    is_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def gen_file_link(self):
        if self.task_file:
            return "<a href='%s'>File</a>" % self.task_file.url
        else:
            return ""


@receiver(models.signals.post_delete, sender=Task)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Task` object is deleted.
    """
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except AttributeError:
        pass


@receiver(models.signals.pre_save, sender=Task)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Task` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = Task.objects.get(pk=instance.pk).task_file
    except Task.DoesNotExist:
        return False

    if not old_file:
        return False

    new_file = instance.task_file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class SolvedTasks(models.Model):
    task = models.ForeignKey(Task)
    team = models.ForeignKey(User)
    solved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('task', 'team'),)


