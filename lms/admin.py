from django.contrib import admin

from .models import Course, Lesson


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'video_link']
    list_filter = ['course']
    search_fields = ['name', 'description', 'video_link']
