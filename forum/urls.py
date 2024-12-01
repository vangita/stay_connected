
from django.urls import path

from forum.views import QuestionListView, MyQuestionListView, QuestionDetailView, AnswerListView, VoteCreateView, \
    AcceptAnswerView, RejectAnswerView, TagListView, UserAnsweredQuestionsListView, TopRatedUsersView

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='questions'),
    path('tags/', TagListView.as_view(), name='tags'),
    path('myquestions/', MyQuestionListView.as_view(), name='myquestions'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('<int:question_id>/answers/', AnswerListView.as_view(), name='answer-list-create'),
    path('answers/<int:answer_id>/vote/', VoteCreateView.as_view(), name='vote-create'),
    path('answers/<int:answer_id>/accept/', AcceptAnswerView.as_view(), name='accept-answer'),
    path('answers/<int:answer_id>/reject/', RejectAnswerView.as_view(), name='reject-answer'),
    path('answered-questions/', UserAnsweredQuestionsListView.as_view(), name='answered-questions'),
    path('leaderboard/', TopRatedUsersView.as_view(), name='leaderboard'),
]