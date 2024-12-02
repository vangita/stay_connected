from django.db import transaction
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import reload_api_settings
from rest_framework.views import APIView

from forum.models import Question, Answer, Tag, User, Vote
from forum.serializers import QuestionSerializer, DetailQuestionSerializer, AnswerSerializer, VoteSerializer, \
    TagSerializer, UserSerializer


# Create your views here.
class UserProfile(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        tag = self.request.query_params.get('tags', None)
        if search_term:
            queryset = queryset.filter(Q(subject__icontains=search_term) | Q(description__icontains=search_term))
        if tag:
            queryset = queryset.filter(tags__name=tag)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyQuestionListView(generics.ListAPIView):

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Question.objects.filter(user=self.request.user)
        search_term = self.request.query_params.get('search', None)
        tag = self.request.query_params.get('tags', None)
        if search_term:
            queryset = queryset.filter(Q(subject__icontains=search_term) | Q(description__icontains=search_term))
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = DetailQuestionSerializer
    permission_classes = [IsAuthenticated]

class AnswerListView(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs['question_id'])

    def perform_create(self, serializer):
        question = Question.objects.get(id=self.kwargs['question_id'])
        serializer.save(user=self.request.user, question=question)

class VoteCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        answer_id = kwargs.get('answer_id')
        vote_type = request.data.get('vote')
        answer = get_object_or_404(Answer, id=answer_id)
        if answer.user == request.user:
            return Response({"error": "You cannot vote on your own answer."}, status=status.HTTP_400_BAD_REQUEST)

        vote, created = Vote.objects.get_or_create(user=request.user, answer=answer)

        if not created:
            vote.vote = vote_type
            vote.save()
        else:
            vote.vote = vote_type
            vote.save()

        serializer = VoteSerializer(vote)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AcceptAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, answer_id):
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            raise NotFound("Answer not found.")
        if answer.user == request.user:
            raise PermissionDenied("You cannot accept your own answer.")
        if answer.question.user != request.user:
            raise PermissionDenied("You are not allowed to accept an answer for this question.")
        if answer.is_accepted:
            raise PermissionDenied("You have already accepted this answer.")

        previously_accepted_answer = Answer.objects.filter(
            question=answer.question, is_accepted=True).first()


        with transaction.atomic():
            if previously_accepted_answer:
                previously_accepted_answer.is_accepted = False
                previously_accepted_answer.save()
                previous_author_profile = previously_accepted_answer.user
                previous_author_profile.rating -= 3
                previous_author_profile.accepted_answers_count-=1
                previous_author_profile.save()

            answer.is_accepted = True
            answer.save()
            answer_author_profile = answer.user
            answer_author_profile.rating += 5
            answer_author_profile.accepted_answers_count+=1
            answer_author_profile.save()

        return Response({"message": "Answer accepted successfully."})

class RejectAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, answer_id):
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            raise NotFound("Answer not found.")

        if answer.question.user != request.user:
            raise PermissionDenied("You are not allowed to reject this answer.")

        if not answer.is_accepted:
            return Response({"message": "This answer is not currently accepted."}, status=400)

        with transaction.atomic():
            answer.is_accepted = False
            answer.save()
            answer_author_profile = answer.user
            answer_author_profile.rating -= 3
            answer_author_profile.save()

        return Response({"message": "Answer rejected successfully."})

class UserAnsweredQuestionsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        answered_questions = Answer.objects.filter(user=self.request.user).values('question').distinct()
        question_ids = [q['question'] for q in answered_questions]
        return Question.objects.filter(id__in=question_ids).order_by('-created_at')

class TopRatedUsersView(APIView):
    def get(self, request):
        top_users = User.objects.all().order_by('-rating')[:10]
        serializer = UserSerializer(top_users, many=True)
        return Response(serializer.data)



