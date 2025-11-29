from django.shortcuts import render
from rest_framework import viewsets, generics

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


# CRUD для курсов через ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


# CRUD для уроков через Generic-классы

# Получение списка уроков
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Получение одного урока
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Создание урока
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Обновление урока
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Удаление урока
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
