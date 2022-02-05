from rest_framework import serializers
from quiz.models import Quiz, Question, Answer, Result
from home.serializers import CourseModuleSerializer, CourseModuleSerializer


class QuizSerializer(serializers.ModelSerializer):
    module = CourseModuleSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'module', 'created_at')


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'questionText', 'questionImage')


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answerText', 'answerImage', 'isCorrect')


class ResultSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(many=False, required=True)

    class Meta:
        model = Result
        fields = ('id', 'quiz', 'user', 'score', 'created_at')
