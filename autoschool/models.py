from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Администратор'),
        ('instructor', 'Инструктор'),
        ('student', 'Курсант'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    class Meta:
        permissions = [
            ("create_admin", "Can create admin users"),
            ("create_instructor", "Can create instructor users"),
            ("create_student", "Can create student users"),
        ]


class DriverGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='instructing_groups',
        limit_choices_to={'user_type': 'instructor'}
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StudentGroup(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'},
        related_name='student_groups'
    )
    group = models.ForeignKey(
        DriverGroup,
        on_delete=models.CASCADE,
        related_name='students'
    )

    class Meta:
        unique_together = ('student', 'group')

    def __str__(self):
        return f"{self.student.username} - {self.group.name}"


class Lecture(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='lectures',
        limit_choices_to={'user_type__in': ['admin', 'instructor']}
    )
    groups = models.ManyToManyField(DriverGroup, related_name='lectures')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class LectureImage(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='lectures/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.lecture.title}"


class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tests',
        limit_choices_to={'user_type__in': ['admin', 'instructor']}
    )
    groups = models.ManyToManyField(DriverGroup, related_name='tests')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)

    def __str__(self):
        return f"Question {self.id} for {self.test.title}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer {self.id} for Question {self.question.id}"


class TestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='test_results',
        limit_choices_to={'user_type': 'student'}
    )
    score = models.IntegerField()
    max_score = models.IntegerField()
    date_taken = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.username} - {self.test.title}: {self.score}/{self.max_score}"