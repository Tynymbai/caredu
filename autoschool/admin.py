from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, DriverGroup, StudentGroup, Lecture,
    LectureImage, Test, Question, Answer, TestResult
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type')
    list_filter = ('user_type',)
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('user_type', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('user_type', 'phone_number')}),
    )

@admin.register(DriverGroup)
class DriverGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'instructor', 'created_at')
    list_filter = ('instructor',)
    search_fields = ('name',)

@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('student', 'group')
    list_filter = ('group',)

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'groups')
    search_fields = ('title', 'content')

@admin.register(LectureImage)
class LectureImageAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'caption')
    list_filter = ('lecture',)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'groups')
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'text')
    list_filter = ('test',)
    search_fields = ('text',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('text',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test', 'student', 'score', 'max_score', 'date_taken')
    list_filter = ('test', 'student')
    search_fields = ('test__title', 'student__username')