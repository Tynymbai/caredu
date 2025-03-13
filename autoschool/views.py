from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    CustomUser, DriverGroup, StudentGroup, Lecture,
    LectureImage, Test, Question, Answer, TestResult
)
from .serializers import (
    CustomUserSerializer, DriverGroupSerializer, StudentGroupSerializer,
    LectureSerializer, LectureImageSerializer, TestSerializer,
    QuestionSerializer, AnswerSerializer, TestResultSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.user_type == 'admin'


class IsAdminOrInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['admin', 'instructor']


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        user_type = request.data.get('user_type')

        # Проверка разрешений
        if user_type == 'admin':
            if not request.user.has_perm('autoschool.create_admin'):
                return Response({'error': 'У вас нет прав на создание администраторов'},
                                status=status.HTTP_403_FORBIDDEN)
        elif user_type == 'instructor':
            if not (request.user.user_type == 'admin' or request.user.has_perm('autoschool.create_instructor')):
                return Response({'error': 'У вас нет прав на создание инструкторов'},
                                status=status.HTTP_403_FORBIDDEN)
        elif user_type == 'student':
            if not (request.user.user_type in ['admin', 'instructor'] or
                    request.user.has_perm('autoschool.create_student')):
                return Response({'error': 'У вас нет прав на создание курсантов'},
                                status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)


class DriverGroupViewSet(viewsets.ModelViewSet):
    queryset = DriverGroup.objects.all()
    serializer_class = DriverGroupSerializer
    permission_classes = [IsAdminOrInstructor]

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response({'error': 'Нужно указать ID курсанта'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            student = CustomUser.objects.get(id=student_id, user_type='student')
        except CustomUser.DoesNotExist:
            return Response({'error': 'Курсант не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        student_group, created = StudentGroup.objects.get_or_create(
            student=student,
            group=group
        )

        if created:
            return Response({'message': 'Курсант успешно добавлен в группу'},
                            status=status.HTTP_201_CREATED)
        return Response({'message': 'Курсант уже в группе'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def remove_student(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response({'error': 'Нужно указать ID курсанта'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            student_group = StudentGroup.objects.get(
                student_id=student_id,
                group=group
            )
            student_group.delete()
            return Response({'message': 'Курсант успешно удален из группы'},
                            status=status.HTTP_200_OK)
        except StudentGroup.DoesNotExist:
            return Response({'error': 'Курсант не находится в этой группе'},
                            status=status.HTTP_404_NOT_FOUND)


class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsAdminOrInstructor]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            return Lecture.objects.filter(groups__students__student=user).distinct()
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        lecture = self.get_object()
        image = request.data.get('image')
        caption = request.data.get('caption', '')

        if not image:
            return Response({'error': 'Нужно загрузить изображение'},
                            status=status.HTTP_400_BAD_REQUEST)

        lecture_image = LectureImage.objects.create(
            lecture=lecture,
            image=image,
            caption=caption
        )

        serializer = LectureImageSerializer(lecture_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAdminOrInstructor]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            return Test.objects.filter(groups__students__student=user).distinct()
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        test = self.get_object()
        text = request.data.get('text')
        image = request.data.get('image')

        if not text:
            return Response({'error': 'Нужно указать текст вопроса'},
                            status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.create(
            test=test,
            text=text,
            image=image
        )

        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_answer(self, request, pk=None):
        test = self.get_object()
        question_id = request.data.get('question_id')
        text = request.data.get('text')
        is_correct = request.data.get('is_correct', False)

        if not question_id or not text:
            return Response({'error': 'Нужно указать ID вопроса и текст ответа'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.get(id=question_id, test=test)
        except Question.DoesNotExist:
            return Response({'error': 'Вопрос не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        answer = Answer.objects.create(
            question=question,
            text=text,
            is_correct=is_correct
        )

        serializer = AnswerSerializer(answer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def submit_test(self, request, pk=None):
        test = self.get_object()
        student = request.user

        if student.user_type != 'student':
            return Response({'error': 'Только курсанты могут проходить тесты'},
                            status=status.HTTP_403_FORBIDDEN)

        # Проверка ответов
        submitted_answers = request.data.get('answers', {})
        score = 0
        max_score = 0

        for question in test.questions.all():
            max_score += 1
            correct_answer_id = question.answers.filter(is_correct=True).first()

            if correct_answer_id:
                correct_answer_id = correct_answer_id.id
                submitted_answer_id = submitted_answers.get(str(question.id))

                if submitted_answer_id and int(submitted_answer_id) == correct_answer_id:
                    score += 1

        # Сохранение результата
        test_result = TestResult.objects.create(
            test=test,
            student=student,
            score=score,
            max_score=max_score
        )

        serializer = TestResultSerializer(test_result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == 'student':
            return TestResult.objects.filter(student=user)
        elif user.user_type == 'instructor':
            return TestResult.objects.filter(
                test__groups__instructor=user
            ).distinct()

        return super().get_queryset()