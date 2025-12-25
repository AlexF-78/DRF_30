from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from lms.models import Course, Lesson, Subscription

# Получаем кастомную модель пользователя
User = get_user_model()


class LessonCRUDTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей - используем email вместо username
        self.user1 = User.objects.create_user(
            email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="test2@example.com", password="testpass123"
        )

        # Создаем курс для user1
        self.course = Course.objects.create(
            name="Test Course", description="Test Course Description", owner=self.user1
        )

        # Создаем тестовый урок
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Lesson Description",
            video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            course=self.course,
            owner=self.user1,
        )

        # Создаем клиент API
        self.client = APIClient()

        # URL для уроков
        self.lessons_url = "/lessons/"
        self.lesson_detail_url = f"/lessons/{self.lesson.id}/"

    def test_create_lesson_authenticated(self):
        """Тест создания урока авторизованным пользователем"""
        # утентифицируем пользователя
        self.client.force_authenticate(user=self.user1)

        data = {
            "name": "New Lesson",
            "description": "New Lesson Description",
            "video_link": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "course": self.course.id,
        }

        create_url = "/lessons/create/"  # Правильный URL для создания урока
        response = self.client.post(create_url, data, format="json")

        # Проверяем успешное создание
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().name, "New Lesson")
        self.assertEqual(Lesson.objects.last().owner, self.user1)

    def test_create_lesson_unauthenticated(self):
        """Тест создания урока неавторизованным пользователем"""
        data = {
            "name": "New Lesson",
            "description": "New Lesson Description",
            "video_link": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "course": self.course.id,
        }

        create_url = "/lessons/create/"
        response = self.client.post(create_url, data, format="json")

        # роверяем, что доступ запрещен
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_read_lesson_authenticated(self):
        """Тест чтения урока авторизованным пользователем"""
        # утентифицируем владельца
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.lesson_detail_url)

        # роверяем успешное чтение
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.lesson.name)

    def test_read_lesson_other_user(self):
        """Тест чтения урока другим пользователем (должен получить только свои уроки)"""
        # Создаем урок для другого пользователя
        other_lesson = Lesson.objects.create(
            name="Other Lesson",
            description="Other Lesson Description",
            video_link="https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            course=self.course,
            owner=self.user2,
        )

        # утентифицируем user2
        self.client.force_authenticate(user=self.user2)

        # Проверяем, что user2 может получить СВОЙ урок
        other_lesson_url = f'/lessons/{other_lesson.id}/'
        response_own = self.client.get(other_lesson_url)
        self.assertEqual(response_own.status_code, status.HTTP_200_OK)

        # Пытаемся получить урок user1
        response = self.client.get(self.lesson_detail_url)

        # Должен получить 403, так как урок принадлежит другому пользователю
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "name": "Updated Lesson",
            "description": "Updated Description",
            "video_link": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
            "course": self.course.id,
        }

        update_url = f"/lessons/{self.lesson.id}/update/"
        response = self.client.put(update_url, data, format="json")

        # Проверяем успешное обновление
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Updated Lesson")

    def test_update_lesson_non_owner(self):
        """Тест обновления урока не владельцем"""
        self.client.force_authenticate(user=self.user2)

        data = {
            "name": "Updated Lesson",
            "description": "Updated Description",
            "video_link": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
            "course": self.course.id,
        }

        update_url = f"/lessons/{self.lesson.id}/update/"
        response = self.client.put(update_url, data, format="json")

        # Должен получить 403, так как урок принадлежит другому пользователю
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user1)

        delete_url = f"/lessons/{self.lesson.id}/delete/"
        response = self.client.delete(delete_url)

        # Проверяем успешное удаление
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_non_owner(self):
        """Тест удаления урока не владельцем"""
        self.client.force_authenticate(user=self.user2)

        delete_url = f"/lessons/{self.lesson.id}/delete/"
        response = self.client.delete(delete_url)

        # Должен получить 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_list_lessons_pagination(self):
        """Тест пагинации списка уроков"""
        # Создаем дополнительные уроки для тестирования пагинации
        for i in range(15):
            Lesson.objects.create(
                name=f"Lesson {i}",
                description=f"Description {i}",
                video_link=f"https://www.youtube.com/watch?v=lesson{i:011}",
                course=self.course,
                owner=self.user1,
            )

        self.client.force_authenticate(user=self.user1)

        # Получаем первую страницу
        response = self.client.get(self.lessons_url)

        # Проверяем пагинацию
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        # Проверяем количество элементов на странице (должно быть 10 по умолчанию)
        self.assertEqual(len(response.data["results"]), 10)

        # Проверяем изменение количества элементов через параметр
        response = self.client.get(f"{self.lessons_url}?page_size=5")
        self.assertEqual(len(response.data["results"]), 5)


class SubscriptionTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных для подписок"""
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            email="sub1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="sub2@example.com", password="testpass123"
        )

        # Создаем курсы
        self.course1 = Course.objects.create(
            name="Course 1", description="Description 1", owner=self.user1
        )
        self.course2 = Course.objects.create(
            name="Course 2", description="Description 2", owner=self.user2
        )

        # Создаем клиент API
        self.client = APIClient()

        # URL для подписок
        self.subscriptions_url = "/subscriptions/"

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user1)

        data = {"course": self.course2.id}

        response = self.client.post(self.subscriptions_url, data, format="json")

        # Проверяем успешную подписку
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(Subscription.objects.first().user, self.user1)
        self.assertEqual(Subscription.objects.first().course, self.course2)

    def test_subscribe_to_own_course(self):
        """Тест подписки на свой собственный курс"""
        self.client.force_authenticate(user=self.user1)

        data = {"course": self.course1.id}

        response = self.client.post(self.subscriptions_url, data, format="json")

        # Проверяем, что можно подписаться на свой курс
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_double_subscription(self):
        """Тест двойной подписки на один курс"""
        self.client.force_authenticate(user=self.user1)

        data = {"course": self.course2.id}

        # Первая подписка
        response1 = self.client.post(self.subscriptions_url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # вторая попытка подписки на тот же курс
        response2 = self.client.post(self.subscriptions_url, data, format="json")

        # Должен получить ошибку, так как подписка уже существует
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        # Сначала создаем подписку
        subscription = Subscription.objects.create(user=self.user1, course=self.course2)

        self.client.force_authenticate(user=self.user1)

        # URL для удаления конкретной подписки
        subscription_detail_url = f"{self.subscriptions_url}{subscription.id}/"

        # Удаляем подписку
        response = self.client.delete(subscription_detail_url)

        # Проверяем успешное удаление
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_list_user_subscriptions(self):
        """Тест получения списка подписок пользователя"""
        # Создаем несколько подписок
        Subscription.objects.create(user=self.user1, course=self.course2)
        Subscription.objects.create(user=self.user2, course=self.course1)

        # Проверяем подписки user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.subscriptions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Только одна подписка у user1
        self.assertEqual(response.data[0]["course"], self.course2.id)

    def test_subscription_unauthenticated(self):
        """Тест подписки без аутентификации"""
        data = {"course": self.course1.id}

        response = self.client.post(self.subscriptions_url, data, format="json")

        # Должен получить ошибку авторизации
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaginationTestCase(TestCase):
    def setUp(self):
        """Настройка для тестов пагинации"""
        self.user = User.objects.create_user(
            email="pagination@example.com", password="testpass123"
        )

        self.course = Course.objects.create(
            name="Pagination Course",
            description="Course for pagination tests",
            owner=self.user,
        )

        # Создаем 25 уроков для тестирования пагинации
        for i in range(25):
            Lesson.objects.create(
                name=f"Lesson {i}",
                description=f"Description {i}",
                video_link=f"https://www.youtube.com/watch?v=test{i:011}",
                course=self.course,
                owner=self.user,
            )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.lessons_url = "/lessons/"
        self.courses_url = "/courses/"

    def test_default_pagination(self):
        """Тест пагинации по умолчанию (10 элементов)"""
        response = self.client.get(self.lessons_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 25)
        self.assertIsNotNone(response.data["next"])

    def test_custom_page_size(self):
        """Тест изменения количества элементов на странице"""
        response = self.client.get(f"{self.lessons_url}?page_size=5")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

        # Проверяем, что есть следующая страница
        self.assertIsNotNone(response.data["next"])

    def test_max_page_size(self):
        """Тест максимального количества элементов на странице"""
        response = self.client.get(
            f"{self.lessons_url}?page_size=150"
        )  # Больше максимума

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 25
        )  # Все элементы, но не больше 100
        self.assertIsNone(response.data["next"])  # все на одной странице

    def test_course_pagination(self):
        """Тест пагинации для курсов"""
        # Создаем еще 15 курсов
        for i in range(15):
            Course.objects.create(
                name=f"Course {i}", description=f"Description {i}", owner=self.user
            )

        response = self.client.get(self.courses_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)  # По умолчанию 10
        self.assertIn("next", response.data)
