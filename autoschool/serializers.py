from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    CustomUser, DriverGroup, StudentGroup, Lecture,
    LectureImage, Test, Question, Answer, TestResult
)


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'user_type', 'phone_number', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data['user_type'],
            phone_number=validated_data.get('phone_number', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class DriverGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverGroup
        fields = ('id', 'name', 'description', 'instructor', 'created_at')


class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = ('id', 'student', 'group')


class LectureImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureImage
        fields = ('id', 'image', 'caption')


class LectureSerializer(serializers.ModelSerializer):
    images = LectureImageSerializer(many=True, read_only=True)

    class Meta:
        model = Lecture
        fields = ('id', 'title', 'content', 'author', 'groups', 'created_at', 'updated_at', 'images')


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'text', 'is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'image', 'answers')


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'author', 'groups', 'created_at', 'updated_at', 'questions')


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ('id', 'test', 'student', 'score', 'max_score', 'date_taken')