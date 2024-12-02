from django.urls import path

from forum.views import MyQuestionListView, QuestionDetailView, AnswerListView, VoteCreateUpdateView, \
    AcceptAnswerView, RejectAnswerView, TagListView, UserAnsweredQuestionsListView, TopRatedUsersView, \
    QuestionListCreateView, UserProfile

urlpatterns = [
    path('profile/' , UserProfile.as_view(), name='profile'),
    path('questions/', QuestionListCreateView.as_view(), name='questions'),
    path('tags/', TagListView.as_view(), name='tags'),
    path('myquestions/', MyQuestionListView.as_view(), name='myquestions'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:question_id>/answers/', AnswerListView.as_view(), name='answer-list-create'),
    path('answers/<int:answer_id>/vote/', VoteCreateUpdateView.as_view(), name='vote-create'),
    path('answers/<int:answer_id>/accept/', AcceptAnswerView.as_view(), name='accept-answer'),
    path('answers/<int:answer_id>/reject/', RejectAnswerView.as_view(), name='reject-answer'),
    path('answered-questions/', UserAnsweredQuestionsListView.as_view(), name='answered-questions'),
    path('leaderboard/', TopRatedUsersView.as_view(), name='leaderboard'),
]