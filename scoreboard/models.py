import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver


class TeamUserManager(BaseUserManager):
    def create_user(self, team_name, password=None):

        user = self.model(
            team_name=team_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, team_name, password):
        user = self.create_user(
            password=password,
            team_name=team_name
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Player(AbstractBaseUser):
    #required fields
    email = models.EmailField(unique=True,name="Адрес электронной почты")
    username = models.CharField(max_length=100,unique=True,name="Логин")
    USERNAME_FIELD = 'username'

    SSU = "SSU"
    SSAU = "SSAU"
    SSTU = "SSTU"
    PSUTI = "PSUTI"
    PGSGA = "PGSGA"
    IMI = "IMI"
    NAY = "NAY"
    SGASU = "SGASU"
    SGUPS = "SGUPS"
    SSEU = "SSEU"

    UNI_CHOICES = (
        (NAY,"Академия Наяновой"),
        (IMI,"МИР"),
        (PSUTI,"ПГУТИ"),
        (PGSGA,"ПГСГА"),
        (SSU,"СамГУ"),
        (SSAU,"СГАУ"),
        (SSTU,"СамГТУ"),
        (SGASU,"СГАСУ"),
        (SGUPS,"СамГУПС"),
        (SSEU,"СГЭУ")
    )

    university = models.CharField()



    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = TeamUserManager()

    def get_full_name(self):
        # The user is identified by their team name
        return self.username

    def get_short_name(self):
        # The user is identified by their team name
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


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
    team = models.ForeignKey(Team)
    solved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('task', 'team'),)


