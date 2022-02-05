from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from home.models import Users, IsFinished

from quiz.models import Quiz, Question, Answer, Result
from quiz.serializers import QuestionSerializer, QuizSerializer


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_quiz_view(request, pk):
    if request.method == 'GET':
        quiz = Quiz.objects.filter(id=pk)
        questions = Question.objects.filter(quiz=pk)
        quiz = QuizSerializer(quiz, many=True)
        question = QuestionSerializer(questions, many=True)
        data = {
            "quiz": quiz.data,
            "question": question.data,
        }
        return Response(data)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def submit_quiz_view(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        quiz = request.POST.get('quiz')
        score = request.POST.get('score')

        result = Result.objects.create(user=Users.objects.get(id=user), quiz=Quiz.objects.get(id=quiz), score=score)

        IsFinished.objects.create(user=Users.objects.get(id=user), quiz=Quiz.objects.get(id=quiz))

        data = {
            "result": result.score,
            "Test": "Is Finished!"
        }

    return Response(data)